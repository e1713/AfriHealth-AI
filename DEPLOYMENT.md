# AfriHealth AI deployment and operations

This prototype has two deployment surfaces:

1. a static browser frontend (`index.html`, JavaScript, and assets); and
2. a server-side API bridge (`main.py`) that keeps the Intron credential private
   and proxies speech requests.

The frontend may be hosted on Cloudflare Pages. The FastAPI service must run on
an HTTPS-capable host that supports WebSockets. Do not deploy the API key in
the static frontend.

## Recommended architecture

```text
Browser
  |
  | HTTPS / WSS
  v
Cloudflare Pages       Separate FastAPI service
static frontend  --->  /health
                       /api/intron/stt/upload-sync
                       /api/intron/tts/generate
                       /api/intron/tts/enqueue
                       /api/intron/voicebot/workflows
                      /api/v1/fhir/export
                      /api/v1/ehr/commit
                       /ws/stream
                              |
                              v
                       Intron Voice API
```

The browser records audio locally, presents playback for review, and uploads
only after the user explicitly selects the upload action. The API service
receives the audio and uses `INTRON_API_KEY` server-side.

## Required environment variables

Configure these only on the API host:

```text
APP_ENV=production
INTRON_API_KEY="<YOUR_EXISTING_INTRON_API_KEY>"
SAHARA_API_KEY="<YOUR_GENERATED_API_KEY_SECRET>"
DATABASE_URL=${{Postgres.DATABASE_URL}}
ALLOWED_ORIGINS=https://your-project.pages.dev
INTRON_TTS_VOICE_LANGUAGE=am
INTRON_TTS_VOICE_ACCENT=amharic
INTRON_TTS_VOICE_GENDER=female
```

Use a comma-separated list for multiple exact origins. Do not use `*` for
production CORS when credentials or protected clinical workflows are involved.
In Railway, add a PostgreSQL service and link its `DATABASE_URL` reference to
the FastAPI service. The backend converts Railway's `postgresql://` URL to the
asyncpg SQLAlchemy driver automatically. Keep the Cloudflare Pages frontend and
its API-origin configuration unchanged. Set the Railway start command to
`uvicorn main:app --host 0.0.0.0 --port $PORT` in the service settings.
Do not commit `.env` files, API keys, patient recordings, full transcripts, or
provider response IDs.

`/api/v1/fhir/export` always builds a server-side FHIR bundle. `/api/v1/ehr/commit`
returns `503` until `EHR_FHIR_ENDPOINT` is configured, and then submits the
bundle with the optional `EHR_API_KEY`.

Set `SAHARA_API_KEY` on the FastAPI host and provide the same secret to
authorized browser users out of band. The page prompts for it when a protected
API is first used, sends it as a Bearer token for REST calls, and keeps it only
in memory. Native browser WebSockets cannot set an `Authorization` header, so
WebSocket routes validate an encoded `sahara-auth.*` subprotocol instead.
Without a valid key, `/api/*` returns 401. A shared API key does not establish
an individual clinician identity; EHR commit also requires explicit sign-off.

The gateway exposes `POST /api/intron/stt/upload-sync` using the documented
`audio_file_blob` multipart field; `POST /api/intron/tts/generate` and
`POST /api/intron/tts/enqueue` accept JSON text up to 4,096 characters;
`/ws/intron/tts/stream` proxies TTS chunks of 10 to 100 characters with the
60-second idle and 300-second session limits; and
`POST /api/intron/voicebot/workflows` creates a workflow. The supplied provider
documentation does not specify a TTS job-status route, so the gateway does not
invent one.

## Run the API

Install the Python dependencies and start the service on an externally
reachable interface:

```bash
python -m pip install -r requirements.txt
export INTRON_API_KEY="your-key"
export SAHARA_API_KEY="your-generated-api-key"
export ALLOWED_ORIGINS="https://your-project.pages.dev"
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Terminate TLS at the hosting platform or reverse proxy. The public API URL
must be HTTPS, and WebSocket clients must connect through `wss://`.

## Deploy the frontend to Cloudflare Pages

The repository is a static site. Configure Cloudflare Pages to stage only the
browser assets and benchmark methodology document:

- **Build command:** `mkdir -p _site && cp index.html pcm-processor.js offline-sync-worker.js sw.js BENCHMARK_RESULTS.md _site/`
- **Build output directory:** `_site`
- **Root directory:** repository root

This allowlist excludes notebook outputs, benchmark audio, Python source,
configuration, and private evaluation files from the static deployment.

Set `SAHARA_API_ORIGIN` as a public Pages build variable to the HTTPS FastAPI
origin. For Cloudflare Pages
Git integration, use this build command and output directory:

```sh
if [[ ! "$SAHARA_API_ORIGIN" =~ ^https://[A-Za-z0-9.-]+(:[0-9]+)?$ ]]; then exit 1; fi
mkdir -p _site
cp index.html pcm-processor.js offline-sync-worker.js sw.js BENCHMARK_RESULTS.md _site/
printf 'window.SAHARA_API_ORIGIN = "%s";\n' "$SAHARA_API_ORIGIN" > _site/api-origin.js
```

Set the build output directory to `_site` (not `.`). Never embed
`SAHARA_API_KEY` in the static frontend; users enter it at runtime.

For a production deployment, this value should be injected during the
deployment process rather than edited manually for each environment.

## Post-deployment checks

1. Open `https://your-project.pages.dev/` and confirm the page loads.
2. Request `https://api.example.org/health` and confirm the service is online.
3. Confirm unauthenticated `/api/*` requests return 401 and authenticated
   requests pass API-key validation.
4. Test one consented, de-identified recording:
   local playback -> explicit upload -> transcript -> clinician review.
5. Confirm browser developer tools show no API key in source, storage, or
   request bodies.
6. Confirm REST requests use HTTPS and WebSocket requests use WSS.
7. Confirm a request from an unapproved origin is rejected by CORS.
8. Review hosting logs and retention settings before handling real patient
   information.
9. Confirm unauthenticated HTTP and WebSocket requests are rejected, and
   forged identity headers do not authenticate.

## Operational boundaries

This prototype is a clinician-reviewed documentation and decision-support aid.
Generated transcripts, entities, triage labels, coding suggestions, SOAP notes,
and medication suggestions require qualified human review. Clinical validation
materials are private evaluation and governance artifacts, not a public
approval claim. Use only consented, de-identified data for demonstrations and
evaluation.

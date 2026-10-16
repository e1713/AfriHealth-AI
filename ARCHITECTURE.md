# AfriHealth AI Architecture

## 1. System purpose

AfriHealth AI is a browser-based clinical voice documentation and
decision-support prototype for community health workers and clinicians. The
current production language scope is Amharic-English code-switching.
Tigrinya-English and Oromo-English are future roadmap languages only; neither
is current production scope.
The system produces draft transcripts and clinician-review artifacts; it is
not an autonomous diagnostic or prescribing service.

## 2. Production provider, model, and deployment

Production speech and voice functionality uses the Intron API, with Intron
Sahara v2.5 as the primary ASR model and Intron STT/SST capabilities used where
required. Other AI providers are not application dependencies.

The official production deployment architecture is a Cloudflare Pages static
frontend and a Railway-hosted FastAPI backend. This documents the target
architecture and does not verify which deployment is currently live.

Current module boundaries remain distinct: Frontline Triage uses Intron speech
services with local triage logic; Voice EHR Intake uses Intron transcription
and currently validates structured SOAP JSON or falls back to manual review,
not model-generated SOAP prose; POST-CARE includes a local workflow simulation
and a separate Intron-backed follow-up API path. A local simulation is not a
live patient-contact workflow.

## 3. Runtime components

```text
Browser (index.html)
  |-- microphone PCM capture and local WAV review
  |-- WebSocket client for live STT
  |-- REST client for saved-recording STT upload
  |-- triage, EHR intake, and follow-up views
  |
  +--> FastAPI service (main.py :8000)
          |-- server-side Intron API-key boundary
          |-- streaming STT WebSocket proxy
          |-- follow-up TTS generation bridge
          |-- synchronous STT upload bridge
          |-- server-side FHIR export and optional EHR commit
          |-- synchronous TTS generation and status bridges
          |-- clinical artifact and medication safety gate
          |-- async SQLAlchemy persistence adapter (PostgreSQL in production; SQLite locally)
          |
          +--> Intron API (Sahara v2.5 primary ASR; STT/SST where required)
          +--> Configured FHIR/EHR endpoint (optional)

Optional local static server (server.js or npm start :3000)
  |-- serves the browser files
  +-- optional legacy Intron proxy route
```

The browser must not receive or store the Intron API key. Under the official
target architecture, the frontend is hosted on Cloudflare Pages and the
FastAPI backend on Railway. Production deployments should expose only the
FastAPI service through an allowlisted origin and configure `ALLOWED_ORIGINS`.
The active deployment state must be verified separately.

## 4. Main request flows

### Live transcription

1. The browser requests microphone access and captures audio.
2. Audio bytes and control messages are sent to `/ws/stream`.
3. FastAPI adds the server-side Authorization header and connects to Intron.
4. Partial and final transcript messages are returned to the browser.
5. Final text populates the transcript, entity, triage, and safety-review
   panels.

### Saved recording review and upload

1. The browser captures PCM and encodes a local WAV blob.
2. The user reviews playback and may download the local copy.
3. Upload occurs only after the explicit upload action.
4. FastAPI forwards the multipart file to Intron's synchronous STT endpoint.
5. The browser displays the returned transcript and clinician-review triage
   output.

Synchronous uploads are limited by the provider's documented 120-second
maximum. The controlled clinical uploader uses one reviewed recording per
case and keeps raw audio and provider response data outside Git.

### Clinical artifact generation

`/api/v1/process-clinical` (also available as `/api/v1/clinical/process-text`)
accepts transcript text, applies limited email
and phone redaction, and attempts to validate structured SOAP JSON. Ordinary
prose falls back to a summary marked for manual review; this endpoint does not
invoke a generation model and is not currently called by `index.html`. The UI's
editable clinical workflow and this API endpoint are separate paths. Do not
describe the current endpoint as an agentic SOAP/ICD-10 generator. Any medication
safety gate must be verified in the specific workflow before describing it as
enforced end to end.

### Clinician review and record export gates

The browser displays a persistent clinical safety disclaimer and marks
transcripts and derived artifacts as pending verification. The EHR workflow
requires a separate review-confirmation checkbox and sign-off action. Approval
does not automatically commit data; FHIR export, clinical summary export, and
EHR commit controls remain unavailable until the reviewer signs off. Editing
the current SOAP draft invalidates its approval.

Both `/api/v1/fhir/export` and `/api/v1/ehr/commit` require the
`clinician_signed_off` request field. This is a caller-supplied assertion, not
authenticated clinician identity or an auditable digital signature. The
prototype still requires deployment-level authentication, authorization, and
audit controls before identifiable patient data can be used.

The UI does not synthesize ASR confidence values. When confidence is
unavailable, the clinical SOAP response carries `null` rather than a synthetic
zero. Until verified backend inference metadata provides a confidence tier, the
UI shows a pending-verification placeholder. A score supplied inside
structured SOAP input is not independently verified and must not be treated as
inference metadata. Frontend heuristics must not be presented as model
confidence.

## 5. Stream session metadata

Each live stream receives a session ID and clinic ID, which are stored in
PostgreSQL using Railway's `DATABASE_URL`; local development defaults to an
async SQLite database. The current WebSocket path returns partial and committed
transcripts to the browser but does not call the transcript persistence method.
Raw audio is processed in memory and is not stored by this layer. Session
metadata has no expiry or deletion policy. The schema is created automatically
at service startup.

## 6. Security and privacy boundaries

- Keep `INTRON_API_KEY` in a server environment variable.
- Never place credentials in `index.html`, commits, screenshots, or demo
  recordings.
- Raw audio is not stored by the stream persistence tables. The WebSocket path
  currently persists session metadata only; it does not write transcript text
  to `clinic_sessions` or `transcript_events`. No expiry or deletion policy is
  implemented for session metadata.
- The clinical text endpoint redacts common email addresses and Ethiopian
  phone numbers only. This limited redaction is not applied to live-stream
  persistence and is not comprehensive de-identification.
- Do not use identifiable patient data until retention, deletion, and access
  controls have been approved and implemented.
- Use de-identified or simulated cases for public demonstrations.
- Configure exact production CORS origins rather than broad wildcards.
- Treat generated transcripts, entities, codes, triage labels, and medication
  candidates as clinician-review drafts.

The persistence `session_id` is a stream-session UUID. It is not linked to the
separate, caller-supplied FHIR `encounter_id`. The repository has no patient or
clinician tables and no built-in clinician accounts or role-based access
control. `REQUIRE_PROXY_AUTH` enables only a trusted identity-header check.

## 7. Known limitations

- The current frontend uses a lightweight browser capture path and requires a
  compatible microphone/browser for live recording.
- The current production scope is Amharic-English code-switching. Oromo-English
  and Tigrinya-English are future roadmap languages only and are not
  production-supported.
- No independent clinical safety or efficacy claim has been established.
- No demo video is included in this repository. The written
  [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) is provided for a future recording or
  live judging session.

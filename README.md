# AfriHealth AI — Unified Voice Suite

**Sahara Healthcare Suite** is a clinician-support prototype for voice-enabled
clinical documentation workflows. It is designed for Amharic-English
code-switched conversations and keeps transcript review and clinician approval
in the workflow.

> This is a prototype, not an autonomous clinical system. Generated
> transcripts, notes, codes, and triage suggestions require clinician
> verification. The current benchmark outputs are mock-only and are not
> evidence of model accuracy or clinical performance.

**Project lead:** Ermias Amare Gebremedhin

[Live prototype](https://sahara-healthcare-suite.pages.dev/) ·
[Official documentation](https://afri-health-ai.mintlify.site/) ·
[Walkthrough](https://youtu.be/47ldOyJxyPE?si=B4X5WVlztZzwGktZ) ·
[Challenge submission](SUBMISSION_SUMMARY.md) ·
[MIT License](LICENSE)

## Product overview

AfriHealth AI brings voice capture, transcription, reviewable clinical
documentation, and benchmark tooling into one prototype. It aims to reduce
documentation friction while keeping clinical decisions and approval with
qualified care professionals.

### Core capabilities

- Browser-based audio recording, upload, and playback.
- Backend speech-to-text gateway with server-side provider credentials.
- Draft clinical intake, SOAP, triage, and clinical-reference workflows.
- Human-review indicators and approval gates before FHIR export or EHR commit.
- Optional provider integrations configured through backend environment
  variables.
- A **VoiceBot Follow-Up Workflow Demo** for demonstration; it does not call
  or contact patients.
- A reproducible ASR benchmark pipeline, evaluation reports, and dataset
  governance documentation.

### Language scope

- **Active workflow focus:** Amharic-English code-switching.
- **English:** Clinical English terms appear in the code-switched workflow;
  this is not a separate English-accent certification.
- **Afaan Oromoo-English and Tigrinya-English:** Future roadmap languages;
  neither is enabled as an active recognition scope in the current UI.
- Additional language or accent support requires provider capability and
  evaluation against appropriately consented, annotated audio.

## Architecture

```text
Clinician / patient conversation
              ↓
      Static browser app
     (HTML, CSS, JavaScript)
              ↓ HTTPS / WebSocket
       FastAPI API gateway
              ↓
 Configured ASR / clinical services
              ↓
 Draft transcript and structured outputs
              ↓
      Clinician review
              ↓
     Approved export / EHR
```

The gateway keeps provider keys on the server. The checked-in frontend is a
static browser application, not a Next.js app; there is no Streamlit interface
in this repository. The benchmark and data-preparation utilities are Python
scripts. The frontend can be hosted on a static platform such as Cloudflare
Pages, while the API requires a separate secure backend service.

**Current stack**

| Layer | Technology |
| --- | --- |
| Web interface | Static HTML, CSS, and JavaScript |
| API | Python, FastAPI, Uvicorn |
| State persistence | PostgreSQL in hosted deployments; SQLite for local development |
| Benchmark tooling | Python evaluation, validation, and reporting scripts |
| Static hosting | Cloudflare Pages-compatible |

## Get started

### Requirements

- Python 3.10 or later
- Node.js/npm for the included static-server command (or use another static
  file server)
- An ASR provider key only if you intend to make live transcription requests

### 1. Install the API dependencies

```bash
git clone https://github.com/sahara-healthcare-suite/sahara-healthcare-suite.git
cd sahara-healthcare-suite

python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate the environment with:

```powershell
.venv\Scripts\Activate.ps1
```

### 2. Configure local environment

Copy `.env.example` to `.env` and set only the provider and deployment values
you need. Keep all API keys on the backend; never place secrets in frontend
files or commit `.env`.

```bash
cp .env.example .env
```

For local use, configure allowed origins for the frontend address you use
(the included `npm start` script serves on port 3000 by default).

### 3. Start the API and frontend

In the first terminal:

```bash
source .venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```bash
npm start
```

Open `http://localhost:3000`. Live transcription requires a valid provider
configuration. Without one, use the interface and benchmark only for local
development or demonstration.

## Benchmarking

The canonical benchmark source is the verified Google Sheet export at
[benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx](benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx)
and its normalized CSV companion. The 100 rows have unique CS-01 through CS-100
IDs and `review_status=verified`; the manifest uses the source
`normalized_transcript` values. It differs from the older DOCX on 16 cases and
the PDF on 19; see [GROUND_TRUTH_AUDIT_REPORT.md](GROUND_TRUTH_AUDIT_REPORT.md).
Matching audio files exist for all source filenames, and checksums are recorded.
Speaker labels are pseudonymized; assignments remain pending separate review.
Consent, de-identification, and hosted-inference approval remain `unknown`.
The source provides clinical domains and an Amharic-English language-mix label;
the finer code-switch categories remain provisional.

The evaluator includes six adapter names: Sahara, Gemini, Whisper, Wav2Vec2,
SpeechBrain, and NeMo. Mock mode tests data flow only; local baseline adapters
are placeholders and do not load model weights.

To validate the manifest and dictionary:

```bash
python validate_metadata.py
```

The validator requires evidence references for affirmative consent,
de-identification, hosted-inference approval, audio verification, and reviewed
annotations, plus a documented SHA-256 for verified audio. The spreadsheet's
verified review status supports reference promotion but does not establish
consent or provider approval. The hosted inference
runner checks that the manifest checksum matches the exact cleaned WAV; the live
sample endpoint likewise requires evidence-backed approvals and the uploaded
audio checksum. Until those records are provided, hosted inference is blocked.

To exercise the pipeline without live provider calls:

```bash
python inference_engine.py --env mock
python evaluator.py \
  --manifest benchmark/metadata/BENCHMARK_MANIFEST.csv \
  --dictionary dictionaries/medical_terms.json \
  --outputs results/model_comparisons.csv \
  --results results/final_evaluation_metrics.csv
python generate_results_doc.py \
  --metrics results/final_evaluation_metrics.csv \
  --benchmark-report BENCHMARK_RESULTS.md \
  --recommendation-report MODEL_RECOMMENDATION.md
```

Mock transcripts and simulated latency are pipeline fixtures, not ASR
measurements. WER, clinical-term recall, critical-term miss rate, and CEAS
remain unavailable for mock-only output. CEAS is a proposed project metric and
cannot be calculated until speaker assignments and code-switch annotations are
independently reviewed and a paired live evaluation is available.

See [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) for the generated evaluation
snapshot, [MODEL_RECOMMENDATION.md](MODEL_RECOMMENDATION.md) for the
evidence-based model-selection status, and [benchmark/](benchmark/) for the
protocol, metric definitions, and limitations.

## Safety and data handling

- Treat generated content as draft clinical reference material, not a
  diagnosis, treatment order, or prescription.
- Verify transcripts and structured outputs against the source audio and
  patient context before clinical use.
- Demo fixtures, projected workflow impacts, and the simulated VoiceBot are
  not clinical evidence or live patient-facing services.
- The prototype does not provide built-in clinician accounts or complete
  role-based access control, audit, retention, and deletion safeguards. Do not
  use identifiable patient data until these controls and the deployment have
  been independently implemented and verified.
- Review [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) and
  [CLINICAL_RECORDING_PROTOCOL.md](CLINICAL_RECORDING_PROTOCOL.md) before any
  data collection or hosted inference.

## Project documentation

- [Architecture](ARCHITECTURE.md)
- [Deployment guide](DEPLOYMENT.md)
- [Responsible AI](RESPONSIBLE_AI.md)
- [Challenge alignment](CHALLENGE_ALIGNMENT.md)
- [Benchmark protocol and limitations](benchmark/README.md)
- [Submission summary](SUBMISSION_SUMMARY.md)
- [Presentation script](benchmark/reporting/PRESENTATION_SLIDES.md)

## Tests

Run the repository unit tests from the project root:

```bash
python -m unittest discover tests -v
```

## Attribution and license

**Project lead:** Ermias Amare Gebremedhin

**License:** MIT — see [LICENSE](LICENSE).

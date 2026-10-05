# Afrihealth AI

> Sahara Healthcare Suite

A clinician-reviewed Amharic-English code-switched clinical documentation platform designed to reduce clinician workload, accelerate patient intake, and improve documentation quality in African healthcare environments.

[![Live Application](https://img.shields.io/badge/Live-Application-blue?style=for-the-badge)](https://sahara-healthcare-suite.pages.dev/)
[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-black?style=for-the-badge)](https://github.com/sahara-healthcare-suite/sahara-healthcare-suite)
[![YouTube Walkthrough](https://img.shields.io/badge/Video-Walkthrough-red?style=for-the-badge)](https://youtu.be/47ldOyJxyPE?si=B4X5WVlztZzwGktZ)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**Lead Author:** Ermias Amare (`ermiasamare1713@gmail.com`)

**Live Production Application:** https://sahara-healthcare-suite.pages.dev/

**GitHub Repository:** https://github.com/sahara-healthcare-suite/sahara-healthcare-suite

**Video Walkthrough:** https://youtu.be/47ldOyJxyPE?si=B4X5WVlztZzwGktZ

**Deployment Infrastructure:** Cloudflare Pages (Serverless / Global Edge Network)

---

## Overview

Sahara Healthcare Suite v1.0 is a clinician-facing documentation platform focused on Amharic-English code-switched clinical conversations. Afaan Oromoo-English is a Phase 2 roadmap item; Tigrinya-English is Phase 3. It captures audio, transcribes clinical speech, and supports review workflows for SOAP drafts, triage, coding, benchmarking, and FHIR-compatible exports.

The system is built around a static frontend and a secure FastAPI gateway that keeps sensitive credentials, such as the Intron API key, out of the browser while enabling real-time clinical processing at edge scale.

---

## Why it matters

- Reduces documentation burden for clinicians working in high-volume care settings
- Supports Amharic-English code-switched conversations in the current release
- Improves time-to-note generation for patient intake, follow-up, and triage workflows
- Creates a safer, review-first documentation pipeline for clinical AI assistance
- Enables interoperability with FHIR-ready export structures for downstream health systems

---

## Key capabilities

- Real-time audio capture and playback in the browser
- Amharic-English code-switched speech support for clinical settings
- Secure backend transcription proxy with server-side API key handling
- Human-in-the-loop clinical review workflow for transcripts and structured outputs
- Editable SOAP clinical-reference draft panel and structured SOAP validation
- FHIR-compatible export and EHR commit actions gated on explicit clinician review
- Optional EHR submission when configured by deployment
- Intron-focused live audio benchmark with transcript-only or reference-scored WER/CER
- PostgreSQL stream persistence in production with a local SQLite development fallback
- Safety-oriented design with physician verification requirements
- One-click **Clinical Impact & Efficiency Dashboard** with clearly labeled, illustrative pilot projections (not measured outcomes)
- A **VoiceBot Follow-Up Workflow Demo** that is explicitly a local simulation, separate from any live call or patient-contact capability
- A **Sahara CodeSwitch Africa Challenge Alignment** navigation view and [CHALLENGE_ALIGNMENT.md](CHALLENGE_ALIGNMENT.md) evidence map

## Judge-ready views

The primary navigation opens the impact dashboard, challenge alignment map,
clinical modules, simulated follow-up workflow, and benchmark matrix directly.
The impact dashboard includes the requested planning values—approximately
5 minutes per patient, 200 minutes per clinician-day, 70% documentation burden
reduction, and 15% daily patient-support capacity—as **illustrative pilot
projections only**. The 200-minute projection assumes 40 consultations at five
minutes each. None of these values are measured outcomes or validated clinical
study findings.

The **VoiceBot Follow-Up Workflow Demo** advances through discharge/intake,
simulated reminder scheduling, simulated adherence check, and a fictional
follow-up/adverse-reaction log. It does not make or schedule calls, contact
patients, or send staff alerts. The existing post-care API and interactive
voice session are separate application features; the state-machine demo itself
is not wired to a verified live calling workflow.

The **Sahara CodeSwitch Africa Challenge Alignment** view maps voice workflows,
the four-model comparison, health-category focus, Responsible AI, and demo
evidence to specific repository files. See [CHALLENGE_ALIGNMENT.md](CHALLENGE_ALIGNMENT.md)
for the full mapping and limits.

Trust indicators shown in the dashboard refer only to prototype controls; they
are not production-readiness certification. The application is not ready for
identifiable patient data until authentication/RBAC, auditability, retention
and deletion controls, and production configuration are implemented and
verified.

---

## Evidence and benchmark status

The repository separates fixture demonstrations from measured validation:

- The Module 4 fixture matrix uses embedded hypotheses and is not an audio benchmark or production model ranking.
- [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) reports a separate four-model transcript comparison scored on the unchanged 15-case Amharic-English manifest. It includes normalized WER, alias-aware annotated target-term recall, and M-WER for Intron, Whisper Tiny, English-only Wav2Vec2, and Gemini.
- The live benchmark accepts one reviewed Amharic-English sample and reports Intron Sahara v2.5 latency, transcript, WER, and CER.
- WER/CER require a verified reference transcript. A provisional Intron-reference mode is available for model-to-model comparison, but it is not independent gold-standard accuracy.
- The clinical validation report covers 15 reviewed simulated cases and reports a 56.38% mean WER, 44.33% target-term recall, and six cases with critical-term misses. These results require clinician review and do not support autonomous care.

The four-model report scores saved transcripts, not fresh inference during report generation. Its custom target-term recall is not a demographic fairness metric; no hallucination-rate or streaming segment-loss result is reported. OpenAI's optional hosted baseline has no complete outputs in the recorded run and is excluded.

---

## Architecture

This repository is structured as a hybrid web application:

- Frontend: static browser interface served from the repository root
- Backend: FastAPI service in `main.py`
- Deployment model: frontend on Cloudflare Pages, API on a secure HTTPS host such as Railway or another server runtime

Typical flow:

1. Clinician records or uploads patient audio in the browser.
2. The frontend sends the request to the API gateway.
3. The backend authenticates to the Intron API using `INTRON_API_KEY`.
4. The system returns transcript, clinical analysis, and optional structured outputs.
5. Module 2 exposes an editable SOAP draft and requires clinician sign-off before FHIR export or EHR commit.
6. Module 4 can send a reviewed sample to `/api/v1/benchmark/live` for Intron-focused scoring.

---

## Tech stack

- Python 3.x
- FastAPI
- JavaScript / static frontend assets
- Intron AI transcription service
- FHIR-compatible export workflow
- Cloudflare Pages-friendly static deployment

---

## Repository structure

```text
.
├── main.py                  # FastAPI application and API routes
├── index.html               # Browser frontend entry point
├── server.js                # Optional local static server behavior
├── package.json             # Frontend run script
├── requirements.txt         # Python dependencies
├── .env.example             # Example environment configuration
├── config.py                # Configuration helpers
├── benchmark_suite.py       # Fixture benchmark and model comparison utilities
├── edge_persistence.py      # Async PostgreSQL/SQLite stream metadata adapter
├── clinical_validation_*    # Validation and reporting scripts
├── tests/                   # Safety and validation tests
├── README.md                # Project documentation
├── DEPLOYMENT.md            # Deployment guidance
├── ARCHITECTURE.md          # Technical design notes
├── LICENSE                  # MIT license
└── ...
```

---

## Prerequisites

Before running locally, ensure the following are installed:

- Python 3.10+
- pip
- Node.js and npm
- An Intron API key

---

## Local development setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd sahara-healthcare-suite
```

### 2. Configure environment variables

Copy the sample environment file and add your API credentials:

```bash
cp .env.example .env
```

Example variables in `.env.example` include:

```env
INTRON_API_KEY=
INTRON_TTS_VOICE_LANGUAGE=am
INTRON_TTS_VOICE_ACCENT=amharic
INTRON_TTS_VOICE_GENDER=female
ALLOWED_ORIGINS=https://your-project.pages.dev
REQUIRE_PROXY_AUTH=false
EHR_FHIR_ENDPOINT=
EHR_API_KEY=
DATABASE_URL=sqlite+aiosqlite:///./edge_sync.sqlite3
OPENAI_API_KEY=
OPENAI_TRANSCRIBE_MODEL=gpt-4o-mini-transcribe
GEMINI_API_KEY=
GEMINI_TRANSCRIBE_MODEL=gemini-2.0-flash
```

The FastAPI app loads `.env` automatically for local development. OpenAI and
Gemini are optional comparison providers. Keep all provider keys on the
backend; never add them to `index.html`.

### 3. Install Python dependencies

```bash
python -m pip install -r requirements.txt
```

This installs only the lightweight API runtime. For the optional local AfriSwitch
audio import and ASR benchmark tools, install `requirements-benchmark.txt` as
well; that set includes large machine-learning dependencies.

### 4. Start the FastAPI backend

```bash
export INTRON_API_KEY="your-key"
export ALLOWED_ORIGINS="http://localhost:3000"
python -m uvicorn main:app --host 127.0.0.1 --port 8000
```

### 5. Serve the frontend locally

In a second terminal:

```bash
npm install
npm start
```

This uses the static server configuration defined in `package.json` and serves the app from the repository root.

---

## Important security and privacy notes

- Never expose `INTRON_API_KEY` in the browser or source code.
- Live stream session metadata is persisted in PostgreSQL/SQLite, but the current WebSocket path does not persist transcript text; audio is processed in memory and is not stored by this persistence layer. Session metadata has no expiry or deletion policy. Do not use identifiable patient data until approved retention and access controls are in place.
- The clinical text endpoint redacts common email addresses and Ethiopian-format phone numbers, but this is not comprehensive de-identification and is not applied to live-stream persistence.
- The backend has an optional trusted-proxy identity-header check, not built-in clinician accounts or role-based access control.
- Use HTTPS and WSS in production.
- Configure CORS restrictions carefully for deployment.
- Do not commit `.env` files or sensitive deployment values.
- Treat generated notes as assistive material that requires clinician verification before clinical action.

---

## Clinical safety principles

This project is designed as a clinician-support workflow, not an autonomous clinical authority. Generated transcripts, SOAP notes, codes, triage labels, and risk indicators are clinical reference suggestions. They require clinician verification against source audio and patient context and must not be treated as a diagnosis, treatment order, or prescription.

## Clinical safety features

- **Persistent UI disclaimer:** Clinical transcript, triage, extracted-entity, SOAP, ICD-10, post-care, benchmark-transcript, and FHIR surfaces display: “Clinical Workflow Assistant — Pending Clinician Approval. Generated transcripts, SOAP notes, and codes are clinical reference suggestions for clinician verification only. Not an autonomous diagnosis or prescription.”
- **Reusable UI elements:** `ClinicalSafetyBanner`, `HumanReviewStatusBadge`, and `ConfidenceTierCard` are implemented as native custom elements in the static frontend and reused across the clinical result surfaces.
- **Human review status:** Clinical results are labeled **Pending Verification** until review is completed. The EHR workflow requires the reviewer to confirm that the source transcript and draft were reviewed, then explicitly select **Verify & Sign Off**. Changes to the draft revoke the current approval and require review again.
- **FHIR/EHR protection:** FHIR export, clinical-summary export, and EHR commit controls are disabled until approval; the page identifies the gate as **Review Required before FHIR Commit**. Approval and committing are separate actions. The `/api/v1/fhir/export` and `/api/v1/ehr/commit` endpoints also reject requests without the `clinician_signed_off` assertion.
- **No automatic commit on approval:** Signing off a draft does not submit it to an EHR. The reviewer must separately invoke the commit action.
- **Confidence transparency:** The UI does not calculate or fabricate ASR confidence. No verified inference-confidence metadata is currently wired into these views, so confidence panels show **Estimated Confidence: Pending Verification** and state that no backend confidence metadata is available. The API returns `null` when confidence is unavailable rather than a synthetic zero. A score supplied inside structured SOAP input is not independently verified and is not used to assign a tier. No high/medium/low tier is assigned without an explicit backend-supplied tier.
- **Accessible tier colors:** If supported backend metadata is integrated in the future, high, medium, low, and pending tiers are styled green, amber, red, and indigo respectively, with text labels so color is not the only indicator.

These UI and endpoint gates do not establish reviewer identity or provide an auditable digital signature: `clinician_signed_off` is a caller-supplied assertion, and the project has no built-in clinician accounts or role-based access control. Do not use identifiable patient data or treat this prototype as a production clinical system until authentication, authorization, audit, retention, and deletion controls are implemented and verified.

---

## Deployment guidance

The project is intended for a split deployment model:

- Static frontend hosted on Cloudflare Pages or similar static hosting
- API service hosted on a secure backend runtime with TLS enabled

For full deployment guidance, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Validation and benchmarking

Run the focused regression suite with:

```bash
python -m unittest tests.test_safety tests.test_edge_persistence -v
python -m py_compile main.py edge_persistence.py
```

The live benchmark supports two reference modes:

1. `verified`: paste an approved reference transcript to calculate independent WER/CER.
2. `intron`: use the Intron transcript as a provisional reference for comparing another configured provider.

Both modes are evaluation aids, not standalone clinical validation. Use
simulated or de-identified recordings and require clinician review.

---

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Project contributors

- Ermias Amare — Project Management & Architecture Lead
- Fasil Bazazew — Software Engineer
- Melaku Bayu — AI & ML Researcher
- Dr. Hiwot Shewangizaw — Clinical Advisor & Validation Lead
- Nurse Rahel Tamru — Clinical Advisor & Validation Lead

---

## Support and maintenance

For production deployment and operational guidance, refer to the supporting documentation in this repository, especially [DEPLOYMENT.md](DEPLOYMENT.md) and [ARCHITECTURE.md](ARCHITECTURE.md).

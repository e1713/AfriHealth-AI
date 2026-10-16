# Sahara CodeSwitch Africa Challenge Alignment

This page maps challenge-relevant project requirements to the current
prototype and repository evidence. “Implemented” means present in this
checkout; it does not imply clinical validation, production readiness, or
challenge compliance certification.

| Requirement | Project implementation | Evidence location |
| --- | --- | --- |
| Healthcare category focus | Clinician-support voice documentation prototype for Amharic-English code-switched workflows, including triage support, intake, transcript review, and post-care follow-up. Ordinary prose is not automatically converted into a SOAP note or ICD-10 code. | [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), [`index.html`](index.html), [`main.py`](main.py) |
| Voice downstream clinical workflows | Browser audio capture/transcription, clinician-review triage and intake, structured SOAP validation, post-care analysis/session APIs, and FHIR-compatible export with review gates. The dedicated VoiceBot workflow state machine on the Impact/Follow-up views is a UI-only simulation; it does not schedule calls, contact patients, or send alerts. | [`index.html`](index.html), [`main.py`](main.py) (`/api/v1/process-clinical`, `/api/v1/post-care/analyze`, `/api/v1/post-care/session/start`, `/api/v1/post-care/session/answer`, `/api/v1/fhir/export`, `/api/v1/ehr/commit`), [DEMO_SCRIPT.md](DEMO_SCRIPT.md) |
| Responsible AI and human review | Clinical-safety banners, pending-review status, explicit browser review confirmation, FHIR/EHR sign-off assertions, and server-side FHIR/EHR checks. The caller-supplied sign-off is not authenticated clinician identity or an auditable digital signature; identifiable-patient production use remains blocked on additional controls. | [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md), [README.md](README.md#clinical-safety-features), [`index.html`](index.html), [`main.py`](main.py), [`tests/test_safety.py`](tests/test_safety.py) |
| Working prototype / judge demonstration | Static single-page application with a one-click Impact Dashboard, Challenge Alignment view, VoiceBot Workflow Simulation, and clinical modules. The walkthrough link requires confirmation against the currently deployed build. | [`index.html`](index.html), [DEMO_SCRIPT.md](DEMO_SCRIPT.md#60-second-judge-walkthrough), [README.md](README.md#judge-ready-views) |
| Projected workflow impact | The dashboard displays ~5 minutes/patient, ~200 minutes/clinician-day, ~70% documentation burden reduction, and ~15% patient-support capacity as illustrative pilot projections only. The 200-minute arithmetic assumes 40 consultations at five minutes each. These are not measured or clinically validated results. | [`index.html`](index.html) (`sec-impact`), [README.md](README.md#judge-ready-views) |

## Fast navigation

- In the app, open **Impact Dashboard** for pilot projections and prototype
  trust indicators.
- Open **VoiceBot Workflow Simulation** for the four-step interactive demo.
- Open **Challenge Alignment** for the in-app requirement-to-evidence map.

## Important interpretation limits

- Pilot projections are illustrative assumptions, not measured time savings,
  throughput, adoption, safety, or efficacy outcomes.
- The VoiceBot workflow state machine is a simulation. Do not present it as a
  completed outbound calling integration.
- The prototype's review gate does not establish clinician authentication,
  authorization, or auditability. Do not use identifiable patient data until
  the controls described in [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) are
  implemented and verified.

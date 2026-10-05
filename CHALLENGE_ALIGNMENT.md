# Sahara CodeSwitch Africa Challenge Alignment

This maps challenge-relevant requirements to the current prototype and
repository evidence. Implementation evidence does not imply clinical
validation, production readiness, or challenge certification.

| Requirement | Project implementation | Evidence location |
| --- | --- | --- |
| Healthcare category focus | Clinician-support voice documentation prototype focused on Amharic-English workflows. Clinical artifacts require human verification. | [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md), [`index.html`](index.html), [`main.py`](main.py) |
| Voice downstream clinical workflows | Browser audio capture, transcription, clinician-review triage/intake, post-care workflows, and FHIR-compatible export gates. The VoiceBot state machine is a UI simulation; it does not contact patients or schedule calls. | [`index.html`](index.html), [`main.py`](main.py) (`/api/v1/post-care/analyze`, `/api/v1/fhir/export`, `/api/v1/ehr/commit`), [DEMO_SCRIPT.md](DEMO_SCRIPT.md) |
| Three-or-more speech model comparisons | Six model adapters and a common inference/output schema are implemented. Mock mode verifies data flow only. Live accuracy is unavailable because no eligible, audio-verified benchmark run is established; four local-model adapters remain placeholders. | [benchmark/metadata/BENCHMARK_MANIFEST.csv](benchmark/metadata/BENCHMARK_MANIFEST.csv), [inference_engine.py](inference_engine.py), [evaluator.py](evaluator.py), [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md) |
| Single benchmark source | The 100-case manifest is the sole active reference source. Its text came from the cited source export; it is not independently verified against audio. | [benchmark/metadata/BENCHMARK_MANIFEST.csv](benchmark/metadata/BENCHMARK_MANIFEST.csv), [benchmark/DATASET_CARD.md](benchmark/DATASET_CARD.md), [benchmark/BENCHMARK_LIMITATIONS.md](benchmark/BENCHMARK_LIMITATIONS.md) |
| Responsible AI and human review | Consent/de-identification/hosted-inference gates, safety banners, explicit client review before export, and backend review assertions. Caller-supplied review is not authenticated identity or an auditable signature. | [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md), [tests/test_safety.py](tests/test_safety.py), [`index.html`](index.html), [`main.py`](main.py) |
| Equity-conscious benchmark design | Proposed CEAS combines overall WER-derived accuracy with worst-speaker and worst-code-switch-category accuracy. It is not calculable until references and subgroup labels are adjudicated and minimum coverage is met. | [benchmark/EVALUATION_METRICS.md](benchmark/EVALUATION_METRICS.md), [benchmark/SCORING_RUBRIC_ALIGNMENT.md](benchmark/SCORING_RUBRIC_ALIGNMENT.md) |
| Working prototype / judge demonstration | Single-page application with one-click Impact Dashboard, Challenge Alignment, simulated follow-up, clinical modules, and benchmark view. Confirm the recording reflects this build. | [`index.html`](index.html), [DEMO_SCRIPT.md](DEMO_SCRIPT.md), [SUBMISSION_READINESS.md](SUBMISSION_READINESS.md), [README.md](README.md) |
| Projected workflow impact | Dashboard values are illustrative pilot projections only, not measured outcomes or validated clinical study findings. | [`index.html`](index.html), [README.md](README.md) |
| Optional consented, de-identified audio | Protocol and metadata template are provided. Raw audio, consent, provenance, and provider approval must be handled in restricted storage and verified per case before inference. | [CLINICAL_RECORDING_PROTOCOL.md](CLINICAL_RECORDING_PROTOCOL.md), [BENCHMARK_METADATA_TEMPLATE.csv](BENCHMARK_METADATA_TEMPLATE.csv), [benchmark/metadata/BENCHMARK_MANIFEST.csv](benchmark/metadata/BENCHMARK_MANIFEST.csv) |

## Fast navigation

- Open **Impact Dashboard** for pilot projections and prototype trust indicators.
- Open **VoiceBot Workflow Simulation** for the four-step demonstration.
- Open **Challenge Alignment** for this evidence map.
- Open the benchmark view and [BENCHMARK_RESULTS.md](BENCHMARK_RESULTS.md)
  for current pipeline status and limitations.

## Interpretation limits

- Mock transcripts and simulated latency are not model-performance evidence.
- The source manifest has not been audio-verified; speaker assignments are
  absent and code-switch labels are provisional.
- CEAS is a project-proposed research metric, not a validated fairness score or
  an exact reproduction of a published framework.
- Pilot projections and the VoiceBot workflow must not be presented as
  measured outcomes or a live patient-contact service.
- Review gates do not establish clinician authentication, authorization, or
  auditability. Identifiable-patient use remains blocked on the controls
  described in [RESPONSIBLE_AI.md](RESPONSIBLE_AI.md) and
  [SUBMISSION_READINESS.md](SUBMISSION_READINESS.md).

# Sahara CodeSwitch Africa submission readiness

## Challenge requirements

The challenge brief requests a solution description, working-prototype demo,
technical documentation, comparison across at least three speech models,
ethics/inclusion notes, and optionally consented, de-identified audio.

## Current coverage

| Requirement | Project evidence | Status |
| --- | --- | --- |
| Solution description | Product UI and workflows in `index.html`, `README.md` | Covered |
| Working prototype | Browser app served by `npm start` | Covered; record/confirm the final demo |
| Technical documentation | `README.md`, `main.py`, `ARCHITECTURE.md`, `benchmark/` | Covered |
| Active language scope | Amharic-English v1.0 | Afaan Oromoo-English and Tigrinya-English remain future phases |
| Model comparison pipeline | `inference_engine.py`, `evaluator.py`, `results/` schemas | Implemented, but no live model comparison is currently validated |
| Benchmark corpus | `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx` and manifest | 100 unique source rows marked verified; checksummed audio files present; DOCX differs on 16 and PDF on 19 transcripts |
| Ethics and inclusion | `RESPONSIBLE_AI.md`, `benchmark/EVALUATION_METRICS.md` | Documented; case-level consent and label evidence remain unverified |
| Patient-data production controls | Session persistence and proxy settings | **Not ready for identifiable patient data:** transcript deletion, clinician RBAC, auditability, and production gateway validation remain open |
| Demo video | YouTube walkthrough linked from `README.md` | Confirm accessibility and ensure it reflects the current build |
| Audio/provenance metadata | Manifest and `BENCHMARK_METADATA_TEMPLATE.csv` | Complete only with verified, consented, de-identified information |

## Benchmark evidence decision

The canonical source is the verified 100-case Google Sheet export. Its
`normalized_transcript` values and `review_status=verified` are carried into the
manifest; the DOCX differs on 16 cases and the PDF on 19. Pseudonymized speaker
labels and domains are provided, but speaker-to-case review remains pending and
code-switch categories are provisional. Consent, de-identification, and hosted
approval are unknown. The mock pipeline run demonstrates data flow only. Mock
transcripts and simulated latencies are excluded from accuracy claims.
Consequently, live WER, medical-term recall, CEAS, and model rankings are
**not available**.

The application has a separate embedded five-case UI fixture. It is a product
demonstration, not a benchmark or evidence of ASR performance. Any historical
results generated from retired manifests are excluded from current claims.

Before submitting model metrics, include:

- the master manifest version and paired eligible case counts;
- consented audio provenance and checksums;
- audio-verified/adjudicated references, speaker IDs, and code-switch labels;
- exact model versions and decoding settings;
- frozen metric definitions and subgroup denominators;
- per-case coverage/failure counts and limitations.

Do not claim fairness, clinical efficacy, or model superiority from the
current manifest or mock run.

## Demo script

Record a 2–3 minute walkthrough showing the intended users, a safe prototype
workflow, clinician review, benchmark evidence status, and Responsible AI
limitations. Never show credentials or identifiable patient data.

## Final pre-submission checklist

- [x] Prototype source, local setup, API contracts, and safety documentation
      are included.
- [ ] Record and verify the current-build demo video.
- [ ] Complete consent/provenance records before using audio.
- [ ] Review speaker assignments, clinical domains/entities, and switch
      categories before subgroup scoring or CEAS.
- [ ] Verify exact model versions, metrics, and failed-case coverage.
- [ ] Before identifiable-patient use, implement and verify transcript
      retention/deletion, clinician authentication/RBAC, auditability, and
      production gateway controls.
- [ ] Clinically review generated SOAP, coding, triage, and medication content.

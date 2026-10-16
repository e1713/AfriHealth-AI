# Sahara CodeSwitch Africa submission readiness

## Challenge requirements

The challenge brief requests:

1. a solution description;
2. a short working-prototype demo;
3. code or technical documentation;
4. a comparison across at least three speech models;
5. an ethics/inclusion note; and
6. optional consented, de-identified benchmark audio.

## Current coverage

| Requirement | Project evidence | Status |
| --- | --- | --- |
| Solution description | Product UI and workflow modules in `index.html` | Covered |
| Working prototype | Browser app served by `npm start` | Covered; record a final demo |
| Technical documentation | `README.md`, `main.py`, `server.js`, `benchmark_suite.py` | Covered |
| Active language scope | Amharic-English v1.0 | Afaan Oromoo-English Phase 2; Tigrinya-English Phase 3 (disabled in UI) |
| Primary speech model | Intron Sahara v2.5 | Implemented for live STT and default live benchmark; other providers are optional comparisons |
| Three-model benchmark | `BENCHMARK_RESULTS.md`, `benchmark_report.json`, `evaluation_report_summary.json` | Four complete model outputs scored on the unchanged 15-case Amharic-English manifest using normalized WER, target recall, and M-WER |
| SOAP/ICD-10 processing | `/api/v1/process-clinical` | Frontend trigger is wired; endpoint validates structured JSON or returns a manual-review fallback. It does not generate SOAP or ICD-10 from prose |
| Ethics and inclusion | `RESPONSIBLE_AI.md` | Covered; obtain consent evidence |
| Patient-data production controls | Session metadata persistence and production proxy-auth setting | **Not ready for identifiable patient data: no transcript expiry/deletion, built-in clinician RBAC, or verified production gateway configuration** |
| Demo video link | YouTube walkthrough linked from `README.md` | Confirm accessibility and fit to the challenge requirement; update if it shows an outdated build |
| Benchmark audio metadata | `BENCHMARK_METADATA_TEMPLATE.csv` | Fill with real consented data |
| Recording and audit handoff | `CLINICAL_RECORDING_PROTOCOL.md`, `TEAM_HANDOFF_CHECKLIST.md` | Ready for team use |

## Benchmark evidence decision

The checked-in `BENCHMARK_RESULTS.md` and `benchmark_report.json` are generated
by `benchmark_suite.py` from the 15-row `benchmark_data/manifest.csv`, not from
the three-sample in-app fixture. The report includes four complete output
columns: Intron Sahara v2.5, Whisper Tiny, Wav2Vec2 Base 960h, and Gemini. The
scored figures are Intron 34.91% normalized WER / 57.78% target recall /
42.22% M-WER, Whisper Tiny 99.56% / 23.67% / 76.33%, Wav2Vec2 108.23% /
2.22% / 97.78%, and Gemini 11.46% / 93.33% / 6.67%.
`evaluation_report_summary.json` summarizes this same experiment. OpenAI has
0/15 outputs after HTTP 429 and is not scored.

The fixture currently contains transcript hypotheses embedded in
`benchmark_suite.py`; it does not contain audio files. Do not describe those
hypotheses as independently rerun model outputs unless you attach the audio,
model versions, and inference logs.

The in-app fixture and the four-model transcript report are separate evidence.
The report's target-term recall uses annotated manifest terms; it is not
clinical entity accuracy or demographic fairness. No ASR-FAIRBENCH analysis,
subgroup breakdown, hallucination rate, or streaming segment-loss result is
available. The manifest annotator-count field is blank, and raw audio is not
included in the public repository, so the saved transcripts can be rescored
but the underlying inference cannot be independently rerun from this checkout.

Before submitting, include the measured report and its limitations, including:

- dataset version and sample count;
- language and code-switch composition;
- audio provenance and consent/de-identification status;
- model versions and decoding settings;
- WER/entity-accuracy definitions;
- per-sample results or an accessible artifact; and
- limitations, including the small current fixture.

Do not claim 0% WER, 100% entity accuracy, or benchmark-wide superiority
unless those figures can be reproduced from the submitted, consented dataset.

## Demo script

Record a 2–3 minute unlisted video showing:

1. the three care modules and intended users;
2. a consented, de-identified sample or the built-in judge-mode sample;
3. partial and final transcription;
4. clinician review of the generated artifacts;
5. the benchmark matrix and methodology;
6. the Responsible AI limitations; and
7. server-side API-key configuration without exposing the key.

## Final pre-submission checklist

- [x] Generate the 15-case four-model transcript comparison from complete
      manifest outputs; do not describe the in-app fixture as that comparison.
- [ ] Complete and record the manifest annotator-count metadata.
- [ ] Confirm the existing README YouTube walkthrough meets the challenge
      requirement and add its accessible URL to the submission form; update it
      if it shows an outdated build.
- [ ] Fill [BENCHMARK_METADATA_TEMPLATE.csv](./BENCHMARK_METADATA_TEMPLATE.csv)
      only with real consent and provenance information.
- [ ] Follow [CLINICAL_RECORDING_PROTOCOL.md](./CLINICAL_RECORDING_PROTOCOL.md)
      and complete [TEAM_HANDOFF_CHECKLIST.md](./TEAM_HANDOFF_CHECKLIST.md).
- [ ] Verify all model names, versions, and metrics against the actual runs.
- [ ] Deploy with `INTRON_API_KEY` server-side and set `ALLOWED_ORIGINS` to
      the exact production origins.
- [ ] Before any identifiable patient data is used, implement and verify
      transcript retention/deletion controls and clinician authentication with
      role-based access.
- [ ] Have a clinician review generated SOAP, ICD-10, triage, and medication
      outputs before showing them as clinical artifacts.
- [ ] Implement and validate a backend-enforced medication safety gate before
      claiming automated viral/allergy checks or blocked medication suggestions.
- [ ] Remove local secrets and temporary challenge downloads before commit.

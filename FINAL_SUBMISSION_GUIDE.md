# Sahara Challenge Final Submission Guide

## Submission statement

AfriHealth AI is a clinician-support voice documentation prototype for
Amharic-English code-switched workflows. It helps capture speech, review
transcripts, structure clinical intake, and prepare follow-up documentation.
It does not diagnose, prescribe, or replace clinical judgment.

## What is included

- Browser prototype: `index.html`
- FastAPI integration and review gates: `main.py`
- Setup, architecture, and Responsible AI documentation
- The authoritative 100-case source-text manifest:
  `benchmark/metadata/BENCHMARK_MANIFEST.csv`
- Resumable inference and evaluation scripts: `inference_engine.py`,
  `evaluator.py`
- Benchmark governance, metric definitions, and result templates in
  `benchmark/`
- Mock-aware visualizations and report generators

## Evidence interpretation

The manifest contains source reference text, not independently audio-verified
gold transcripts. Speaker IDs are missing and code-switch category annotations
are provisional. No validated clinical model-performance comparison or CEAS
score is currently available. Mock transcripts and simulated latency verify
pipeline behavior only and must not be presented as measured ASR results.

The in-app five-case fixture is separate product-demo content, not benchmark
evidence.

## Reviewer run instructions

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-benchmark.txt
python validate_and_prep.py
python inference_engine.py --env mock
python evaluator.py
python visualize_results.py
python generate_results_doc.py
```

Mock inference is offline and uses synthetic transcripts. Before any live
hosted inference, verify approvals for every case and provide the required
server-side keys:

```bash
python inference_engine.py --env live --models sahara gemini
```

The current manifest has consent, de-identification, and hosted-inference
approval set to false. Live hosted inference will therefore be blocked until
those fields are properly established. Several local model adapters remain
placeholders.

## Privacy and clinical review

Do not commit raw recordings, credentials, consent records, or sensitive
provider payloads. Before real-patient use, implement and verify clinician
authentication/RBAC, auditability, retention/deletion controls, and production
gateway configuration. A qualified clinician must review generated clinical
artifacts; the system is not authorized for autonomous care.

## Demo video

Confirm that the existing README walkthrough is accessible and reflects the
current build. Use [DEMO_SCRIPT.md](./DEMO_SCRIPT.md) to record an updated
walkthrough if required.

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
- Canonical verified ground-truth export and evaluation manifest:
  `benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx`,
  `benchmark/metadata/GROUND_TRUTH_SOURCE.csv`, and
  `benchmark/metadata/BENCHMARK_MANIFEST.csv`
- Resumable inference and evaluation scripts: `inference_engine.py`,
  `evaluator.py`
- Benchmark governance, metric definitions, and result templates in
  `benchmark/`
- Mock-aware visualizations and report generators

## Evidence interpretation

The primary sheet marks all 100 normalized references `verified`; the active
manifest records that evidence and matching audio checksums. The older DOCX
differs on 16 cases and the PDF on 19; neither is canonical. Speaker labels are pseudonymized but
their assignments remain pending separate review; code-switch categories are
provisional. Consent, de-identification, and hosted-inference approval remain
unknown. No live clinical model-performance comparison or CEAS score is
available. Mock transcripts and simulated latency are not measured ASR results.

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

The current manifest records consent, de-identification, and hosted-inference
approval as `unknown`. Live hosted inference remains blocked until those fields
have evidence-backed approvals. Several local model adapters remain placeholders.

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

# Sahara Challenge Final Submission Guide

## Submission statement

AfriHealth AI is a clinician-reviewed voice documentation and decision-support
prototype for English-Amharic code-switched workflows (active v1.0 scope).
Afaan Oromoo-English is planned for Phase 2 and Tigrinya-English for Phase 3. It
helps frontline workers capture speech, review a transcript, structure a
clinical intake, and prepare follow-up documentation. It does not diagnose,
prescribe, or replace clinical judgment.

## What is included

- Working browser prototype: `index.html`
- FastAPI integration and safety gate: `main.py`
- Optional static/proxy server: `server.js`
- Setup and endpoint instructions: `README.md`
- Architecture and data-flow description: `ARCHITECTURE.md`
- Responsible AI and inclusion controls: `RESPONSIBLE_AI.md`
- Reproducible fixture benchmark: `benchmark_suite.py`
- Four-model, 15-case transcript benchmark: `BENCHMARK_RESULTS.md`,
  `benchmark_report.json`, and `evaluation_report_summary.json`
- AfriSwitch import and real-inference tooling:
  `afriswitch_import.py` and `afriswitch_asr_benchmark.py`
- Reviewed 15-case simulated clinical benchmark report:
  `clinical_validation_report.json`
- Recording protocol, metadata template, and team handoff checklist

## Evidence interpretation

Use the evidence labels below in the submission:

1. **Prototype evidence:** browser workflows and built-in judge-mode samples.
2. **Fixture benchmark evidence:** reproducible demonstration scores from the
   labelled fixture. These are not general performance claims.
3. **General ASR evidence:** bounded AfriSwitch pilot import/inference. This is
   not clinical validation.
4. **Simulated clinical benchmark evidence:** 15 reviewed Amharic-English
   recordings of simulated clinical scenarios, uploaded to Intron with a mean
   WER of `0.564` and mean target-term recall of `0.443`. These results are
   useful for model comparison, error analysis, and terminology improvement,
   but are not evidence from real patients and do not authorize autonomous
   care.
5. **Four-model transcript comparison:** The same 15-case manifest contains
  complete outputs for Intron Sahara v2.5, OpenAI Whisper Tiny, English-only
  Meta Wav2Vec2 Base 960h, and Google Gemini. The report scores saved
  transcripts against verified references; it does not rerun inference.
  Gemini currently has the lowest normalized WER (11.46%) and highest
  target-term recall (93.33%); Intron scores 34.91% normalized WER, 57.78%
  target-term recall, and 42.22% M-WER. These
  small simulated-set results do not establish population performance or
  fairness. The annotator-count field is blank, and the source audio is not
  included in the public repository.

`evaluation_report_summary.json` is a metadata-rich summary of the same
four-model experiment in `benchmark_report.json`. Keep both separate from the
single-provider `clinical_validation_report.json`, which uses a different
evaluation protocol.

## Run instructions for reviewers

### Frontend

```powershell
npm install
npm start
```

Open `http://localhost:3000`.

### FastAPI integration

```powershell
python -m pip install -r requirements.txt
$env:INTRON_API_KEY = "your-key"
python -m uvicorn main:app --reload --port 8000
```

Never put the real key in the frontend or commit it.

### Safe judge path without microphone

1. Open Module 1.
2. Select `GOLD-ETH-001`, `GOLD-ETH-002`, or `GOLD-ETH-003`.
3. Use **Pre-load Audio Judge Mode**.
4. Review the transcript, extracted entities, triage label, and recommendation.
5. Explain that the result is clinician-review output.

## Privacy and clinical review

The public repository intentionally excludes raw audio, complete provider
responses, and private transcripts. The reviewed recordings are simulated
clinical scenarios with no real patient identities. Detailed files remain in
the approved local validation package.

Before any real clinical deployment or real-patient evaluation, obtain:

- documented consent and de-identification;
- clinician review of the 15-case outputs;
- completed safety scenarios and Responsible AI sign-off;
- an approved retention and access-control policy;
- production CORS, authentication, monitoring, and incident-response
  configuration.

## Demo video

The README links the project's YouTube walkthrough. Confirm that it is
accessible to judges and demonstrates the current build; use
[DEMO_SCRIPT.md](./DEMO_SCRIPT.md) to record an updated 2–3 minute video if the
existing walkthrough does not meet the challenge's demo requirement.

## Final checklist

- [x] Working prototype source included.
- [x] Local setup and API contracts documented.
- [x] Architecture and data-flow documentation included.
- [x] Responsible AI, privacy, and medication safety limitations documented.
- [x] Benchmark limitations explicitly documented.
- [x] Clinical baseline aggregate report included without private audio.
- [x] No API key or raw clinical recordings committed.
- [ ] Add a demo URL only if the challenge portal makes it mandatory.
- [ ] Complete clinician sign-off and attach consent evidence privately if
      requested by the challenge organizers.

# Reproducibility Guide

## Environment

Use a clean, recorded Python environment and the repository's dependency files.
For the existing benchmark evaluator:

```bash
python -m pip install -r requirements.txt
python -m pip install -r requirements-benchmark.txt
```

The optional ASR/audio stack can be large and may require platform-specific
PyTorch installation. Record Python, OS, package lock/versions, CPU/GPU model,
driver, and thread settings. Do not install unpinned versions for a final
comparison without recording the resolved versions.

## Configuration and privacy

- Put provider credentials in an untracked `.env` or secret manager; never put
  keys in source, command history, notebooks, manifests, or reports.
- Before hosted inference, verify consent, de-identification, source rights,
  applicable provider terms, region/retention controls, and approval to transmit
  each recording.
- Use only the intended de-identified corpus in the run environment. Restrict
  access to raw audio and full transcripts.
- Record the dataset release/version and SHA-256 for each source and canonical
  audio file.

## Prepare and execute

1. Verify each canonical audio file and link it in
   [`metadata/BENCHMARK_MANIFEST.csv`](metadata/BENCHMARK_MANIFEST.csv).
2. Use the verified spreadsheet's normalized transcript as the reference and
   preserve its source-row evidence. Independently review speaker assignments,
   code-switch labels, critical terms, consent, de-identification, provenance,
   and provider approval; resolve pending fields before hosted inference or
   subgroup scoring.
3. Standardize audio using the repository's `validate_and_prep.py` only after
   reviewing the preservation implications. Its normalization/denoising
   switches are opt-in.
4. Run a safe mock pass over the manifest:

   ```bash
   python inference_engine.py --env mock
   ```

   It reads cleaned audio from `cleaned_audio/`, skips missing recordings
   without crashing, and writes synthetic outputs under `results/`. Audio
   standardization from `raw_audio/` is available through:

   ```bash
   python validate_and_prep.py
   ```

5. Mock transcripts and randomized latency are synthetic, not model results.
   For live hosted API inference, set `consent_obtained`, `de_identified`, and
   `hosted_inference_approved` to `true` only when each claim is supported by
   an evidence reference in the corresponding manifest column. The validator
   and inference engine reject unsupported positive claims. Do not treat a
   value in `approvals.csv` as evidence unless its evidence-reference columns
   cite auditable records. The case must also be `verified_present` with
   `audio_presence_evidence_reference`, `audio_checksum_evidence_reference`,
   and a SHA-256 matching the cleaned WAV that will be uploaded. Then run only
   configured APIs:

   ```bash
   python inference_engine.py --env live --models sahara gemini
   ```

   The manifest currently records these approval fields as `unknown`, with no
   evidence references, so hosted inference is blocked. Whisper,
   Wav2Vec2, SpeechBrain, and NeMo are local adapter placeholders and are not
   yet runnable.

6. Run hosted providers only with explicit project approval and valid keys.
   The compatibility entry point `generate_benchmark_hypotheses.py` delegates
   to the same manifest-based inference engine; it does not mutate manifest
   content or provide a separate model runner.
7. Score with `python evaluator.py`, visualize with
   `python visualize_results.py`, and update summaries with
   `python generate_results_doc.py`. Raw hypotheses remain in approved
   restricted storage; keep failed cases visible.

The source contains 100 cases marked verified and matching audio files exist.
Do not claim a completed 100-case model comparison until governance approvals
are documented, unresolved labels are adjudicated, and paired live inference
is complete. Inference may still
run on a partial set, but reports must disclose coverage and failures.

## Required run artifacts

- Immutable manifest and audio checksums.
- Model/provider/checkpoint/version and complete decode configuration.
- Dependency lock or exact resolved package versions.
- Per-case status and elapsed-time records in restricted storage.
- Scoring code revision, normalization and alias-table versions.
- Aggregate result table, coverage, failure counts, and this limitations note.
- Human review/adjudication and dataset-provenance records.

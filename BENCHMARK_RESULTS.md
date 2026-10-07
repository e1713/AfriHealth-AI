# AfriHealth AI Benchmark Results

## Current evidence status

The canonical source is the verified 100-case spreadsheet at
[benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx](benchmark/metadata/GROUND_TRUTH_SOURCE.xlsx)
with a normalized [CSV](benchmark/metadata/GROUND_TRUTH_SOURCE.csv). All rows
have unique IDs and `review_status=verified`; the manifest uses the canonical
normalized transcript. Matching audio files and checksums are recorded. The
legacy DOCX differs on 16 cases and the PDF on 19; neither overrides the sheet.
Speaker labels are pseudonymized, but assignment review remains pending;
code-switch labels remain provisional. Consent, de-identification, and
hosted-inference approval are `unknown`.

See [GROUND_TRUTH_COVERAGE_REPORT.md](GROUND_TRUTH_COVERAGE_REPORT.md) for case
coverage and [GROUND_TRUTH_AUDIT_REPORT.md](GROUND_TRUTH_AUDIT_REPORT.md) for
source reconciliation and unresolved governance states.

No validated live ASR accuracy comparison or Clinical Equity-Adjusted ASR
Score (CEAS) is currently available. Mock runs produce synthetic transcripts
and simulated latency for pipeline testing only. Mock accuracy metrics are
intentionally unscored.

The embedded five-case application fixture is demo content, not a speech
benchmark.

See [benchmark/EVALUATION_METRICS.md](benchmark/EVALUATION_METRICS.md) for
metric definitions and CEAS prerequisites, and
[benchmark/BENCHMARK_LIMITATIONS.md](benchmark/BENCHMARK_LIMITATIONS.md) for
the corpus limitations.

<!-- BEGIN AUTO-GENERATED EVALUATION SUMMARY -->
## Current Evaluation Pipeline Summary

> Generated from `results/final_evaluation_metrics.csv` at 2026-10-05 23:00 UTC. The source marks all 100 normalized references verified; speaker and code-switch labels and governance approvals remain under review.

| Model | Status | Live outputs | Mock outputs | Failed | Mean WER | Medical-term recall | Critical miss rate | Live mean latency (s) | Simulated mean latency (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Sahara | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.321 |
| Gemini | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.225 |
| Whisper | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.280 |
| Wav2Vec2 | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.214 |
| SpeechBrain | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.292 |
| NeMo | mock_only_accuracy_not_scored | 0 | 100 | 0 | N/A | N/A | N/A | N/A | 1.282 |

**Interpretation:** Mock outputs are synthetic pipeline fixtures. Accuracy and critical-term metrics are intentionally `N/A` for mock-only runs; simulated latency is not measured inference latency.

Code-switch category breakdown is available in `results/figures/codeswitch_breakdown.png` only when live outputs can be joined to manifest categories. Those categories are provisional script-share estimates until human confirmation.
<!-- END AUTO-GENERATED EVALUATION SUMMARY -->

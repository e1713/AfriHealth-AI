# Model Recommendation

<!-- BEGIN AUTO-GENERATED MODEL RECOMMENDATION -->
## Automated Evaluation Snapshot

> Generated from `results/final_evaluation_metrics.csv`. This is a descriptive pipeline summary, not clinical approval or an autonomous-use recommendation.

| Model | Evidence status | Live / mock outputs | WER | Medical-term recall | Critical-term miss rate | Live latency (s) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Sahara | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |
| Gemini | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |
| Whisper | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |
| Wav2Vec2 | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |
| SpeechBrain | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |
| NeMo | mock_only_accuracy_not_scored | 0 / 100 | N/A | N/A | N/A | N/A |

### Recommendation

No model is ranked or recommended for clinical use by this generated summary. A mock-only run provides no evidence about model accuracy or clinical suitability. The canonical spreadsheet marks all references verified, but no live paired model scores are available.

### Evidence required before selecting a model

- Paired live outputs on the same audio cases with exact model/provider versions.
- Clinician-adjudicated target terms, criticality, and entity annotations; preserve the canonical reference source.
- Review of medication, dose, negation, and critical-term errors by qualified clinicians.
- Hosted-data governance, privacy, latency, reliability, and deployment review.

<!-- END AUTO-GENERATED MODEL RECOMMENDATION -->

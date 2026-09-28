# Clinical Audio Dataset Benchmark Report

> **Evidence status:** Results were scored from 15 manifest-selected recordings against verified references. Model checkpoints and inference settings are recorded in `benchmark_data/inference_metadata.json`.

| Model | Average WER ↓ | Clinical Entity Recall ↑ | FAAS Score (dB) ↑ | Status |
| :--- | :---: | :---: | :---: | :---: |
| Intron Sahara v2.5 | 47.82% | 90.00% | 2.75 | Measured hosted ASR |
| OpenAI Whisper Tiny | 106.41% | 63.33% | -2.25 | Measured local ASR |
| Meta Wav2Vec2 Base 960h (English) | 118.77% | 46.67% | -4.06 | English-only local baseline; checkpoint in inference metadata |
| Google Gemini gemini-flash-latest | 29.20% | 96.67% | 5.20 | Measured ASR |

### Evaluation Methodology
1. **Word Error Rate (WER)**: Normalized string distance metric (S + D + I) / N.
2. **Clinical Entity Recall**: Recall rate of reference clinical terms (symptoms, dosages, diagnoses).
3. **FAAS composite**: Calculated as 10 * log10(Clinical Entity Recall / WER); this aggregate score is not a demographic fairness metric.

The separate 15-case clinical validation baseline reported 56.38% mean WER,
44.33% target-term recall, and critical-term misses in 6 cases. That result is
for clinician review only and does not support autonomous clinical use.

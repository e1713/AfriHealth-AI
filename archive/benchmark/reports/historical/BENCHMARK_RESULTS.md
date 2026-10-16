# Clinical Audio Dataset Benchmark Report

> **Evidence status:** Results were scored from 15 manifest-selected recordings against verified references. Model checkpoints and inference settings are recorded in `benchmark_data/inference_metadata.json`.

| Model | Normalized WER ↓ | Mean Target-Term Recall ↑ | M-WER ↓ | Status |
| :--- | :---: | :---: | :---: | :--- |
| Intron Sahara v2.5 | 34.91% | 57.78% | 42.22% | Measured hosted ASR |
| OpenAI Whisper Tiny | 99.56% | 23.67% | 76.33% | Measured local ASR |
| Meta Wav2Vec2 Base 960h (English) | 108.23% | 2.22% | 97.78% | English-only local baseline; checkpoint in inference metadata |
| Google Gemini gemini-flash-latest | 11.46% | 93.33% | 6.67% | Measured hosted ASR |

### Evaluation Methodology
1. **Normalized WER**: Clinical text normalization standardizes punctuation, common units, and selected transliterations before whitespace-token Levenshtein scoring (using `jiwer` when installed).
2. **Mean Target-Term Recall**: For each recording, the fraction of semicolon-separated manifest target terms matched by normalized tokens; parenthetical bilingual alternatives are accepted. Clinical aliases may match English, Amharic, and transliterated variants.
3. **M-WER**: `1 - target-term recall`, calculated per sample then averaged; lower is better.
4. **Fairness**: No demographic or subgroup fairness metric is computed in this benchmark.

The separate 15-case clinical validation baseline reported 56.38% mean WER,
44.33% target-term recall, and critical-term misses in 6 cases. That result is
for clinician review only and does not support autonomous clinical use.

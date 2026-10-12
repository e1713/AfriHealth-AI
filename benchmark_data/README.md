The shared audit document reports audio-confirmed reference verification for all 15 cases, and the user confirmed consent/de-identification documentation; these flags are recorded in the manifest. Annotator count is still blank. All 15 samples currently have outputs from Intron Sahara, `openai/whisper-tiny`, and `facebook/wav2vec2-base-960h`; the latter is English-only and not an Amharic/code-switch model. See `inference_metadata.json` for exact checkpoints and run status.

Optional hosted API hypotheses can be generated from the server-side `.env` configuration. Never paste API keys into source files or chat. The keys included in a previous setup message should be rotated before reuse.

```sh
./.venv/bin/python generate_benchmark_hypotheses.py --only openai --include-hosted-providers
./.venv/bin/python generate_benchmark_hypotheses.py --only gemini --include-hosted-providers
./.venv/bin/python benchmark_suite.py
```

The first two commands require documented consent/de-identification in every manifest row and send audio to the selected hosted provider. They save raw transcripts to `openai_hypothesis` and `gemini_hypothesis`. HTTP 429 and 503 responses receive up to three retries with exponential backoff (respecting a numeric `Retry-After` header when present). Gemini requests are spaced 15 seconds apart by default; override with `--gemini-request-interval-seconds`. Configure ordered Gemini keys with `GEMINI_API_KEY`, `GEMINI_API_KEY_1`, and `GEMINI_API_KEY_2`; on 429 the adapter tries the next configured key, and it stops once all configured keys are rate-limited. Key fallback only helps when each key belongs to a separately authorized project with its own available quota; keys in the same project share project-level limits. Successful rows are saved immediately, so rerunning resumes only missing rows. Benchmark reports include either model only when all 15 rows have outputs for that provider; partial columns block scoring rather than silently reducing the sample count. The Gemini key is sent using the `x-goog-api-key` header, not a URL parameter.
# Benchmark audio dataset

The manifest uses only 15 primary recordings, one for each audited case CS-01 through CS-15. The source folder's alternate takes and duplicate remain on disk but are not referenced by the benchmark manifest. Audio is kept locally and ignored by Git. Consent and de-identification were confirmed by the user and recorded in the manifest; annotator count is still blank.

## Expected format

The transcript workbook in the second Drive folder matches all 15 cases and target-term annotations in the repository's [CLINICAL_REFERENCE_TRANSCRIPTS.csv](../CLINICAL_REFERENCE_TRANSCRIPTS.csv); `manifest.csv` maps each case to one selected recording. `CS_04` uses source `CS_04.m4a` because no `CS-04.m4a` exists. Alternate takes and the byte-identical duplicate `CS_03.m4a` are deliberately omitted from the manifest. The original recording path is retained in `source_audio_file`; `audio_file` points to the normalized WAV used for evaluation.

Create or validate WAV files with:

```sh
./.venv/bin/python convert_benchmark_audio.py
```

The command reads only manifest-selected recordings, writes mono 16 kHz PCM s16 WAV files under `benchmark_data/wav/`, validates each output, and does not overwrite valid WAVs unless `--force` is supplied.

The loader in [benchmark_suite.py](../benchmark_suite.py) reads:

- `benchmark_data/manifest.csv`

An existing CSV manifest is authoritative, including when its transcript or model-output fields are empty. The built-in fixture is used only when no CSV manifest exists.

## Current state

The shared audit document reports audio-confirmed reference verification for all 15 cases, and the user confirmed consent/de-identification documentation; these flags are recorded in the manifest. Annotator count is still blank. Intron, Whisper Tiny, and Wav2Vec2 Base outputs are present for all 15 samples. The Wav2Vec2 checkpoint is English-only and is not an Amharic/code-switch model. See `inference_metadata.json` for exact checkpoints and run status. OpenAI and Gemini outputs are optional additions; a provider is included in reports only after its outputs cover all 15 samples.

## Required columns

- `sample_id`
- `language_pair`
- `audio_file`
- `source_audio_file`
- `reference`
- `target_terms`
- `reference_source`
- `consent_obtained`
- `de_identified`
- `annotator_count`
- `reference_verified`
- `verified_gold_standard`
- `intron_hypothesis`
- `whisper_hypothesis`
- `wav2vec2_hypothesis`
- `openai_hypothesis` (optional)
- `gemini_hypothesis` (optional)
- `duplicate_of` (optional; excluded from scoring)

For final benchmark submission, the dataset should also include:

- consent status
- de-identification status
- annotator count
- audio provenance
- model versions and decode settings
- per-sample reference transcripts

Only set `verified_gold_standard` to `true` after the corresponding reference transcript has been checked and its provenance documented.

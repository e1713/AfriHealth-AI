# Benchmark Limitations

- **Coverage:** The canonical Google Sheet has 100 unique cases and all matching
  WAV filenames exist in `raw_audio/` and `cleaned_audio/`. The manifest stores
  cleaned-audio SHA-256 checksums. Checksums and filenames do not establish
  licensing, consent, or source provenance.
- **Reference quality:** All 100 source rows carry `review_status=verified` and
  populated normalized transcripts. The raw-transcript column is blank. The
  older DOCX differs from this source on 16 cases and the PDF on 19; use the
  sheet's normalized transcript as canonical. The repository does not contain separate
  annotator-agreement records.
- **Single active source:** `metadata/BENCHMARK_MANIFEST.csv` is the sole
  reference source for this benchmark. Historical reports from removed
  manifests must not be merged into current metrics or cited as current
  performance evidence.
- **Speaker representation:** The source supplies five name-like speaker
  labels and case mappings. Repository copies pseudonymize those labels; the
  mapping is not retained. Speaker-to-case assignment review remains pending.
- **Domain and switch labels:** Clinical domains and an Amharic-English
  language-mix label are source-populated. Code-switch categories in the
  manifest remain provisional script-share estimates, not token-level audio
  annotations.
- **Language scope:** Amharic-English clinical speech only. Results do not
  generalize to other languages, dialects, facilities, devices, or acoustic
  environments.
- **Size and sampling:** A 100-case corpus, especially with five speakers,
  cannot support robust demographic subgroup or population claims. Case mix
  and speaker repetition can inflate apparent sample size.
- **No fairness assessment:** Language/script categories are not demographic
  groups. This benchmark is not a demographic fairness or bias audit.
- **Not diagnostic:** ASR and entity recall do not validate diagnosis,
  treatment, dosage safety, clinical efficacy, or autonomous clinical use.
- **Model comparability:** Hosted APIs can change; checkpoints, language
  support, prompts, decoding, hardware, and network conditions differ. Current
  Wav2Vec2 evidence uses an English-only checkpoint.
- **No live Tier 2 evidence:** SpeechBrain and NeMo are proposed candidates,
  not measured models in current repository artifacts.
- **Privacy/provenance:** Manifest consent, de-identification, and hosted-use
  states are `unknown`; no per-case evidence references are present. Verify
  consent, de-identification, audio license, retention, and provider approvals
  per asset. Do not publish recordings, identifiers, or full sensitive
  transcripts.

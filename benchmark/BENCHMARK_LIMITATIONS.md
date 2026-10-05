# Benchmark Limitations

- **Coverage:** The authoritative source manifest defines 100 text cases. A
  complete 100-recording audio benchmark is not established by the manifest
  alone, and the current mock run is not performance evidence.
- **Reference quality:** The source contains reference utterances and focus
  terms, but the accessible export does not document audio-aligned expert
  verification, annotator agreement, or adjudication for every item. Treat
  references as provided source text until those checks are recorded.
- **Single active source:** `metadata/BENCHMARK_MANIFEST.csv` is the sole
  reference source for this benchmark. Historical reports from removed
  manifests must not be merged into current metrics or cited as current
  performance evidence.
- **Speaker representation:** The project brief targets five speakers, but
  speaker-to-case mapping and demographic/recording metadata were not provided
  in the accessible corpus. No assignments are fabricated here.
- **Domain and switch labels:** The source includes batch descriptions but not
  dependable case-level medical-domain labels. Manifest switch categories are
  provisional estimates from script share; not audio-grounded annotations.
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
- **Privacy/provenance:** Consent, de-identification, audio license, retention,
  and provider transmission approvals must be verified per asset. Do not
  publish recordings, identifiers, or full sensitive transcripts.

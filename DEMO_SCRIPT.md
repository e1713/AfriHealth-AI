# Sahara challenge demo script

Target duration: 2–3 minutes. Use only built-in judge-mode samples or audio
for which consent and de-identification have been documented.

## 60-second judge walkthrough

1. **0:00–0:10 — Impact Dashboard:** Open the first navigation tab. Point out
   the pilot-projection disclaimer and say these figures are illustrative,
   not measured or clinically validated outcomes.
2. **0:10–0:25 — VoiceBot Workflow Simulation:** Use **VoiceBot Workflow
   Simulation**, advance through the four states, and show the fictional
   adverse-reaction log. State that no patient is called or contacted.
3. **0:25–0:40 — Challenge Alignment:** Open the mapping view to show the
   implementation and evidence locations for voice workflows, health focus,
   model comparison, and Responsible AI.
4. **0:40–1:00 — Benchmark and review gate:** Open the benchmark evidence,
   name the four-model, 15-case saved-transcript comparison and its limitations,
   then show the pending clinician review / FHIR gate.

## 0:00–0:20 — Problem and users

Say: “AfriHealth AI v1.0 focuses on clinician-reviewed English-Amharic
code-switched documentation. Afaan Oromoo-English is Phase 2 and
Tigrinya-English is Phase 3. It does not replace clinical judgment.”

Show the three care modules and the target frontline workflow.

## 0:20–1:05 — Frontline triage

Open Module 1 and select a built-in sample such as
`GOLD-ETH-001: Pediatric High Fever`. Use “Pre-load Audio Judge Mode” so the
demo is deterministic and does not expose a patient recording.

Show the transcript, extracted medical entities, triage classification, and
referral recommendation. State that the clinician must verify every result
against the source audio and patient context.

## 1:05–1:35 — Clinical intake and follow-up

Open Module 2 to show the editable clinical/EHR intake fields, then Module 3
to show the post-care voice workflow. Do not claim that plain transcript input
is automatically converted into a SOAP note; the clinical text API currently
validates structured JSON and otherwise returns a manual-review fallback.

## 1:35–2:10 — Benchmark

Distinguish the in-app fixture matrix from the offline comparative report. The
in-app matrix uses embedded hypotheses and is not independent audio evaluation.
Show `BENCHMARK_RESULTS.md` for the 15-case transcript comparison:

| Model | Normalized WER | Target-term recall | M-WER |
| --- | ---: | ---: | ---: |
| Intron Sahara v2.5 | 34.91% | 57.78% | 42.22% |
| OpenAI Whisper Tiny | 99.56% | 23.67% | 76.33% |
| Meta Wav2Vec2 Base 960h (English) | 108.23% | 2.22% | 97.78% |
| Google Gemini gemini-flash-latest | 11.46% | 93.33% | 6.67% |

Say: “These scores are from saved transcripts on 15 simulated
Amharic-English cases. Gemini scores best on this small set. The English-only
Wav2Vec2 checkpoint is a limited baseline. M-WER is one minus target-term
recall; neither metric is a fairness measure, and these results do not
establish population-wide or clinical performance.”

## 2:10–2:35 — Safety and deployment

Show the Responsible AI note. Mention consent, de-identification,
human-in-the-loop review, and server-side API-key storage. Do not display or
type a real API key into the recording.

## Final spoken limitation

“This prototype is a clinical documentation and decision-support aid. It must
not be used as an autonomous diagnostic or prescribing system.”

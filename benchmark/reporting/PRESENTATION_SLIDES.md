# AfriHealth AI — Sahara CodeSwitch Africa Challenge
## Six-slide presentation script

**Suggested runtime:** 5–6 minutes  
**Audience:** Challenge judges, clinical reviewers, and technical evaluators  
**Presenter:** Ermias Amare  

### Presentation guardrails

- The active corpus is a 100-case **source-text manifest**, not a verified
  100-recording benchmark release.
- The mock inference run validates pipeline behavior only. Mock transcripts
  and simulated latency are not model results.
- CEAS is a proposed, project-specific research metric. It has not been
  calculated, validated, or independently compared with a published
  implementation.
- Do not describe projected workflow impact as measured savings, claim
  clinical efficacy, or present this prototype as ready for identifiable
  patient data.

---

## Slide 1 — Title

### On-slide content

**AfriHealth AI**  
**Clinician-reviewed voice workflows for Amharic-English care**

Sahara CodeSwitch Africa Challenge  
Ermias Amare · Sahara Healthcare Suite

**From spoken clinical conversations to reviewable documentation workflows**

### Speaker script

“Hello, I’m Ermias Amare, and this is AfriHealth AI, a clinician-support
prototype focused on Amharic-English code-switched clinical conversations.

Our goal is to make voice-enabled documentation workflows more practical for
healthcare teams while keeping clinicians in control. The application brings
together speech capture, transcript review, clinical intake and follow-up
demonstrations, and a benchmark pipeline designed around clinical terminology
and language switching.

Throughout this presentation I’ll distinguish implemented workflow
capabilities from benchmark evidence. In particular, our current benchmark
manifest contains source text for 100 cases; it is not yet a fully verified
audio benchmark.”

### Visual direction

- Show the AfriHealth AI project name and a clean product screenshot.
- Keep the subtitle readable; avoid unsupported performance or outcome claims.
- Optional footer: “Prototype · Human review required”.

### Transition

“To explain why this matters, let’s start with the documentation challenge.”

---

## Slide 2 — Problem

### On-slide content

**The problem: clinical speech is multilingual; documentation workflows are not**

- Amharic-English code-switching is part of real communication.
- Clinical terms, medication names, doses, numbers, and negation are
  consequential transcription details.
- Manual note-taking competes with clinician attention during a consultation.
- A transcript is not a clinical decision: context and review still matter.

**Design principle:** Support the clinician; do not replace clinical judgment.

### Speaker script

“In clinical conversations, language does not always follow clean boundaries.
A patient or clinician may move between Amharic and English within a sentence,
especially around symptoms, diagnoses, tests, and medicines.

That creates a difficult documentation problem. A recognizer can produce
fluent-looking text and still miss a medication, dose, number, negation, or
code-switched phrase. Those errors matter because a transcript may be used as
the starting point for documentation and follow-up.

AfriHealth AI is designed around a review-first workflow. The system can help
capture and structure information, but a transcript or draft is not a diagnosis
and is not a substitute for clinical judgment. We make human review an
explicit part of the product boundary rather than treating automation as the
goal by itself.”

### Visual direction

- Use a simple speech-to-documentation illustration with Amharic and English
  text fragments, without patient-identifying content.
- Highlight “medication · dose · negation · code-switch”.
- Avoid imagery implying autonomous diagnosis or treatment.

### Transition

“That review-first principle is reflected in the architecture.”

---

## Slide 3 — Architecture

### On-slide content

**A review-first clinical voice workflow**

```text
Clinician / patient conversation
              ↓
       Audio capture
              ↓
  ASR provider or local adapter
              ↓
 Draft transcript + terminology review
              ↓
 Clinician review and correction
              ↓
 Structured intake / approved export
```

**Implemented safeguards and boundaries**

- Provider credentials remain server-side.
- Draft clinical artifacts require clinician review.
- FHIR-compatible export and EHR commit use review gates.
- VoiceBot follow-up sequence is a **workflow simulation**, not a live calling
  service.

### Speaker script

“The frontend captures or accepts audio and sends eligible requests through
the application backend. Provider credentials stay on the server rather than
in the browser. The backend returns transcription or application outputs to a
review workflow.

The clinician can review and correct the transcript and structured
information. Export paths include explicit review gates; this is a prototype
control, not a claim of authenticated clinician identity, complete auditability,
or production readiness.

The benchmark tooling is a separate path. A resumable inference engine reads
the shared manifest and standardized audio folder, records per-attempt status
and latency, and writes results separately from reference data. The evaluator
then computes available metrics while leaving mock-only accuracy unscored.

The follow-up VoiceBot shown in the application is a workflow simulation. It
does not place calls, schedule reminders, or contact patients.”

### Visual direction

- Animate the pipeline one step at a time.
- Show a visible clinician approval checkpoint before export.
- If showing a screenshot, label the follow-up module “Simulation”.

### Transition

“A key question for evaluation is not only average accuracy, but consistency
across speakers and language-mix conditions. That motivates CEAS.”

---

## Slide 4 — CEAS Fairness

### On-slide content

**CEAS: a proposed equity-conscious robustness summary**

```text
CEAS = 100 × (
  0.50 × overall accuracy
  + 0.25 × worst-speaker accuracy
  + 0.25 × worst-code-switch-category accuracy
)
```

Accuracy component: `max(0, 1 − min(WER, 1))`

**Status today**

- Proposed project metric; not a validated score or exact reproduction of a
  published framework.
- Speaker assignments are missing.
- Code-switch labels are provisional.
- Therefore **CEAS is not currently calculable**.

### Speaker script

“A single overall WER can hide uneven performance. A model might look
acceptable on average while struggling for a particular speaker or language
mix.

We therefore define CEAS as a proposed project metric. It combines overall
WER-derived accuracy with the lowest observed speaker-group accuracy and the
lowest observed accuracy across adjudicated code-switch categories. The
weights shown here are our explicit proposal: 50 percent overall performance,
25 percent worst-speaker robustness, and 25 percent worst-category
consistency.

This is inspired conceptually by fairness-adjusted ASR scoring work, including
the framework attributed in our documentation to Rai and colleagues at
Interspeech 2025. It is not an exact reproduction or a validated clinical
metric.

Most importantly, we are not reporting a CEAS result today. The current
manifest does not include assigned speaker IDs, and its code-switch categories
are estimates from written script share that still need human confirmation.
References also need audio-aligned verification. Until those prerequisites
are met and subgroup coverage is adequate, the score remains unavailable.
Even then, CEAS would describe robustness across these benchmark labels; it
would not prove demographic fairness.”

### Visual direction

- Present the formula beside three component tiles: Overall, Speaker floor,
  Code-switch floor.
- Put “NOT CALCULATED — annotation prerequisites pending” in a prominent
  status badge.
- Do not display a fabricated number, gauge, or sample subgroup ranking.

### Transition

“With that evidence boundary in mind, here is what our evaluation pipeline
currently demonstrates—and what it does not.”

---

## Slide 5 — Evaluation Results

### On-slide content

**Evaluation status: pipeline exercised; clinical accuracy not established**

| Evidence item | Current status |
| --- | --- |
| Master manifest | 100 cases, CS-01 through CS-100 |
| Reference transcripts | Source-corpus text; audio verification pending |
| Speaker assignments | Not supplied in accessible source |
| Code-switch categories | Provisional; human confirmation pending |
| Mock pipeline run | 100 mock outputs per each of six configured adapters |
| WER, term recall, CEAS | N/A for mock-only / unverified evidence |

**Mock transcripts and simulated latency are not model-performance results.**

### Speaker script

“The benchmark has one active source of truth: the 100-case master manifest,
covering CS-01 through CS-100. It contains reference text and focus terms
mapped from the supplied corpus.

We have exercised the inference and reporting pipeline in mock mode across
the cases. That verifies that the manifest can drive the data flow, that
attempts can be recorded, and that reports can keep synthetic outputs separate
from measured latency. It does not tell us how well any model transcribes
clinical audio.

For that reason, the current report does not publish mock WER, medical-term
recall, or CEAS as model results. A complete live comparison still requires
approved audio for the cases, audio-verified and adjudicated references,
confirmed labels, and model outputs gathered under documented settings.

We have intentionally retired the conflicting legacy subset data rather than
mixing it with this master corpus. This keeps the evidence path clear even
though it means our validated performance results are currently unavailable.”

### Visual direction

- Show the current benchmark status table or the `BENCHMARK_RESULTS.md`
  summary.
- If showing generated plots, label mock-only charts as pipeline/test
  artifacts and note that accuracy is N/A.
- Do not show historical subset metrics as results for this manifest.

### Transition

“The next phase is therefore about evidence quality and readiness, not
inflating a score.”

---

## Slide 6 — Roadmap

### On-slide content

**Roadmap: from reproducible prototype to evidence-backed evaluation**

1. **Verify the corpus**
   - Confirm audio availability, provenance, consent, and de-identification.
   - Match each recording to its manifest case.
2. **Adjudicate annotations**
   - Audio-review references and clinical focus terms.
   - Assign de-identified speakers and confirm code-switch categories.
3. **Run paired model evaluation**
   - Freeze models, versions, settings, and normalization.
   - Report coverage, failures, WER, clinical-term and critical-term errors.
4. **Assess robustness**
   - Compute CEAS only when its subgroup and annotation gates are satisfied.
   - Publish subgroup counts and component scores alongside any composite.
5. **Strengthen operational safeguards**
   - Complete authentication/RBAC, auditability, retention/deletion, and
     deployment controls before identifiable-patient use.

**North star:** Useful clinical workflows with transparent evidence and human
oversight.

### Speaker script

“Our roadmap starts with data integrity. We need to verify which audio files
are available, confirm provenance and consent, ensure the audio matches each
case, and protect de-identified material appropriately.

Next, qualified reviewers need to verify the references against the audio and
adjudicate the medical terms. Speaker assignments and code-switch categories
must be based on evidence, not assumed from a project target or estimated
from text alone.

Once those prerequisites are in place, we can run a paired comparison using
the same eligible cases and frozen model settings, publish failures and
coverage alongside metrics, and inspect clinically important errors.

CEAS belongs after those steps. We will calculate it only when the subgroup
labels and denominators are adequate, and we will publish its components so
that the composite cannot conceal a weak subgroup.

Finally, the prototype’s review gates are not a substitute for production
controls. Authentication, role-based access, auditability, retention, and
deletion must be implemented and verified before identifiable patient data is
used.

AfriHealth AI’s goal is a useful clinical workflow supported by transparent
evidence and human oversight. Thank you.”

### Visual direction

- Show a five-stage roadmap with corpus verification first and CEAS later.
- Close with the product name, repository, and challenge alignment document.
- End on “Human oversight · Evidence before claims”.

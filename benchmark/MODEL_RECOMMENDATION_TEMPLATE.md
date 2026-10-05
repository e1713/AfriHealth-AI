# Model Recommendation (Template)

> Complete only after reviewing paired results, coverage, model versions, and
> clinical error cases. A benchmark recommendation is not clinical approval.

## Recommendation summary

- **Intended workflow:** TBD
- **Candidate model/version:** TBD
- **Evidence tier:** measured / partial / proposed
- **Recommendation:** advance for controlled evaluation / do not advance /
  insufficient evidence
- **Reviewer and date:** Pseudonymous reviewer ID / TBD

## Evidence table

| Dimension | Result | Evidence and sample count | Caveat |
| --- | --- | --- | --- |
| Amharic transcription | TBD | TBD | TBD |
| English clinical terms | TBD | TBD | TBD |
| Code-switch behavior | TBD | TBD | TBD |
| WER | TBD | TBD | TBD |
| Medical-term recall | TBD | TBD | TBD |
| Critical-term misses | TBD | TBD | TBD |
| Entity capture | TBD | TBD | TBD |
| Latency and availability | TBD | TBD | TBD |
| Privacy/deployment constraints | TBD | TBD | TBD |

## Strengths

- TBD, tied to measured evidence and paired case coverage.

## Weaknesses and safety-relevant errors

- TBD, include omissions, substitutions, negation, numbers/doses, and
  code-switch failures.
- List critical misses by count and category; do not expose identifiable case
  text.

## Code-switch performance

Report human-adjudicated token-level metrics by language and mixed spans.
Separate script-based estimates from audio-grounded annotation. Include the
number of reviewed tokens and ambiguous tokens.

## Production suitability

Address supported languages/dialects, model/version stability, data residency,
retention, consent, endpoint security, latency, failure handling, clinician
review, auditability, and cost. Default conclusion is **not suitable for
autonomous diagnosis or treatment**. A positive benchmark result alone is
insufficient for clinical deployment.

## Decision and next evidence

- **Decision:** TBD
- **Conditions:** TBD
- **Required follow-up validation:** TBD
- **Clinical owner approval:** pending / not applicable / documented separately

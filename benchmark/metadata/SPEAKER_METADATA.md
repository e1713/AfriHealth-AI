# Speaker Metadata (De-identified)

## Policy

The canonical ground-truth sheet provides five speaker labels and case-level
values. The repository exports replace those name-like labels with
`Speaker-01` through `Speaker-05`; the identity mapping is deliberately not
stored. The sheet's general `review_status=verified` supports transcript
review, but does not separately attest speaker identity or every case
assignment, so manifest `speaker_assignment_status` remains `pending_review`.

| Pseudonymous ID | Case assignments | Language/dialect | Recording conditions | Status |
| --- | --- | --- | --- | --- |
| Speaker-01 | Source mapping present; review pending | Not supplied | Not supplied | Pseudonymized source label |
| Speaker-02 | Source mapping present; review pending | Not supplied | Not supplied | Pseudonymized source label |
| Speaker-03 | Source mapping present; review pending | Not supplied | Not supplied | Pseudonymized source label |
| Speaker-04 | Source mapping present; review pending | Not supplied | Not supplied | Pseudonymized source label |
| Speaker-05 | Source mapping present; review pending | Not supplied | Not supplied | Pseudonymized source label |

## Collection requirements

When source documentation is available, record only metadata needed to assess
corpus coverage: pseudonymous speaker ID, case mapping, self-described
language/dialect where consented, recording context, microphone/channel
conditions, and annotation confidence. Keep the identity key separately with
restricted access, if one exists.

Do not place names, exact age, address, facility/clinician identifiers,
contact details, voiceprints, or other direct identifiers here. Do not infer
gender, ethnicity, age, accent, or demographic group from voice. Collect,
retain, or publish speaker-level data only with documented consent and
governance approval.

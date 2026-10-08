# De-identification Evidence Record

> Template only. Replace every bracketed placeholder with the result of a real case-specific assessment. Do not put names, identifiers, identity keys, full sensitive transcripts, or confidential findings in this repository.

## Record

- evidence_id: `[PLACEHOLDER: actual controlled de-identification review ID]`
- case_id: `[PLACEHOLDER: CS-01 through CS-100]`
- record_status: `[PLACEHOLDER: draft / reviewed / approved; do not infer approval]`
- source_record_locator: `[PLACEHOLDER: restricted repository locator]`
- audio_reviewed: `[PLACEHOLDER: yes/no, exact filename, SHA-256, and review scope]`
- transcript_reviewed: `[PLACEHOLDER: yes/no, transcript version/source and review scope]`
- identifiers_assessed: `[PLACEHOLDER: actual categories and applicable standard; include direct/indirect spoken and textual identifiers, and voice identifiability where applicable]`
- findings: `[PLACEHOLDER: actual findings and disposition/remediation; do not use a generic assertion]`
- method_or_standard: `[PLACEHOLDER: actual policy/standard and steps performed]`
- reviewer: `[PLACEHOLDER: authorized privacy reviewer role or ID]`
- review_date: `[PLACEHOLDER: YYYY-MM-DD]`
- limitations_or_conditions: `[PLACEHOLDER: actual residual risks, restrictions, or none with rationale]`
- case_audio_mapping: `[PLACEHOLDER: case ID, filename, and restricted mapping record]`

## Repository registration

- manifest field: `de_identified`
- evidence reference field: `de_identification_evidence_reference`
- expected reference shape: `evidence://<controlled-store>/<dataset-version>/de-identification/<case-id>/<actual-evidence_id>`
- proposed status after authorized review: `[PLACEHOLDER: true / false / unknown; only the responsible authority determines this]`

Pseudonymizing a speaker label or asserting that there is no patient-identifiable information is not, by itself, a completed audio/transcript de-identification review. The validator requires a non-empty reference for `de_identified=true`; it does not authenticate the review or its conclusions.

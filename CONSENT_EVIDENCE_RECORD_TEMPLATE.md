# Consent Evidence Record

> Template only. Replace every bracketed placeholder using the actual controlled record. Do not put participant names, signatures, contact details, or identity keys in this repository. An evidence record and locator must exist before the manifest status can be promoted.

## Record

- evidence_id: `[PLACEHOLDER: actual controlled consent-record ID]`
- case_id: `[PLACEHOLDER: CS-01 through CS-100]`
- record_status: `[PLACEHOLDER: draft / reviewed / approved; do not infer approval]`
- source_record_locator: `[PLACEHOLDER: restricted repository locator]`
- participant_agreement_basis: `[PLACEHOLDER: actual signed consent, or approved determination and its scope]`
- collection_date: `[PLACEHOLDER: YYYY-MM-DD; use the actual date]`
- reviewer: `[PLACEHOLDER: authorized reviewer role or ID]`
- review_date: `[PLACEHOLDER: YYYY-MM-DD]`
- approval_scope: `[PLACEHOLDER: recording/storage/research/benchmark purposes actually covered]`
- hosted_provider_scope: `[PLACEHOLDER: state whether external Intron/Sahara processing is explicitly covered; reference terms]`
- retention_statement: `[PLACEHOLDER: governing retention/deletion policy and applicable duration or event]`
- audio_or_case_mapping: `[PLACEHOLDER: case ID and restricted mapping to the covered recording]`
- restrictions_or_conditions: `[PLACEHOLDER: actual conditions; do not leave relevant restrictions implicit]`

## Repository registration

- manifest field: `consent_obtained`
- evidence reference field: `consent_evidence_reference`
- expected reference shape: `evidence://<controlled-store>/<dataset-version>/consent/<case-id>/<actual-evidence_id>`
- proposed status after authorized review: `[PLACEHOLDER: true / false / unknown; only the responsible authority determines this]`

The repository validator checks only that a `true` value has a non-empty reference. It does not validate this record's authenticity, participant mapping, consent scope, or legal sufficiency. A waiver or alternative basis requires an institutionally approved interpretation because the repository has no separate waiver status.

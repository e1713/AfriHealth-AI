# Hosted Inference Approval Record

> Template only. Replace every bracketed placeholder with the actual provider/institution record. Do not treat dataset-owner authorization for benchmark evaluation as provider-specific authorization unless the real record explicitly covers hosted transfer.

## Record

- evidence_id: `[PLACEHOLDER: actual controlled approval/authorization ID]`
- case_id: `[PLACEHOLDER: CS-01 through CS-100, or approved batch scope with explicit case mapping]`
- record_status: `[PLACEHOLDER: draft / reviewed / approved; do not infer approval]`
- provider: `[PLACEHOLDER: actual provider legal/service name, e.g. Intron; verify]`
- provider_service: `[PLACEHOLDER: actual API/service/endpoint covered]`
- approval_scope: `[PLACEHOLDER: exact audio/data categories, transfer, purpose, permitted processing, and conditions]`
- dataset_scope: `[PLACEHOLDER: dataset version and case IDs covered; link controlled case list]`
- reviewer: `[PLACEHOLDER: authorized institutional privacy/security/legal approver role or ID]`
- approval_date: `[PLACEHOLDER: YYYY-MM-DD]`
- effective_period: `[PLACEHOLDER: actual start/end or policy-defined validity]`
- consent_record_reference: `[PLACEHOLDER: actual consent/approved-basis record(s) and scope]`
- deidentification_record_reference: `[PLACEHOLDER: actual case review record(s)]`
- provider_terms_reference: `[PLACEHOLDER: actual agreement/data-processing terms covering retention, use, region, subprocessors, and deletion as required]`
- retention_and_deletion_conditions: `[PLACEHOLDER: actual provider/institution terms]`
- restrictions_or_conditions: `[PLACEHOLDER: actual limitations, or none with documented basis]`
- source_record_locator: `[PLACEHOLDER: restricted repository locator]`

## Repository registration

- manifest field: `hosted_inference_approved`
- evidence reference field: `hosted_inference_approval_evidence_reference`
- expected reference shape: `evidence://<controlled-store>/<dataset-version>/hosted-inference/<provider>/<case-id>/<actual-evidence_id>`
- proposed status after authorized review: `[PLACEHOLDER: true / false / unknown; only the responsible authority determines this]`

The importer/validator require consent and de-identification to be `true` with their own non-empty references before hosted approval can be `true`. They also require `audio_presence_status=verified_present`, audio-presence and checksum references, and a 64-hex-character SHA-256. Code validation does not establish that institutional/provider authorization is authentic, in force, or legally sufficient.

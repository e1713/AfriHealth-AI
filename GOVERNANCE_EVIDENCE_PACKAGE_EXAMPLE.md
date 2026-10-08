# Governance Evidence Package Examples

> **Illustrative placeholders only.** These examples are not evidence records, do not assert that records exist, and must not be copied into `approvals.csv` or the manifest as real references. Replace every `[PLACEHOLDER: ...]` with actual restricted-record details only after review. No status is promoted in this package.

## CS-01

### Consent record

- evidence_id: `[PLACEHOLDER: actual consent record ID for CS-01]`
- case_id: `CS-01`
- participant_agreement_basis: `[PLACEHOLDER: actual record and scope covering this recording and intended research/benchmark use]`
- collection_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- reviewer: `[PLACEHOLDER: authorized reviewer ID/role]`
- approval_scope: `[PLACEHOLDER: actual approved purposes; specify if Intron/Sahara external processing is covered]`
- retention_statement: `[PLACEHOLDER: actual retention/deletion rule and governing policy]`
- proposed `consent_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/consent/CS-01/<actual-consent-record-id>`
- manifest status: `unknown` until actual record and scope are reviewed

### De-identification record

- evidence_id: `[PLACEHOLDER: actual de-identification review ID for CS-01]`
- case_id: `CS-01`
- audio_reviewed: `[PLACEHOLDER: actual filename, checksum, scope, and result]`
- transcript_reviewed: `[PLACEHOLDER: actual transcript source/version and result]`
- identifiers_assessed: `[PLACEHOLDER: categories/standard actually assessed, including applicable spoken/voice risks]`
- findings: `[PLACEHOLDER: actual case findings and disposition]`
- reviewer: `[PLACEHOLDER: authorized reviewer ID/role]`
- review_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- proposed `de_identification_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/de-identification/CS-01/<actual-review-record-id>`
- manifest status: `unknown` until the actual case-linked assessment is reviewed

### Hosted Inference Approval record

- evidence_id: `[PLACEHOLDER: actual provider approval ID for CS-01]`
- case_id: `CS-01`
- provider: `[PLACEHOLDER: actual provider entity]`
- provider_service: `[PLACEHOLDER: actual service/endpoint]`
- approval_scope: `[PLACEHOLDER: actual transfer, purpose, data, conditions, and dates]`
- dataset_scope: `[PLACEHOLDER: approved dataset version and case-list record]`
- reviewer: `[PLACEHOLDER: authorized institutional approver ID/role]`
- approval_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- proposed `hosted_inference_approval_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/hosted-inference/<provider>/CS-01/<actual-approval-record-id>`
- manifest status: `unknown` until provider-specific authorization and dependencies are verified

## CS-02

### Consent record

- evidence_id: `[PLACEHOLDER: actual consent record ID for CS-02]`
- case_id: `CS-02`
- participant_agreement_basis: `[PLACEHOLDER: actual record and scope covering this recording and intended research/benchmark use]`
- collection_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- reviewer: `[PLACEHOLDER: authorized reviewer ID/role]`
- approval_scope: `[PLACEHOLDER: actual approved purposes; specify if Intron/Sahara external processing is covered]`
- retention_statement: `[PLACEHOLDER: actual retention/deletion rule and governing policy]`
- proposed `consent_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/consent/CS-02/<actual-consent-record-id>`
- manifest status: `unknown` until actual record and scope are reviewed

### De-identification record

- evidence_id: `[PLACEHOLDER: actual de-identification review ID for CS-02]`
- case_id: `CS-02`
- audio_reviewed: `[PLACEHOLDER: actual filename, checksum, scope, and result]`
- transcript_reviewed: `[PLACEHOLDER: actual transcript source/version and result]`
- identifiers_assessed: `[PLACEHOLDER: categories/standard actually assessed, including applicable spoken/voice risks]`
- findings: `[PLACEHOLDER: actual case findings and disposition]`
- reviewer: `[PLACEHOLDER: authorized reviewer ID/role]`
- review_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- proposed `de_identification_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/de-identification/CS-02/<actual-review-record-id>`
- manifest status: `unknown` until the actual case-linked assessment is reviewed

### Hosted Inference Approval record

- evidence_id: `[PLACEHOLDER: actual provider approval ID for CS-02]`
- case_id: `CS-02`
- provider: `[PLACEHOLDER: actual provider entity]`
- provider_service: `[PLACEHOLDER: actual service/endpoint]`
- approval_scope: `[PLACEHOLDER: actual transfer, purpose, data, conditions, and dates]`
- dataset_scope: `[PLACEHOLDER: approved dataset version and case-list record]`
- reviewer: `[PLACEHOLDER: authorized institutional approver ID/role]`
- approval_date: `[PLACEHOLDER: actual YYYY-MM-DD]`
- proposed `hosted_inference_approval_evidence_reference`: `evidence://<controlled-store>/<dataset-version>/hosted-inference/<provider>/CS-02/<actual-approval-record-id>`
- manifest status: `unknown` until provider-specific authorization and dependencies are verified

## Import reminder

These record examples are not an importer CSV. Do not change manifest statuses based on this example package. Once actual evidence is approved, enter its real locator in the evidence register and create the full importer CSV with the four verified audio fields preserved from the manifest. Follow `GOVERNANCE_RECORDS_REQUIRED.md` and `GOVERNANCE_REGISTRATION_CHECKLIST.md` before using `apply_governance_flags.py`.

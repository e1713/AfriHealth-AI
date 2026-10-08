# Governance Evidence Collection Checklist

This checklist maps each current governance gap to the evidence to collect, acceptable source, controlled storage destination, repository reference field, code validation dependency, and promotion dependency. It is for collection only: do not edit `approvals.csv` or the manifest while assembling evidence, and do not treat this checklist as evidence or approval.

## Current baseline

- Cases: CS-01 through CS-100 (100 records).
- Current `approvals.csv` and manifest: `consent_obtained`, `de_identified`, and `hosted_inference_approved` are `unknown`; their reference fields are blank.
- Audio baseline in the manifest: `audio_presence_status=verified_present`, audio-presence/checksum references populated, and SHA-256 values present. Recheck the exact file/hash before any hosted promotion.
- Current readiness: all three governance fields are `NOT_READY`.

## Collection checklist by requirement

### 1. Consent and participant agreement

**Collect for every case CS-01 through CS-100:**

- [ ] Actual signed participant consent record, linked through a restricted identity/case mapping; or an actual institutionally approved alternative/waiver with a formally approved interpretation for the repository's Boolean field.
- [ ] Record/source ID, issuer/collector, date, covered recording/case(s), and scope for collection, storage, benchmark research/evaluation, and any hosted provider processing.
- [ ] Verify consent scope explicitly permits transfer to Intron/Sahara if that case will be sent to the hosted service. Participation or internal evaluation permission alone may not authorize external processing.
- [ ] Reviewer confirms authenticity, participant/case mapping, intended-use scope, and any limits/expiry.

**Acceptable source:** Original signed form or controlled consent register; alternatively, a signed institutional ethics/governance determination accepted by the responsible authority. A dataset-owner statement or blank template is not, by itself, a participant record.

**Store original:** Approved restricted institutional records system, outside public Git. The institution must provide the actual store/path and access controls; none is specified in the repository.

**Register reference:** `GOVERNANCE_EVIDENCE_TEMPLATE.csv` -> `consent_evidence_reference`; future manifest destination: `benchmark/metadata/BENCHMARK_MANIFEST.csv` -> `consent_evidence_reference`.

**Reference shape:** `evidence://<controlled-store>/v1.0/consent/<case-id>/<actual-consent-record-id>`.

**Code dependency:** `validate_metadata.py` and `apply_governance_flags.py` accept only `true`, `false`, or `unknown`; `consent_obtained=true` requires a non-empty `consent_evidence_reference`.

**Promotion dependency:** Set `consent_obtained=true` only for cases the actual record covers. Keep `unknown` if the record, mapping, scope, or authorized interpretation is absent or unresolved.

### 2. De-identification / privacy review

**Collect for every case CS-01 through CS-100:**

- [ ] Completed review of the exact audio, corresponding transcript, and relevant metadata.
- [ ] Case ID, exact filename, SHA-256, source/version reviewed, method/standard, reviewer and date.
- [ ] Identifier categories assessed, including direct/indirect spoken or textual identifiers and voice-identifiability considerations where relevant.
- [ ] Findings, remediation/disposition, residual limitations, and reviewer sign-off.
- [ ] Reviewer's case-level outcome is explicitly linked to the recording and transcript versions.

**Acceptable source:** Signed case-level privacy/de-identification review; a dataset-wide report is acceptable only when it includes a verifiable case-by-case appendix covering all 100 exact assets. A generic owner assertion, pseudonymized speaker name, or text-only redaction description is insufficient by itself.

**Store original:** Approved restricted privacy/data-protection review repository, outside public Git. Keep identity crosswalks and any sensitive detail separately restricted.

**Register reference:** `GOVERNANCE_EVIDENCE_TEMPLATE.csv` -> `de_identification_evidence_reference`; future manifest destination: `benchmark/metadata/BENCHMARK_MANIFEST.csv` -> `de_identification_evidence_reference`.

**Reference shape:** `evidence://<controlled-store>/v1.0/de-identification/<case-id>/<actual-review-record-id>`.

**Code dependency:** `validate_metadata.py` and `apply_governance_flags.py` require a non-empty corresponding reference when `de_identified=true`.

**Promotion dependency:** Set `de_identified=true` only for cases with an approved review outcome tied to the exact audio/transcript. Use `false` when an authorized review establishes the case is not de-identified; otherwise retain `unknown`.

### 3. Hosted Intron/Sahara inference approval

**Collect for every case intended for hosted processing (currently all 100 are in scope for the benchmark plan):**

- [ ] Explicit authorization from the institution/data controller empowered to approve external data transfer; identify approving authority, reviewer, approval date, effective period, conditions, and covered case set/dataset version.
- [ ] Name Intron/Sahara and the exact service/API, benchmark purpose, audio/data categories, and processing/transfer scope.
- [ ] Applicable executed provider agreement/data-processing terms or formal institutional review of the terms, including use, retention, region/residency, subprocessors, and deletion obligations as required by policy.
- [ ] Link the applicable consent and de-identification records for the same case(s).
- [ ] Confirm the exact cleaned audio file is `verified_present` and its recorded SHA-256 matches the file.

**Acceptable source:** Signed institutional/data-controller authorization plus actual provider terms/contract or documented authorized review of applicable provider terms. A running API key, successful prior request, endpoint configuration, deployment description, benchmark-owner intent, or historical mock/test fixture is not hosted-inference approval.

**Store original:** Restricted institutional privacy/security/legal/contracts system, outside public Git. The approved record must explicitly identify the provider and covered dataset/cases. The repository provides no actual contract or authorization storage path.

**Register reference:** `GOVERNANCE_EVIDENCE_TEMPLATE.csv` -> `hosted_inference_approval_evidence_reference`; future manifest destination: `benchmark/metadata/BENCHMARK_MANIFEST.csv` -> `hosted_inference_approval_evidence_reference`.

**Reference shape:** `evidence://<controlled-store>/v1.0/hosted-inference/intron/<case-id>/<actual-approval-record-id>`.

**Code dependency:** Both scripts require `hosted_inference_approved=true` to have its own non-empty evidence reference; hosted approval also requires `consent_obtained=true` and `de_identified=true`. The flags importer additionally requires `audio_presence_status=verified_present`, audio-presence reference, checksum reference, and a 64-character hexadecimal SHA-256. The inference engine checks the actual cleaned audio hash before sending.

**Promotion dependency:** Set hosted approval to `true` only for covered cases after all consent, de-identification, audio-integrity, provider-terms, and institutional-approval requirements are met. Otherwise leave it `unknown` (or set `false` only if an authorized decision explicitly denies approval).

## Shared records and per-case mapping

A shared record may be referenced by multiple cases only if its signed scope or attached schedule explicitly covers each case and the relevant audio/version. A global index may combine links for efficiency, but it does not replace source records:

- Participant consent must map each recording to actual participant agreement(s) and their processing scope.
- A shared de-identification report must contain an outcome for every exact case/audio/transcript asset.
- A batch provider authorization may cover all 100 only if its dataset/version and case-list attachment explicitly include CS-01 through CS-100.

The repository requires a reference on each promoted row; do not use one broad reference on all rows unless the referenced source itself clearly covers all those rows.

## Safe registration and validation sequence

- [ ] Keep current `approvals.csv` and manifest unchanged while collecting evidence.
- [ ] Store originals in approved restricted repositories and record real stable IDs only after they exist; never invent reference IDs or leave placeholder tokens in import data.
- [ ] Complete the governance register for all case IDs; unresolved items remain `unknown` with blank references.
- [ ] Have an authorized reviewer verify source record authenticity, applicability, scope, dates, case mapping, and provider coverage.
- [ ] Build a separate importer CSV keyed by `case_id` with the seven governance fields **plus** the four current audio fields (`audio_presence_status`, `audio_presence_evidence_reference`, `audio_checksum_sha256`, `audio_checksum_evidence_reference`). Do not pass the seven-column template directly: the importer writes audio fields back to the manifest, so omitted columns may clear existing values.
- [ ] Independently check the importer input has exactly 100 unique IDs, CS-01 through CS-100, with no missing/extra/duplicate IDs. The importer itself does not enforce complete 100-case coverage or detect duplicate input IDs.
- [ ] Only after evidence review and authorization, the approved operator may run `.venv/bin/python apply_governance_flags.py /secure/path/full_verified_governance_flags.csv`, inspect the resulting manifest diff, and then run `.venv/bin/python validate_metadata.py`.
- [ ] A successful validator run confirms structural rules only; it does not authenticate evidence or create approval. Inference remains a separate later action after provider, credential, and governance readiness are confirmed.

## Readiness dashboard

| Field | Status | Current blocker |
|---|---|---|
| `consent_obtained` | **NOT_READY** | No actual consent/approved-alternative records or per-case references are present. |
| `de_identified` | **NOT_READY** | No completed case-linked or fully indexed 100-asset privacy review is present. |
| `hosted_inference_approved` | **NOT_READY** | No current provider-specific institutional authorization/terms reference is present; it depends on the first two fields and verified audio/checksum metadata. |

Do not change statuses or populate references from this checklist. It identifies the collection work only; approvals and manifest were not modified to prepare it, and no inference was run.

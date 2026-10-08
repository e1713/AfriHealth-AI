# Governance Evidence Population Plan

## Executive result

**Current promotion readiness: NOT_READY for all three fields across the 100-case benchmark.** The current `approvals.csv` and manifest contain `unknown` for `consent_obtained`, `de_identified`, and `hosted_inference_approved`; all corresponding evidence-reference cells are blank. The canonical ground-truth source does not contain these governance fields.

The owner-supplied facts (project-created recordings, participant agreement, no patient-identifiable information, transcript/alignment review, and owner authorization for benchmark evaluation) are relevant attestations. They have not yet been recorded as controlled, case-mapped evidence in the repository. Transcript review/alignment and owner authorization for benchmark evaluation do not, by themselves, establish consent scope for hosted transfer, a documented de-identification assessment, or provider-specific authorization.

## Evidence Inventory and Shortest Defensible Package

The repository does not require one standalone file per case. A compact package can use **three controlled records plus case-indexed coverage**:

1. **Consent register or source record set:** actual participant agreements (or an institution-approved basis) with an index mapping covered participant/recording to all applicable case IDs and recording versions. A single collection register can consolidate multiple consent forms; it cannot replace the underlying participant agreements with an unsupported owner assertion.
2. **Dataset de-identification report:** one signed report can cover the dataset if it contains a case-level appendix for all 100 exact files/transcripts, their filenames/checksums, review outcome, method, reviewer/date, findings, and disposition. One general statement without per-asset coverage is insufficient.
3. **Provider-specific hosted authorization:** one batch authorization can cover all 100 cases if it explicitly identifies Intron/Sahara and the actual service, evaluation purpose, data categories, exact covered case set/version, effective period, conditions, and applicable provider terms. If its scope excludes any case, use a separate valid authorization or leave that case unapproved.

For each case, the evidence register and eventual manifest still need a reference that resolves to the applicable entry/record. A shared record may be referenced repeatedly only when the record's documented scope explicitly covers each referenced case.

## Dataset-wide versus case-specific evidence

| Evidence | May one document cover all 100? | Case-specific requirement |
|---|---|---|
| Consent | **Conditionally.** A dataset-wide consent register may consolidate actual participant consents. A single blanket owner statement does not substitute for participant agreement or an approved alternative. | Every case must map to the participant agreement(s) covering its recording and to their actual scope. If consent scope differs, reference the applicable record separately. |
| De-identification | **Conditionally.** A shared assessment report/process may be used. | It must include a result for every exact audio/transcript asset, preferably indexed by case ID, filename, and SHA-256. A general “no identifiers” assertion without this coverage is not enough. |
| Hosted provider approval | **Conditionally.** One institutional authorization and provider-terms package may cover all cases as a batch. | The authorization must explicitly include this dataset version and all 100 case IDs (or a controlled, complete case-list attachment), the named Intron/Sahara service, purpose, and conditions. Any excluded case remains unapproved. |

## Evidence and reference structure

### Repository registration fields

The seven governance-register columns are:

```text
case_id
consent_obtained
consent_evidence_reference
de_identified
de_identification_evidence_reference
hosted_inference_approved
hosted_inference_approval_evidence_reference
```

Allowed status values are `true`, `false`, and `unknown`. Each `true` requires its corresponding non-empty reference.

The importer also requires these audio fields in its input:

```text
audio_presence_status
audio_presence_evidence_reference
audio_checksum_sha256
audio_checksum_evidence_reference
```

For hosted approval, the importer requires consent and de-identification `true`, audio status `verified_present`, non-empty audio presence/checksum references, and a valid 64-character hexadecimal SHA-256. The inference engine later checks that the actual cleaned audio bytes match the manifest checksum.

### Evidence record identifiers

Each source record should contain at minimum:

- Stable actual `evidence_id` assigned by the controlled evidence system.
- Dataset/version and applicable case ID(s); for media records also filename and SHA-256.
- Record type and decision/scope (consent, de-identification, or provider authorization).
- Issuing/recording authority, reviewer/approver, dates, and any effective period or restrictions.
- A controlled locator and an index linking the record to the exact covered cases.

Recommended reference convention (syntax only):

```text
evidence://<controlled-store>/<dataset-version>/<record-type>/<case-id>/<actual-record-id>
```

Example shapes only:

```text
evidence://<controlled-store>/v1.0/consent/CS-01/<actual-consent-record-id>
evidence://<controlled-store>/v1.0/de-identification/CS-01/<actual-review-record-id>
evidence://<controlled-store>/v1.0/hosted-inference/intron/CS-01/<actual-approval-record-id>
```

Do not register angle-bracket values, invented IDs, names, signatures, participant contact information, identity keys, or confidential record contents. Store original records in access-controlled institutional systems and put only their approved locators in the repository.

The repository accepts non-empty reference strings; it does not enforce this URI syntax, resolve the target, or prove authenticity/legal sufficiency. Human review of the actual source records is required.

## Promotion prerequisites by field

### `consent_obtained`

Promote a case only when its actual participant consent (or formally accepted alternative) is available, authenticated, and mapped to that recording/case. Verify that it covers the benchmark research/evaluation purpose and the relevant storage/processing scope. For hosted inference, the participant permission must cover the intended provider transfer or be supplemented by another valid approved basis. Populate the actual locator in `consent_evidence_reference` for every covered case.

Owner statement “participants agreed” may be documented as an owner attestation, but it is sufficient only if the responsible governance authority accepts it as a controlled record with actual basis, scope, authority, and case/participant mapping. It is not automatically equivalent to individual consent evidence.

### `de_identified`

Promote a case only after an authorized reviewer has assessed the exact audio and related transcript/metadata using the institutionally accepted method. The record must identify what asset/version was reviewed, reviewer/date, identifier categories assessed, findings, and remediation/disposition. Populate its actual locator in `de_identification_evidence_reference` for every covered case. A dataset-wide report is acceptable only with explicit case-by-case outcomes/asset mapping.

Owner statement “no patient-identifiable information exists” may be recorded as an attestation, but is not sufficient alone unless accepted by the responsible privacy authority and supported by the defined asset-level review. Pseudonymized speaker names and successful transcript alignment do not prove de-identification.

### `hosted_inference_approved`

Promote a case only when an authorized data controller/institution has approved sending that case's audio to the named Intron/Sahara service for benchmark evaluation, the applicable provider/data-processing terms have been reviewed, and the approval scope and period cover that case. Record the actual approval locator in `hosted_inference_approval_evidence_reference`. Consent and de-identification must already be `true` with their own references, and required audio evidence/checksum fields must pass.

Owner authorization for benchmark evaluation supports the benchmark purpose but does not by itself establish authority to disclose recordings to a third-party hosted provider. It can support provider approval only if the owner is the duly authorized data controller/approver and the controlled record explicitly covers provider transfer and applicable terms.

## Promotion readiness matrix

| Field | Current missing evidence | Evidence source needed | Promotion blocker | Current status |
|---|---|---|---|---|
| `consent_obtained` | Case-linked participant consent or accepted alternative; actual record references and scope are absent | Controlled participant consent records/consent register, or signed institutionally accepted determination, indexed to cases and purposes | Owner attestation is not yet a controlled, case-mapped record; consent scope for hosted processing must be established | **NOT_READY** |
| `de_identified` | Case-level review record and per-asset findings/references are absent | Signed privacy/de-identification assessment with 100 case/file/checksum outcomes | General owner claim and pseudonymized speaker labels do not demonstrate exact audio/transcript review | **NOT_READY** |
| `hosted_inference_approved` | Provider-specific institutional approval, actual provider terms, and case-set reference are absent | Approved Intron/Sahara authorization plus applicable DPA/terms and complete case-list scope | Requires consent and de-identification true/referenced for each case, verified audio/checksum metadata, and provider approval | **NOT_READY** |

## Required sequence of operations

1. In restricted storage, collect or index the actual participant agreements and establish which cases, purposes, and transfer scopes they cover.
2. Complete the dataset de-identification assessment with an explicit outcome and filename/checksum mapping for all 100 cases.
3. Obtain/review the provider-specific Intron/Sahara authorization and applicable data-processing terms; ensure the approval names the evaluation use and covers the intended case set.
4. Assign actual stable evidence IDs and create a case-to-record index. Replace placeholders in `GOVERNANCE_EVIDENCE_TEMPLATE.csv` only for reviewed cases. Leave unsupported cases `unknown`.
5. Have the authorized governance/privacy approver review reference resolution, scope, dates, case mapping, and evidence authenticity.
6. Build a separate full-schema importer CSV by joining the governance values/references to current manifest audio fields on exact `case_id`. It must contain exactly CS-01 through CS-100 once each. Do **not** pass the seven-column governance template directly to the importer: missing audio columns can overwrite current manifest audio data with blanks.
7. Only after approval, back up and review the planned change, run `apply_governance_flags.py` on that full-schema file, then run `validate_metadata.py`. Review the manifest diff and every remaining warning. A passing validator is structural validation, not an authorization decision.
8. Before any later inference, confirm per-case governance remains valid and the runner's actual audio checksum matches the approved manifest.

No importer or inference command was run to create this plan. `approvals.csv` and the manifest were not modified.

# Governance Records Required

## Scope and current status

This document describes repository requirements for registering per-case evidence for `consent_obtained`, `de_identified`, and `hosted_inference_approved`. It does not itself constitute evidence or authorize inference.

The active manifest and `approvals.csv` contain 100 cases. All three statuses are currently `unknown` for every case, with blank evidence references. The source CSV/XLSX contains transcript review fields but no governance evidence fields. Owner-reported facts (project-created recordings, participant agreement, no patient-identifiable information, manual transcript/alignment review, and owner authorization for benchmark evaluation) are relevant attestations, but no case-linked source-record identifiers are registered in the repository. Manual transcript/audio review does not by itself prove consent scope, de-identification, or third-party hosted processing approval.

## Exact repository fields

The governance-only registration columns are:

```text
case_id
consent_obtained
consent_evidence_reference
de_identified
de_identification_evidence_reference
hosted_inference_approved
hosted_inference_approval_evidence_reference
```

All status values must be `true`, `false`, or `unknown`. Each `true` requires its own non-empty evidence-reference field.

`apply_governance_flags.py` also expects these audio columns in its input:

```text
audio_presence_status
audio_presence_evidence_reference
audio_checksum_sha256
audio_checksum_evidence_reference
```

For `hosted_inference_approved=true`, the importer requires consent and de-identification to be `true`, `audio_presence_status=verified_present`, non-empty audio-presence and checksum references, and a 64-character hexadecimal SHA-256. `validate_metadata.py` enforces the corresponding value/reference/dependency rules and warns when statuses are not affirmatively documented. The inference engine additionally compares the actual cleaned audio bytes with the manifest checksum before hosted upload.

Neither importer nor validator enforces a URI grammar or verifies that referenced records are authentic, in scope, or legally sufficient. Presence in a reference field is not approval by itself.

## Required evidence by field

### Consent

For each case, retain a controlled record that identifies the actual consenting participant (using a restricted identity mapping), the recording/case covered, the consent date, the collecting authority, and the permitted purposes. The record or its linked approved policy must cover benchmark research/evaluation and the intended processing. If data will be sent to Intron/Sahara, the permission must cover that external/provider processing; general participation or internal benchmark consent alone may not cover it.

If a formally approved waiver or a documented determination that no participant consent is applicable is the basis instead, preserve that signed determination and get the schema/state representation approved by the responsible governance authority. Do not encode a waiver as `consent_obtained=true` unless that interpretation is formally authorized.

The repository stores only a controlled evidence locator in `consent_evidence_reference`, not the signed form or participant identifiers.

### De-identification

For each case, retain a privacy review record linked to the exact audio filename/checksum and associated transcript/metadata. It should identify the reviewer and date, method or standard applied, scope of inspection, findings, and remediation/disposition for direct and indirect identifiers. Where the approved method considers voice itself identifying, document how that risk was assessed and controlled. Pseudonymized speaker labels and an owner statement that no patient identifiers exist do not replace this case-linked assessment.

The controlled record locator goes in `de_identification_evidence_reference`.

### Hosted inference approval

For each case and the exact provider, retain authorization covering the transfer of the audio to Intron/Sahara for the stated benchmark purpose. Record the approving institution/authority, date, scope, provider, conditions, and linked data-processing/retention/residency terms. The record must be consistent with both the participant permission (or approved alternative) and the de-identification review.

The controlled record locator goes in `hosted_inference_approval_evidence_reference`. Owner authorization for benchmark evaluation is not automatically institutional authorization for external disclosure to a provider.

## Reference format

The code only requires non-empty strings; it does not enforce a URI pattern. Use a stable, access-controlled locator that resolves in the approved evidence store. A recommended format is:

```text
evidence://<controlled-store>/<dataset-version>/<record-type>/<case-id>/<actual-record-id>
```

Examples below show syntax only. Bracketed tokens are placeholders and must be replaced with real record IDs before registration:

```text
evidence://<controlled-store>/v1.0/consent/CS-01/<actual-consent-record-id>
evidence://<controlled-store>/v1.0/de-identification/CS-01/<actual-review-record-id>
evidence://<controlled-store>/v1.0/hosted-inference/intron/CS-01/<actual-approval-record-id>
```

Never use example IDs, guessed IDs, or references that do not resolve to the actual controlled record. Do not store names, signatures, contact details, identity keys, or sensitive form contents in the manifest or evidence map.

## Promotion prerequisites

Before any row is promoted:

1. An authorized governance reviewer verifies that each locator resolves and covers the exact case/audio asset and intended purpose.
2. Consent (or approved alternative), de-identification assessment, provider-specific hosted authorization, and applicable provider terms are checked for scope and dates.
3. The exact audio filename and SHA-256 in the evidence process match the cleaned WAV and manifest values.
4. The per-case flags CSV contains exact unique IDs `CS-01` through `CS-100`; missing, duplicated, or extra IDs are resolved before import.
5. The governance CSV is joined by `case_id` with the current manifest audio fields. Do not pass the seven-column governance-only template directly to the importer: omitted audio fields may be written back as blank.
6. The responsible authority approves the promotion; a structural validator pass alone is not approval.

After evidence review, the intended repository commands are:

```bash
.venv/bin/python apply_governance_flags.py /secure/path/full_verified_governance_flags.csv
.venv/bin/python validate_metadata.py
```

`apply_governance_flags.py` writes to the active manifest. Back up and review the resulting diff under the controlled change process. No commands above were run to promote records when this document was created.

# Governance Registration Checklist

Use this checklist with `GOVERNANCE_EVIDENCE_TEMPLATE.csv`, `GOVERNANCE_RECORDS_REQUIRED.md`, and `EVIDENCE_REFERENCE_MAP.csv`. It describes evidence collection and registration; it does not itself grant approval.


## 2. De-identification review

For every case CS-01 through CS-100:

- [ ] Review the exact raw/cleaned recording and associated transcript/metadata for direct and indirect identifiers.
- [ ] Document the review method/standard, case ID, audio filename and SHA-256, reviewer, review date, findings, and any remediation/disposition.
- [ ] Assess spoken identifiers and voice-related identifiability under the institution's applicable standard. A pseudonymous speaker label or a general owner assertion alone is not the case-specific review record.
- [ ] A qualified privacy/data-protection reviewer or authorized designee approves the review outcome.
- [ ] Store the review record in restricted evidence storage and enter only its stable reference in `de_identification_evidence_reference`.

Expected repository fields: `de_identified` and `de_identification_evidence_reference`.

## 3. Hosted provider authorization

For every case intended for Intron/Sahara hosted processing:

- [ ] Confirm consent scope permits the specific transfer to Intron/Sahara for benchmark evaluation.
- [ ] Confirm de-identification review applies to the exact audio and transcript version being sent.
- [ ] Obtain institution/data-controller authorization identifying Intron/Sahara, data categories, purpose, effective period, and the covered case set.
- [ ] Verify the applicable provider contract/data-processing terms, including retention, use, region/residency, subprocessors, and deletion/incident responsibilities, under institutional policy.
- [ ] The institution's authorized privacy/security/contract approver records the decision and scope in the restricted evidence store.
- [ ] Enter the actual decision record reference in `hosted_inference_approval_evidence_reference`.

Expected repository fields: `hosted_inference_approved` and `hosted_inference_approval_evidence_reference`. Hosted approval cannot be `true` unless consent and de-identification are also `true` with references.

## 4. Evidence identifiers and references

Use the controlled evidence repository's actual immutable or stable record ID. The repository accepts non-empty strings and does not validate URI grammar. Recommended convention:

```text
evidence://<controlled-store>/<dataset-version>/<record-type>/<case-id>/<actual-record-id>
```

Expected references per case:

```text
CS-01 consent:           evidence://<controlled-store>/v1.0/consent/CS-01/<actual-consent-record-id>
CS-01 de-identification: evidence://<controlled-store>/v1.0/de-identification/CS-01/<actual-review-record-id>
CS-01 hosted approval:   evidence://<controlled-store>/v1.0/hosted-inference/intron/CS-01/<actual-approval-record-id>
```

Apply the same case-specific form to CS-02 through CS-100. These are syntax examples only; angle-bracket placeholders are not valid record IDs. Do not create guessed IDs or place forms, signatures, names, participant contact details, identity keys, or confidential evidence in the repository.

## 5. Registration and checks

- [ ] Keep original consent, privacy reviews, provider decisions, and identity mapping in approved restricted storage.
- [ ] Fill the seven governance columns in `GOVERNANCE_EVIDENCE_TEMPLATE.csv`; leave state `unknown` and reference blank when a record is missing, ambiguous, out of scope, or not approved.
- [ ] Confirm every row maps to an actual case and exact recording; confirm all required evidence references resolve and cover the purpose/provider/date.
- [ ] Have a second authorized reviewer validate scope and references before import.
- [ ] Build a separate importer CSV keyed by `case_id` that includes the seven governance fields and all four audio fields (`audio_presence_status`, `audio_presence_evidence_reference`, `audio_checksum_sha256`, `audio_checksum_evidence_reference`) copied from the current manifest after verification. Never pass the seven-column template directly to the importer; the importer writes audio fields back and could blank them if omitted.
- [ ] Verify the importer CSV has each ID CS-01 through CS-100 exactly once, with no extra/missing cases and no unresolved placeholder strings.
- [ ] Only after human governance approval, run the importer and validator:

```bash
.venv/bin/python apply_governance_flags.py /secure/path/full_verified_governance_flags.csv
.venv/bin/python validate_metadata.py
```

- [ ] Review the manifest diff, validator errors/warnings, and referenced source records. The validator checks allowed states, non-empty evidence references, hosted-approval dependencies, and audio/checksum structure; it cannot authenticate evidence or determine legal sufficiency.
- [ ] Hosted execution additionally requires the inference runner's exact-file checksum match. A passing structural validation is not itself authorization to transmit data.

## Responsibility and storage summary

| Record | Record owner/provider | Reviewer/approver | Storage |
|---|---|---|---|
| Participant consent or approved alternative | Participant/authorized participant and collection lead; institutional records custodian retains it | Authorized ethics/governance reviewer | Restricted institutional records system; repository holds only a locator |
| De-identification review | Data custodian prepares the case/audio mapping and review packet | Privacy/data-protection reviewer or authorized designee | Restricted privacy evidence system; repository holds only a locator |
| Hosted Intron/Sahara authorization and provider terms | Dataset owner/data controller obtains the request and applicable provider terms | Authorized institutional privacy/security/legal approver | Restricted contracts/governance system; repository holds only a locator |
| Case-to-record index | Data custodian | Authorized governance reviewer | Restricted store separate from public benchmark files |

These roles are workflow recommendations; institutional policy determines the authorized persons and records. The supplied owner facts should be preserved as attestations or linked to their actual source records, not substituted for participant records, case-level review, or provider/institutional authorization.

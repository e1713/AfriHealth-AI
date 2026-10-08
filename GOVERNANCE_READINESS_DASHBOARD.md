# Governance Readiness Dashboard

## Overall status

**Hosted Sahara execution readiness: NOT_READY.** The current `approvals.csv` and `benchmark/metadata/BENCHMARK_MANIFEST.csv` each contain 100 unique cases. For every case, `consent_obtained`, `de_identified`, and `hosted_inference_approved` are `unknown`; all corresponding evidence references are blank. No case has evidence-backed hosted approval.

## 1. Evidence currently present

- **Case mapping:** The source/manifest cover CS-01 through CS-100.
- **Audio identity/integrity metadata:** The manifest records `verified_present`, audio-presence evidence references, checksum evidence references, and 64-character SHA-256 values for the cleaned WAVs. The live inference engine separately checks actual file bytes against the checksum before upload.
- **Transcript/audio review:** Repository notes describe manual transcript and alignment review as owner/source-attested. Reviewer identity, review dates, and underlying review logs are absent; this is not consent or de-identification evidence.
- **Owner statements:** Governance documents record the owner's statements about project-specific recordings, participant agreement, no patient-identifiable information, research intent, and evaluation authorization. These are contextual attestations, not currently registered case-linked source records.
- **Historical report:** `clinical_validation_report.json` describes a historical 15-case simulated validation activity. It does not supply per-case current approval records for the active 100-case benchmark or authorize current Intron uploads.
- **Configuration/integration:** Sahara/Intron endpoint and backend configuration exist. A configured endpoint or API key is not data-transfer authorization.

## 2. Evidence currently missing

- Actual participant consent records (or an institutionally accepted, formally documented alternative), linked to each applicable case and the scope of intended processing.
- Evidence that each participant's agreement covers external hosted processing by Intron/Sahara, if that processing is intended.
- A completed case-level de-identification/privacy assessment tied to the exact audio, transcript, filename, and checksum, including method, reviewer/date, findings, and disposition. A dataset-level report is acceptable only with explicit outcomes/mapping for every covered asset.
- Current institutional/data-controller authorization for Intron/Sahara hosted processing and the applicable provider/data-processing terms, with a complete case/dataset scope, purpose, effective period, and conditions.
- Stable locators to all of the above in the governance evidence-reference fields.

## 3. Validator dependencies

For each case, `validate_metadata.py` requires governance statuses to be `true`, `false`, or `unknown`. Each status set to `true` requires its corresponding non-empty reference:

| Status | Required reference |
|---|---|
| `consent_obtained=true` | `consent_evidence_reference` |
| `de_identified=true` | `de_identification_evidence_reference` |
| `hosted_inference_approved=true` | `hosted_inference_approval_evidence_reference` |

For hosted approval, the validator also requires consent and de-identification to be `true`, `audio_presence_status=verified_present`, checksum evidence, and a valid 64-character lowercase hexadecimal SHA-256. `apply_governance_flags.py` requires the same approval references and checks audio presence/checksum structure. The inference runner verifies that the cleaned audio bytes match the recorded checksum before upload.

These are structural checks only. The code does not resolve evidence locators, verify record authenticity or scope, or establish legal sufficiency. The importer also does not enforce complete/unique coverage of all 100 case IDs; that must be checked before import.

## 4. Promotion dependencies

1. Obtain and review the actual consent/approved-basis records, privacy assessments, and provider-specific authorization in their controlled source systems.
2. Confirm each record covers the exact case/audio/version and intended processing; a shared record is usable only for cases explicitly within its documented scope.
3. Create real stable evidence references and map them to each covered case. Leave unsupported cases `unknown` with blank references.
4. Build importer input keyed by `case_id`, containing all seven governance columns **and** the four current audio fields. Do not pass the seven-column governance template directly: the importer writes audio fields back to the manifest and omitted fields can be cleared.
5. Independently confirm the importer CSV has exactly CS-01 through CS-100 once each, no placeholders, and no missing or duplicate rows.
6. Only after authorized human review, run the importer and validator under the approved change-control process. Review the manifest diff and remaining warnings. Validation success does not itself authorize hosted processing.
7. Run hosted inference only after provider credentials and all per-case governance/audio gates are satisfied.

## 5. Case coverage status

| Coverage measure | Current result |
|---|---:|
| Expected case IDs | 100 (CS-01 through CS-100) |
| Unique IDs in `approvals.csv` | 100 |
| Unique IDs in manifest | 100 |
| Cases with consent status `true` and reference | 0 |
| Cases with de-identification status `true` and reference | 0 |
| Cases with hosted approval `true` and reference | 0 |
| Cases with all three governance statuses and references | 0 |

## 6. Readiness matrix

| Field | Status | Exact evidence still required |
|---|---|---|
| `consent_obtained` | **NOT_READY** | For every covered case: actual signed participant consent or formally approved alternative; participant-to-case/recording mapping in restricted storage; consent date, source/authority, and scope covering benchmark use and the intended processing; stable locator in `consent_evidence_reference`. If hosted processing is intended, scope must cover that transfer or a separately accepted basis must be documented. |
| `de_identified` | **NOT_READY** | For every exact audio/transcript asset: completed privacy/de-identification assessment with case ID, filename and SHA-256, method/standard, reviewer/date, identifier categories assessed, findings, remediation/disposition, and stable locator in `de_identification_evidence_reference`. A shared report must include a case-by-case appendix covering all applicable assets. |
| `hosted_inference_approved` | **NOT_READY** | In addition to consent and de-identification evidence above: current signed institutional/data-controller authorization naming Intron/Sahara and the exact service, benchmark purpose, covered dataset/version and cases, effective period, scope/conditions, and applicable provider data-processing terms; stable locator in `hosted_inference_approval_evidence_reference`. Preserve `verified_present` audio evidence and valid matching checksums. |

## Risk assessment

**High risk / blocked:** Hosted inference would transfer audio to a third-party provider while the manifest has no affirmative consent, de-identification, or provider-approval records. Owner statements and configuration do not remove this gap. Do not promote flags or send audio until actual evidence is reviewed and case coverage is proven. No statuses or references were changed to prepare this dashboard.

# Evidence Gap Report

## Executive finding

The four requested records are absent: `docs/GOVERNANCE_CASE_INDEX.md`, `docs/CONSENT_RECORD_001.md`, `docs/DEIDENTIFICATION_RECORD_001.md`, and `docs/HOSTED_INFERENCE_APPROVAL_001.md`. There are therefore no statements in those files to trace. The repository does contain governance policies, owner-attestation notes, templates, code gates, test fixtures, and a historical validation report, but the active 100-case consent/de-identification/provider-approval evidence references remain blank. No direct participant consent forms, completed case-level de-identification reports, or current provider/hosting authorization records were found.

**Bottom line:**

- The case range CS-01 through CS-100 is supported by the source and manifest.
- Manual transcript/audio-alignment review is documented as a supplied/source-attested process, but the reviewer, date, and underlying logs are absent.
- The owner statements about participant agreement and no patient-identifiable information exist as attestations in governance documentation, not as case-linked primary records.
- Intron integration/configuration exists. It is not provider authorization. The historical 15-case simulated-validation report is not authorization for the active 100-case corpus.
- Railway/Cloudflare appear in deployment guidance/configuration, not as hosting approvals.
- No repository artifact establishes collection dates 2026-10-01–2026-10-06 or a governance approval dated 2026-10-08.

## Search scope and limitations

A case-insensitive search covered repository text/config/data formats (Markdown, CSV, JSON, Python, JavaScript, HTML/CSS, XML, YAML, INI, notebook JSON, and related text), extracted document XML from the DOCX and XLSX, and searched 59 matching file paths plus the notebook match noted below. `.env` contents were excluded to protect secrets; WAV audio was not text-searched. DOCX/XLSX XML was searched. No PDF text extractor (`pdftotext`, PyMuPDF, pypdf, PyPDF2, or pdfminer) is installed; a printable-string search returned no governance hits, but that is not a complete search of the PDF's rendered text. The PDF therefore remains a search limitation.

Line numbers below refer to the current files. The excerpt is a representative exact matching line or phrase from each matching file; locations aggregate related matches. Repeated case rows in generated execution output are summarized as one span.

## Match inventory

| File and matching location(s) | Exact matching text | Category / evidence type | Evidentiary interpretation |
|---|---|---|---|
| `ARCHITECTURE.md` L50, L84, L87, L92, L109, L145, L147, L148, L166 | “FastAPI adds the server-side Authorization header and connects to Intron.” | Hosted inference / configuration and safety policy | Confirms integration design and safeguards; not provider authorization. |
| `BENCHMARK_CERTIFICATION_REPORT.md` L32, L38, L46, L50 | “Consent, de-identification, licensing, retention, and hosted provider approval are `unknown` for every record.” | All / audit report | Directly reports evidence gaps, not approvals. |
| `BENCHMARK_EXECUTION_READINESS.md` L5, L9, L10, L18, L23 | “Validation rejects manifest drift from canonical source, unsupported verification claims, and hosted approval without evidence.” | Hosted inference / readiness report | Documents a gate and states execution is blocked. |
| `BENCHMARK_METADATA_TEMPLATE.csv` L1 | `consent_obtained,consent_evidence_reference,de_identified,...,hosted_inference_approved,...` | All / template | Defines fields only; contains no case evidence. |
| `BENCHMARK_RESULTS.md` L12, L13, L35 | “Consent, de-identification, and hosted-inference approval are `unknown`.” | All / results report | Reports unresolved statuses; no supporting approval records. |
| `CHALLENGE_ALIGNMENT.md` L11, L13, L17, L30, L32, L37 | “Hosted inference is blocked until evidence-backed approvals are recorded.” | Hosted inference / policy summary | A gate statement, not approval. |
| `CLINICAL_RECORDING_PROTOCOL.md` L23, L25-L28 | “Before recording, obtain written consent for speech recognition evaluation, storage, and challenge benchmarking.” | Consent / protocol | Collection requirement; not proof that forms were signed or retained. |
| `CODESWITCH_READINESS_REPORT.md` L34 | “Consent, de-identification, and hosted-provider approval remain unknown; hosted inference stays blocked.” | All / readiness report | Confirms gaps. |
| `CONSENT_EVIDENCE_RECORD_TEMPLATE.md` L9, L11, L15 | “participant_agreement_basis: `[PLACEHOLDER: actual signed consent, or approved determination and its scope]`” | Consent / template | Placeholder structure only. |
| `DEIDENTIFICATION_EVIDENCE_RECORD_TEMPLATE.md` L1, L7, L9, L16, L24, L25, L28 | “Template only.” | De-identification / template | Requires case-level review fields; contains no completed review. |
| `DEMO_SCRIPT.md` L4, L58 | “for which consent and de-identification have been documented.” | Consent/de-identification / demo instruction | Describes a condition for demonstrations; no record is cited. |
| `DEPLOYMENT.md` L9-L11, L20-L32, L55-L59, L145 | “The frontend may be hosted on Cloudflare Pages.” | Hosting / deployment guidance | Documents architecture and recommendations, not an approval record. |
| `EVIDENCE_REFERENCE_MAP.csv` L1-L101 | `evidence://<controlled-store>/<dataset-version>/.../<actual-...-record-id>` | All / placeholder map | Format placeholders for 100 case IDs; explicitly not real evidence IDs. |
| `FINAL_SUBMISSION_GUIDE.md` L31, L51, L58-L60 | “Consent, de-identification, and hosted-inference approval remain...” | All / submission guidance | Reports unresolved status and describes requirements; no evidence record. |
| `GOVERNANCE_EVIDENCE_GUIDE.md` L7, L9, L21, L23, L27, L40-L42, L45, L55, L61-L62, L72, L77, L91, L93, L129, L136, L140, L142 | “The dataset owner has stated that the recordings were created for this project, participants agreed to participate...” | Consent/de-identification / owner attestation and workflow guide | Owner attestation is explicitly distinguished from case-linked evidence; not direct proof by itself. |
| `GOVERNANCE_EVIDENCE_PACKAGE_EXAMPLE.md` L3, L14, L19, L21, L29, L32, L34, L38, L41-L43, L54, L59, L61, L69, L72, L74, L78, L81-L83 | “Illustrative placeholders only.” | All / example template | Explicitly not evidence; no statuses should be promoted from it. |
| `GOVERNANCE_EVIDENCE_POPULATION_PLAN.md` L5, L7, L13-L15, L23-L25, L38, L40, L54, L62, L76-L77, L94, L96, L100, L102, L109-L110, L114-L116, L120, L123 | “Current promotion readiness: NOT_READY for all three fields...” | All / population plan | Summarizes current gaps and requirements, not primary evidence. |
| `GOVERNANCE_EVIDENCE_TEMPLATE.csv` L1 | `case_id,consent_obtained,consent_evidence_reference,...` | All / template | Registration fields only; current rows are placeholders/unknown. |
| `GOVERNANCE_RECORDS_REQUIRED.md` L7, L18, L20, L34, L36, L48, L50, L52, L54, L56, L58, L72-L73, L83, L87 | “All three statuses are currently `unknown` for every case, with blank evidence references.” | All / requirements document and owner-attestation summary | Documents current state and requirements; does not establish approvals. |
| `GOVERNANCE_REGISTRATION_CHECKLIST.md` L3, L6, L14, L16, L18, L23-L24, L27, L29, L43-L44, L51, L57, L64-L65, L72-L73, L76 | “It describes evidence collection and registration; it does not itself grant approval.” | All / checklist | Procedure only. |
| `GROUND_TRUTH_AUDIT_REPORT.md` L13, L31 | “The source has no consent, de-identification, licensing, retention, or hosted-inference approval fields.” | All / audit report | Directly identifies absent source fields; no affirmative evidence. |
| `GROUND_TRUTH_COVERAGE_REPORT.md` L28, L43 | “0/100 affirmative evidence” | All / coverage report | Directly reports no affirmative evidence in the active records. |
| `GROUND_TRUTH_VERIFICATION_REPORT.md` L24-L31, L37, L45-L46 | “Reviewer identity, review date, independent reviewer logs, adjudication records, and consent records were not supplied.” | Consent and review / source-attested historical report | Manual review is documented as supplied methodology; consent/reviewer records remain absent. |
| `HOSTED_INFERENCE_APPROVAL_TEMPLATE.md` L1-L3, L7-L22, L27-L31 | “Do not treat dataset-owner authorization for benchmark evaluation as provider-specific authorization...” | Hosted inference / template | Defines needed fields; no actual provider approval exists in this template. |
| `LIVE_INFERENCE_READINESS.md` L7, L16-L17, L26 | “Consent and de-identification ... `unknown` for all 100 rows; evidence references blank.” | All / readiness report | Current-state report; states inference is blocked. |
| `METADATA_AUDIT_REPORT.md` L5, L10, L18, L20-L22, L38-L39, L43, L48 | “The original manifest and `approvals.csv` asserted affirmative consent, de-identification, and hosted approval for all rows without evidence. Those fields have been reset to `unknown`...” | All / audit report | Explains why prior values are not evidence and confirms current gaps. |
| `MODEL_RECOMMENDATION.md` L6 | “This is a descriptive pipeline summary, not clinical approval...” | Approval / generated report | Explicitly not approval. |
| `README.md` L1, L3-L5, L25, L33, L154, L169, L172-L174 | “Consent, de-identification, and hosted-inference approval remain `unknown`.” | All / project documentation | Identifies current blocker. |
| `RESPONSIBLE_AI.md` L10 | “This is not comprehensive de-identification...” | De-identification / privacy limitation | Describes limited redaction; does not support a zero-PII or de-identification claim. |
| `STRATEGY_DOCUMENT.md` L48, L69 | “...a claim of clinical approval.” | Approval / product strategy | Scope limitation; no governance authorization. |
| `SUBMISSION_READINESS.md` L30-L31 | “Consent, de-identification, and hosted approval are unknown.” | All / readiness report | Confirms blocker. |
| `SUBMISSION_SUMMARY.md` L28-L29 | “Consent, de-identification, and hosted-provider approval remain unknown.” | All / submission summary | Confirms blocker. |
| `apply_governance_flags.py` L2, L11-L21, L29-L47, L77 | “Apply per-case governance approval flags from an external CSV to the manifest.” | All / implementation | Enforces non-empty references, consent/de-identification dependency, and audio evidence structure; cannot authenticate source records. |
| `approvals.csv` L1-L101 | Header defines the three flags and evidence-reference fields; rows contain `unknown` and blank references. | All / current ledger | Direct record of current status, not affirmative evidence. |
| `benchmark/BENCHMARK_LIMITATIONS.md` L38, L40 | “Manifest consent, de-identification, and hosted-use states are `unknown`...” | All / limitations | Confirms unresolved status. |
| `benchmark/BENCHMARK_PROTOCOL.md` L19-L20, L60-L61, L98, L103 | “Consent, de-identification, and hosted-inference approval are `unknown`.” | All / protocol | Policy requires evidence before hosted APIs; not itself evidence. |
| `benchmark/DATASET_CARD.md` L42, L80-L81, L125, L140 | “Consent, de-identification, and hosted-inference approval remain `unknown`.” | All / dataset card | Dataset metadata/limitations, not affirmative record. |
| `benchmark/MODEL_RECOMMENDATION_TEMPLATE.md` L4, L59 | “A benchmark recommendation is not clinical approval.” | Approval / template | Template only; no authorization. |
| `benchmark/README.md` L23, L58-L59 | “Consent, de-identification, licensing, retention, and hosted-inference approval remain unknown.” | All / benchmark documentation | Confirms gap and validation behavior. |
| `benchmark/REPRODUCIBILITY_GUIDE.md` L22-L23, L36-L37, L61, L71, L76, L86 | “Before hosted inference, verify consent, de-identification, source rights...” | All / procedure | Instructions only; no completed verification records. |
| `benchmark/SCORING_RUBRIC_ALIGNMENT.md` L9, L11 | “...consent and hosted-use approvals are unknown.” | All / challenge mapping | Summarizes state, not evidence. |
| `benchmark/metadata/BENCHMARK_MANIFEST.csv` L1-L101 | Governance fields are present; CS-01 and CS-100 rows show all three `unknown` and references blank. | All / current manifest | Direct evidence of current metadata state; not evidence to promote it. |
| `benchmark/metadata/SPEAKER_METADATA.md` L32 | “Collect, retain, or publish speaker-level data only with documented consent and governance approval.” | Consent / privacy policy | Requirement only; not case-level proof. |
| `benchmark/reporting/PRESENTATION_SLIDES.md` L158, L293 | “Confirm audio availability, provenance, consent, and de-identification.” | All / presentation checklist | Proposed future check, not completed evidence. |
| `clinical_validation_upload.py` L10, L71-L74 | `has_documented_hosted_inference_approval(row)` and “Hosted inference blocked...” | Hosted inference / implementation | Enforces gates; not approval. |
| `generate_benchmark_hypotheses.py` L39 | “live requires manifest approvals and provider keys.” | Hosted inference / CLI help | Configuration/gate text, not approval. |
| `generate_results_doc.py` L109 | “descriptive pipeline summary, not clinical approval...” | Approval / reporting code | Output disclaimer, not authorization. |
| `index.html` L101, L222, L834, L954-L960, L1134, L3572, L3675-L3683, L3723-L3725 | “Clinician Approval Required” | Approval / UI strings and fixtures | UI labels and mock data; not participant or provider approval. |
| `inference_engine.py` L29-L32, L57-L62, L352-L356 | Hosted approval requires consent/de-identification and evidence references; live run blocks unauthorized cases. | Hosted inference / implementation | Gate implementation; no approval record. |
| `main.py` L1028, L1803-L1834, L1913-L1978, L2345 | Intron key configuration, upload endpoint, sample approval check, and `INTRON_SYNC_UPLOAD_ENDPOINT`. | Hosted inference / configuration and implementation | Proves the integration/endpoint exists; not provider authorization or institutional approval. |
| `results/sahara_cs01_test.json` L21-L25 | Evidence-reference-present flags are `false`; test status is blocked. | Hosted inference / blocked execution artifact | Records that no CS-01 request was made; not authorization. |
| `results/sahara_execution_manifest.csv` L2-L101 | Per-case rows say statuses unknown and `skipped`; skip reason says hosted inference blocked. | All / generated execution audit | Negative execution record; no approval evidence. |
| `results/sahara_execution_summary.json` L13 | “Consent, de-identification, and hosted-inference approval are unknown for all 100 cases.” | All / generated summary | Current blocked-state summary; not approval. |
| `server.js` L59, L64 | Adds an `Authorization` header for its proxy route. | Hosted inference / configuration/code | Authentication plumbing only; not vendor or institutional authorization. |
| `tests/test_benchmark_docs.py` L73 | Asserts the hosted approval evidence reference is empty. | Hosted inference / test assertion | Test fixture/expected state, not approval. |
| `tests/test_inference_engine.py` L11, L179, L195, L204, L209, L211 | Tests `has_documented_hosted_inference_approval` with synthetic `approval://` strings. | Hosted inference / test fixtures | Mock values used to test code paths; not real approval IDs. |
| `tests/test_metadata_validation.py` L89-L90, L228-L239, L259-L264, L284-L322, L341-L370, L403-L408 | Tests expected missing-evidence warnings and rejects true without references. | All / test fixtures | Synthetic test data and validation expectations; not actual records. |
| `tests/test_safety.py` L589, L605, L637, L656 | Uses `approval://test/CS-01` and similar fake references in tests. | Hosted inference / test fixtures | Explicitly test-only strings; not evidence. |
| `validate_metadata.py` L49-L51, L377-L407, L455-L458 | Requires evidence references and hosted approval dependencies; warns when approvals are absent. | All / validator implementation | Structural checks only; does not verify the evidence itself. |
| `AfriHealth_Sahara_Benchmark.ipynb` Cell 9 | Uses an `Authorization` header with `INTRON_API_KEY`. | Hosted inference / notebook code | API authentication code; not authorization to transfer the active benchmark set. |

## Claim-by-claim assessment

| Claim | Repository finding | Classification |
|---|---|---|
| All participants signed consent forms | No signed forms or participant agreement records were found. The source has blank reviewer/review-date fields; governance flags and references remain unknown/blank. The recording protocol requires written consent, but that is a procedure, not proof it occurred. | **Unsupported as a record claim.** Owner statement is an attestation only. |
| Collection dates 2026-10-01 through 2026-10-06 | No collection-date field or matching dates were found. The source `review_date` and `duration_sec` fields are blank for displayed rows; the 2026-09-13 date in the clinical validation JSON is an evaluation date for a historical 15-case report, not a collection date. | **Unsupported.** |
| 100% of benchmark audio reviewed | The verification report states manual review/alignment was supplied for all 100 source rows, but reviewer identity, date, logs, and independent reproduction are absent. | **Partially supported as a source/owner attestation; not independently verified.** |
| Zero PII found | Owner-reported statement exists in governance documentation. No completed case-by-case PII review or documented de-identification audit was found. Policy says limited text redaction is not comprehensive de-identification. | **Partially supported as an owner attestation; not direct proof.** |
| Cases CS-01 through CS-100 covered | The active source/manifest contains the 100 IDs, and project docs identify that range. | **Directly supported for dataset case mapping only.** This does not imply governance authorization. |
| Intron Voice API authorization exists | Main code configures and calls the Intron endpoint. A historical report describes 15 simulated cases and states authorized use for benchmarking/error analysis, with 15 uploads. No actual authorization record or applicable approval covering the active 100 audio/checksum set was found. | **Integration directly supported; current 100-case authorization unsupported. Historical 15-case assertion is limited and not a substitute.** |
| Railway and Cloudflare hosting approval exists | Deployment documents describe/recommend Cloudflare Pages and a separate FastAPI service, with Railway PostgreSQL/start-command guidance. No hosting/security approval record was found. | **Architecture/configuration only; approval unsupported.** |
| Approval date 2026-10-08 | No approval-date record was found. Manifest/approvals schemas have no approval-date field. Template dates are placeholders. | **Unsupported.** |

## Limitations and conclusion

The four requested `docs/GOVERNANCE_*.md` source records are absent, so there are no statements in them to trace individually. The DOCX and XLSX embedded XML were searched. The PDF could not be text-extracted because no PDF parser is installed; `strings` found no governance text, but that is not a complete PDF search. `.env` was not read to avoid exposing secrets; WAV payloads are not text-searchable.

No repository artifact directly proves the requested consent signatures, collection-date range, zero-PII review, Intron authorization for the active corpus, Railway/Cloudflare approval, or 2026-10-08 approval date. The only broadly supported item is the CS-01–CS-100 dataset mapping; manual review and no-PII are owner/source attestations documented with audit-trail gaps. No files were modified by this audit.

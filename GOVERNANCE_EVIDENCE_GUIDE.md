# Governance Evidence Registration Guide

## Purpose and current state

Use `GOVERNANCE_EVIDENCE_TEMPLATE.csv` to register per-case evidence for the three governance fields consumed by `apply_governance_flags.py`. It is a worksheet, not evidence by itself. Do not promote a field merely because a reference string is present.

At template creation, all 100 cases are `unknown` for consent, de-identification, and hosted-inference approval, and all corresponding evidence references are blank. The canonical source contains no governance columns. The current manifest and `approvals.csv` likewise contain no affirmative evidence references. Keep those states unchanged until controlled records have been reviewed.

The dataset owner has stated that the recordings were created for this project, participants agreed to participate, no patient-identifiable information exists, and transcript/alignment review was completed. These statements are relevant owner attestations, but they are not yet case-linked records in the repository. In particular, participant agreement does not by itself show that consent covered transfer to Intron/Sahara, and an assertion of no patient identifiers does not document an audio-level de-identification review. Record the actual source record, scope, reviewer, and applicable asset/case mapping before promoting any status.

## Registration and importer schemas

`GOVERNANCE_EVIDENCE_TEMPLATE.csv` is a seven-column governance register keyed by `case_id`:

| Field | Required values / meaning |
| --- | --- |
| `case_id` | Exact benchmark ID, `CS-01` through `CS-100` |
| `consent_obtained` | `true`, `false`, or `unknown` |
| `consent_evidence_reference` | Non-empty when consent is `true`; locator for the actual consent record and its scope |
| `de_identified` | `true`, `false`, or `unknown` |
| `de_identification_evidence_reference` | Non-empty when de-identification is `true`; locator for the case-specific review record |
| `hosted_inference_approved` | `true`, `false`, or `unknown` |
| `hosted_inference_approval_evidence_reference` | Non-empty when hosted approval is `true`; must identify the provider and authorized use |

`apply_governance_flags.py` additionally expects these four audio fields in its input CSV:

| Field | Requirement when hosted approval is `true` |
| --- | --- |
| `audio_presence_status` | `verified_present` |
| `audio_presence_evidence_reference` | Non-empty reference to the current presence check |
| `audio_checksum_sha256` | Valid 64-character SHA-256 for the exact cleaned audio |
| `audio_checksum_evidence_reference` | Non-empty reference to the checksum computation |

**Do not pass the seven-column registration template directly to the importer.** The importer writes these four audio values back to the manifest; absent columns are treated as blank and would erase existing audio metadata. Build a separate full-schema import CSV by joining reviewed governance values to the current manifest's audio fields by `case_id`. Preserve the manifest's audio fields unless the files are re-verified. The template itself intentionally does not claim or copy audio-verification evidence.

## Evidence to register per case

Use one row for every case, CS-01 through CS-100. For each row, register:

1. **Consent:** An actual signed consent record, or another documented basis accepted by the institution and applicable policy. To set `consent_obtained=true`, the record must establish affirmative consent covering this recording and the intended research/benchmark use. If the record does not authorize hosted provider processing, it does not support that use. A waiver or synthetic-data determination is not itself affirmative consent; do not encode it as `true` without an approved policy/schema interpretation.
2. **De-identification:** A case-linked assessment of the exact audio and associated transcript/metadata, recording the method, reviewer, date, findings, and handling of identifiers. Pseudonymizing a speaker label alone does not establish that voice or spoken content is de-identified.
3. **Hosted inference:** Explicit authorization for the specific hosted provider (currently Intron/Sahara), audio transfer, benchmark purpose, and applicable retention/data-processing conditions. Record the institutional approver and the governing approval or contract reference. This must be in addition to documented consent and de-identification.
4. **Audio identity:** Confirm the registered filename and checksum identify the exact cleaned WAV covered by the evidence. The importer records evidence-reference presence; the live inference engine separately compares the file bytes with the manifest checksum.

Shared policy or approval documents may be referenced by multiple cases only when their scope explicitly covers each listed case. Keep signed forms, identity mappings, and other sensitive documents in approved restricted storage; store only controlled record locators here.

## Evidence-reference convention

The validator and importer do **not** enforce a URI syntax. They require non-empty references for `true` claims; they cannot verify that a reference resolves to genuine or sufficient evidence. Use the institution's controlled document-management locator where available. A recommended opaque convention is:

```text
evidence://<repository>/<dataset-version>/<record-type>/<case-id>/<record-id>
```

For example, the structure could be `evidence://afrihealth/v1.0/consent/CS-01/<actual-record-id>`. The angle-bracket value is a placeholder, not a usable evidence record. Do not copy example IDs such as `IRB-VERIFIED-2026` unless that exact record exists, is authentic, and applies to the case. Do not put names, signatures, contact information, or confidential form contents in this CSV.

The three reference fields for each case should resolve to the corresponding real record, for example:

```text
CS-01 consent:              evidence://afrihealth/v1.0/consent/CS-01/<actual-consent-record-id>
CS-01 de-identification:    evidence://afrihealth/v1.0/de-identification/CS-01/<actual-review-record-id>
CS-01 hosted approval:      evidence://afrihealth/v1.0/hosted-inference/intron/CS-01/<actual-approval-record-id>
```

Apply the same case-specific pattern for CS-02 through CS-100. These examples do not assert that such records currently exist; leave their template cells blank until their actual controlled record IDs are available.

## Promotion rules enforced by code

- Every governance value must be `true`, `false`, or `unknown`.
- Each field set to `true` must have its corresponding evidence-reference field populated.
- `hosted_inference_approved=true` requires both `consent_obtained=true` and `de_identified=true`, each with its evidence reference.
- Hosted approval also requires `audio_presence_status=verified_present`, audio-presence evidence, checksum evidence, and a syntactically valid SHA-256.
- The repository validator checks these conditions and source/manifest consistency. It does not authenticate the evidence record, assess its legal sufficiency, or establish that the evidence covers the selected provider and use.

## Controlled workflow

1. Keep an untouched copy of current `approvals.csv` and the manifest in the approved records environment. Do not edit those files while gathering evidence. Preserve the original signed participant consent or approved alternative, and create a per-case index mapping each case/audio checksum to its consent scope.
2. Populate one template row per case only from records reviewed by the responsible governance authority. Leave a field `unknown` when evidence is absent, ambiguous, out of scope, or not yet reviewed. Use `false` only when the record supports a negative determination.
3. Have a second authorized reviewer verify record locators, scope, provider, case mapping, and audio checksum. Do not infer consent from transcript review, audio presence, pseudonymization, benchmark intent, or dataset preparation.
4. After review, create a separate importer CSV with the seven reviewed governance columns plus all four audio columns copied from the current manifest by exact `case_id`. The following example refuses duplicate or missing IDs and preserves the manifest's current audio metadata; set `output_path` to an approved restricted location before use:

```python
import csv
from pathlib import Path

expected_ids = {f"CS-{number:02d}" for number in range(1, 101)}
governance_fields = (
	"consent_obtained",
	"consent_evidence_reference",
	"de_identified",
	"de_identification_evidence_reference",
	"hosted_inference_approved",
	"hosted_inference_approval_evidence_reference",
)
audio_fields = (
	"audio_presence_status",
	"audio_presence_evidence_reference",
	"audio_checksum_sha256",
	"audio_checksum_evidence_reference",
)


def read_by_case(path):
	with path.open(encoding="utf-8", newline="") as handle:
		rows = list(csv.DictReader(handle))
	by_case = {row["case_id"].strip(): row for row in rows}
	if len(by_case) != len(rows):
		raise ValueError(f"Duplicate case IDs in {path}")
	return by_case


registered = read_by_case(Path("GOVERNANCE_EVIDENCE_TEMPLATE.csv"))
manifest = read_by_case(Path("benchmark/metadata/BENCHMARK_MANIFEST.csv"))
if set(registered) != expected_ids or set(manifest) != expected_ids:
	raise ValueError("Evidence register and manifest must contain CS-01 through CS-100 exactly")

output_path = Path("/approved/restricted/location/full_verified_governance_flags.csv")
output_path.parent.mkdir(parents=True, exist_ok=True)
fields = ("case_id", *governance_fields, *audio_fields)
with output_path.open("w", encoding="utf-8", newline="") as handle:
	writer = csv.DictWriter(handle, fieldnames=fields)
	writer.writeheader()
	for case_id in sorted(expected_ids):
		row = {field: registered[case_id].get(field, "") for field in governance_fields}
		row.update({field: manifest[case_id].get(field, "") for field in audio_fields})
		writer.writerow({"case_id": case_id, **row})
```

Replace the example output location with an approved restricted path. Inspect the generated file and ensure the actual cited records have been reviewed. Do not alter `approvals.csv` as a substitute for evidence collection. Only then run the importer from the repository root:

```bash
.venv/bin/python apply_governance_flags.py /secure/path/to/full_verified_governance_flags.csv
.venv/bin/python validate_metadata.py
```

The first command updates `benchmark/metadata/BENCHMARK_MANIFEST.csv`; it is intentionally not run as part of template creation. Review the diff and validator output before any inference. A passing validator is a structural check, not governance approval. Hosted inference must remain blocked unless all required evidence is authentic, applicable, and independently approved.

## Current evidence inventory

- `approvals.csv`: 100 cases; all three statuses `unknown`; all three evidence-reference fields blank.
- `benchmark/metadata/BENCHMARK_MANIFEST.csv`: 100 cases; all three statuses `unknown`; all three evidence-reference fields blank.
- `benchmark/metadata/GROUND_TRUTH_SOURCE.csv` and `.xlsx`: contain transcript/review metadata but no consent, de-identification, or hosted-approval fields.
- `clinical_validation_report.json`: a historical 15-case simulated-validation report; it is not case-linked governance evidence for the active 100-case corpus or hosted Intron processing.
- `CLINICAL_RECORDING_PROTOCOL.md`, `RESPONSIBLE_AI.md`, and `benchmark/DATASET_CARD.md`: describe requirements and explicitly unresolved states; they are not completed case-level records.

Until applicable records are registered and verified, do not promote any field and do not run hosted inference.

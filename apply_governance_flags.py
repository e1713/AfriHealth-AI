#!/usr/bin/env python
"""Apply per-case governance approval flags from an external CSV to the manifest."""

import csv
import re
import sys
from pathlib import Path

def apply_governance_flags(manifest_path, flags_csv_path):
    """Apply per-case governance states only when positive claims cite evidence."""
    evidence_fields = {
        'consent_obtained': 'consent_evidence_reference',
        'de_identified': 'de_identification_evidence_reference',
        'hosted_inference_approved': 'hosted_inference_approval_evidence_reference',
    }
    audio_fields = (
        'audio_presence_status',
        'audio_presence_evidence_reference',
        'audio_checksum_evidence_reference',
        'audio_checksum_sha256',
    )
    flags = {}
    with open(flags_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row['case_id'].strip()
            states = {field: (row.get(field) or 'unknown').strip().casefold() for field in evidence_fields}
            evidence = {field: row.get(evidence_field, '').strip() for field, evidence_field in evidence_fields.items()}
            for field, state in states.items():
                if state not in {'true', 'false', 'unknown'}:
                    raise ValueError(f"{case_id}: {field} must be true, false, or unknown")
                if state == 'true' and not evidence[field]:
                    raise ValueError(f"{case_id}: {field}=true requires {evidence_fields[field]}")
            if states['hosted_inference_approved'] == 'true' and any(
                states[field] != 'true' for field in ('consent_obtained', 'de_identified')
            ):
                raise ValueError(f"{case_id}: hosted inference approval requires documented consent and de-identification")
            audio = {field: (row.get(field) or '').strip() for field in audio_fields}
            if states['hosted_inference_approved'] == 'true' and (
                audio['audio_presence_status'] != 'verified_present'
                or not audio['audio_presence_evidence_reference']
                or not audio['audio_checksum_evidence_reference']
                or re.fullmatch(r'[0-9a-fA-F]{64}', audio['audio_checksum_sha256']) is None
            ):
                raise ValueError(
                    f"{case_id}: hosted inference approval requires verified audio presence and checksum evidence"
                )
            flags[case_id] = {"states": states, "evidence": evidence, "audio": audio}

    # Update manifest
    rows = []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        for field in (*evidence_fields, *evidence_fields.values(), *audio_fields):
            if field not in fieldnames:
                fieldnames.append(field)
        for row in reader:
            case_id = row['case_id']
            if case_id in flags:
                for field in evidence_fields:
                    row[field] = flags[case_id]["states"][field]
                    row[evidence_fields[field]] = flags[case_id]["evidence"][field]
                row.update(flags[case_id]["audio"])
            rows.append(row)
    
    # Write back
    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Report
    approved_count = sum(
        1 for r in rows
        if r.get('hosted_inference_approved') == 'true'
        and r.get('hosted_inference_approval_evidence_reference', '').strip()
    )
    print(f"Applied governance flags: {approved_count} of {len(rows)} cases approved for hosted inference")
    return 0

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <path_to_governance_csv>")
        sys.exit(1)
    
    manifest_path = Path('benchmark/metadata/BENCHMARK_MANIFEST.csv')
    flags_csv = Path(sys.argv[1])
    
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}", file=sys.stderr)
        sys.exit(1)
    
    if not flags_csv.exists():
        print(f"ERROR: Governance CSV not found at {flags_csv}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(apply_governance_flags(manifest_path, flags_csv))

#!/usr/bin/env python
"""Apply per-case governance approval flags from an external CSV to the manifest."""

import csv
import sys
from pathlib import Path

def apply_governance_flags(manifest_path, flags_csv_path):
    """Update manifest with per-case consent, de-identification, and hosted-inference approval flags."""
    
    # Load flags from external CSV
    flags = {}
    with open(flags_csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            case_id = row['case_id']
            flags[case_id] = {
                'consent_obtained': row.get('consent_obtained', 'false').lower() == 'true',
                'de_identified': row.get('de_identified', 'false').lower() == 'true',
                'hosted_inference_approved': row.get('hosted_inference_approved', 'false').lower() == 'true',
            }
    
    # Update manifest
    rows = []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            case_id = row['case_id']
            if case_id in flags:
                row['consent_obtained'] = 'true' if flags[case_id]['consent_obtained'] else 'false'
                row['de_identified'] = 'true' if flags[case_id]['de_identified'] else 'false'
                row['hosted_inference_approved'] = 'true' if flags[case_id]['hosted_inference_approved'] else 'false'
            rows.append(row)
    
    # Write back
    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    # Report
    approved_count = sum(1 for r in rows if r['hosted_inference_approved'] == 'true')
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

#!/usr/bin/env python
"""Parse clinical case text from DOCX and extract per-case reference transcripts."""

import re
import csv
import sys
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

def extract_docx_text(docx_path):
    """Extract plain text from DOCX word/document.xml."""
    with ZipFile(docx_path, 'r') as zf:
        xml_content = zf.read('word/document.xml')
    root = ET.fromstring(xml_content)
    
    # Namespace for Word XML
    ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
    
    text_parts = []
    for t in root.findall('.//w:t', ns):
        if t.text:
            text_parts.append(t.text)
    
    return ''.join(text_parts)

def parse_cases(text):
    """Extract case ID and quoted clinical text from unstructured DOCX text."""
    # Pattern: CS-NN: "quoted text"
    pattern = r'CS-(\d{2,3}):\s*["\"](.+?)["\"]'
    matches = re.findall(pattern, text, re.DOTALL)
    
    cases = {}
    for case_num, quoted_text in matches:
        case_id = f"CS-{int(case_num):02d}"  # Normalize to CS-01, CS-02, etc.
        # Clean up HTML entities and extra whitespace
        cleaned = quoted_text.replace('&quot;', '"').strip()
        cases[case_id] = cleaned
    
    return cases

def update_manifest(manifest_path, cases):
    """Update source reference text and reset any prior review to pending."""
    rows = []
    with open(manifest_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        if 'reference_review_evidence' not in fieldnames:
            fieldnames.append('reference_review_evidence')
        for row in reader:
            case_id = row['case_id']
            if case_id in cases:
                row['reference_transcript'] = cases[case_id]
                row['reference_review_status'] = 'pending_review'
                row['reference_review_evidence'] = ''
            rows.append(row)
    
    with open(manifest_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    
    return len([case_id for case_id in cases if any(row['case_id'] == case_id for row in rows)])

def main():
    docx_path = Path('transcripts/AfriHealth_AI_Benchmark_Corpus_CS01_CS100.docx')
    manifest_path = Path('benchmark/metadata/BENCHMARK_MANIFEST.csv')
    
    if not docx_path.exists():
        print(f"ERROR: DOCX not found at {docx_path}", file=sys.stderr)
        return 1
    
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found at {manifest_path}", file=sys.stderr)
        return 1
    
    print("Extracting DOCX text...", file=sys.stderr)
    text = extract_docx_text(docx_path)
    
    print("Parsing case references...", file=sys.stderr)
    cases = parse_cases(text)
    print(f"Found {len(cases)} case references", file=sys.stderr)
    
    print("Updating manifest...", file=sys.stderr)
    updated = update_manifest(manifest_path, cases)
    print(f"Updated {updated} source transcripts; audio review remains pending", file=sys.stderr)
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

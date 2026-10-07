# Code-Switch Readiness Report

## Dataset Language Evidence

- Source language-pair field: `Amharic-English` for 100/100 cases.
- Text-script scan of canonical normalized transcript: 97 contain Ethiopic and Latin letters; 3 contain Latin letters only; 0 contain Ethiopic letters only.
- This scan is a reproducible script-presence heuristic, not human token-level language annotation. The source does not provide token labels or switch-boundary labels.
- Manifest code-switch categories remain provisional script-share estimates and require separate review.

## Clinical Code-Switch Examples

| Case | Excerpt from canonical normalized reference | Observation |
| --- | --- | --- |
| CS-01 | `ሕመምተኛው ... high-grade fever ... severe ሳል` | Amharic frame with English clinical terms |
| CS-03 | `... wheezing ... nebulization ...` | Amharic text with respiratory terms in English |
| CS-04 | `Dysuria እና lower abdominal pain ... urine analysis` | English symptom/test terms embedded in Amharic |
| CS-06 | `Fasting blood sugar ... Metformin 500mg BID ...` | English clinical terms, units, and medication details in Amharic text |

Ellipses indicate omitted portions of the source reference, not transcript corrections.

## Medical Terminology

The spreadsheet medical-entity field is populated for 100/100 cases. Splitting its comma/semicolon-delimited values yields 244 mention entries and 223 distinct exact strings. Frequent examples include Wheezing (3), Appendicitis (3), Nebulization (2), Dysuria (2), Chills (2), Malaria film (2), CBC (2), and Gestation (2). This is a surface-string count, not adjudicated entity recall or clinical criticality.

## Readiness Assessment

**Suitable for Amharic-English code-switch ASR benchmarking as a reference corpus, conditionally.** It has verified normalized reference rows and source-labeled Amharic-English coverage, with text examples demonstrating mixed-script clinical content. Before subgroup/code-switch accuracy claims, independently annotate token language, switch boundaries, uncertain/borrowed terms, and case categories from the audio. The 3 Latin-only references need review to confirm they belong in the Amharic-English code-switch benchmark. No model performance score is produced here.

## Limitations

- No token-level language labels, switch boundaries, inter-annotator agreement, or adjudication logs are present.
- The `language_mix` field is constant and does not quantify per-case Amharic/English proportions.
- Script-presence counts can misclassify borrowed words, numerals, abbreviations, or transliterations.
- Consent, de-identification, and hosted-provider approval remain unknown; hosted inference stays blocked.

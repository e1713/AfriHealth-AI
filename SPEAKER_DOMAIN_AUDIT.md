# Speaker and Domain Audit

## Summary

- Cases: 100.
- Speaker labels: 5 distinct pseudonyms; 100/100 rows populated.
- Speaker assignment status: pending independent review for 100/100. The source provides mappings, but its general transcript-review flag is not speaker-specific.
- Domain coverage: 100/100 rows populated; 73 distinct source domain labels.
- Missing speaker IDs: 0 in the canonical sheet.
- Missing domain values: 0.
- Reviewer/date audit metadata: blank for 100/100; no reviewer identity/date was supplied.

## Cases per Speaker

| Pseudonym | Cases |
| --- | ---: |
| Speaker-01 | 13 |
| Speaker-02 | 27 |
| Speaker-03 | 15 |
| Speaker-04 | 40 |
| Speaker-05 | 5 |

The distribution is imbalanced: Speaker-04 contributes 40% of cases, while Speaker-05 contributes 5%. Do not treat these pseudonyms as demographic groups or infer speaker attributes from voice.

## Domain Distribution

There are 73 exact domain strings across 100 rows:

| Cases per domain label | Number of distinct labels |
| ---: | ---: |
| 1 | 54 |
| 2 | 14 |
| 3 | 3 |
| 4 | 1 |
| 5 | 1 |

Most frequent labels are Obstetrics & Gynecology (OBGYN) (5), Endocrinology (4), Cardiology / Emergency (3), Hematology (3), and Infectious Disease / Pulmonology (3). The remaining labels are distributed across emergency/trauma, infectious disease, pediatrics, cardiology, renal, GI, dermatology, neurology, ENT, psychiatry, and other specialties, often as compound labels. Exact case-level labels are in the canonical CSV.

## Missing Metadata and Review Needs

- No speaker IDs or domain labels are missing from the source export.
- Reviewer name and review date are missing for all cases.
- No identity key is stored in the repository; source name-like speaker values were pseudonymized.
- The sheet does not include a separate reviewer attestation for speaker identity/case mapping. Verify the mapping through approved source records before subgroup metrics or CEAS.
- Clinical domain and entity values are source-provided and should receive qualified review for clinical correctness and criticality before safety-oriented scoring.

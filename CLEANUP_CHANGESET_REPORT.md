# Cleanup Changeset Report

## Branch and baseline

- Cleanup branch: `cleanup/product-separation`
- Base: `main` at `e385725d7eb3a21d9972ee5eeb24e5e10bf7aa36`
- The previous mixed local commit is preserved at `preserved/cleanup-product-separation-cb5d312` and is not an ancestor of this branch.
- The original benchmark/governance materials are excluded from this cleanup commit. The 84 earlier-added archive files listed below remain available on the preserved branch.

## Cleanup files included

Product-separation edits:

```text
.env.example
ARCHITECTURE.md
CHALLENGE_ALIGNMENT.md
CLEANUP_CHANGESET_REPORT.md
DEMO_SCRIPT.md
DEPLOYMENT.md
README.md
RESPONSIBLE_AI.md
STRATEGY_DOCUMENT.md
config.py
index.html
main.py
pytest.ini
tests/test_dashboard_content.py
tests/test_safety.py
docs/architecture/README.md
docs/decisions/README.md
docs/governance/README.md
docs/roadmap/README.md
```

The following 26 pre-existing, main-tracked benchmark-only files are moved under `archive/benchmark/` as part of cleanup. Their contents are the versions tracked on `main`:

```text
AfriHealth_Sahara_Benchmark.ipynb -> archive/benchmark/notebooks/AfriHealth_Sahara_Benchmark.ipynb
BENCHMARK_METADATA_TEMPLATE.csv -> archive/benchmark/datasets/BENCHMARK_METADATA_TEMPLATE.csv
BENCHMARK_RESULTS.md -> archive/benchmark/reports/historical/BENCHMARK_RESULTS.md
CLINICAL_RECORDING_PROTOCOL.md -> archive/benchmark/governance/reports/historical/CLINICAL_RECORDING_PROTOCOL.md
CLINICAL_REFERENCE_TRANSCRIPTS.csv -> archive/benchmark/datasets/CLINICAL_REFERENCE_TRANSCRIPTS.csv
FINAL_SUBMISSION_GUIDE.md -> archive/benchmark/governance/reports/historical/FINAL_SUBMISSION_GUIDE.md
PAGES_DEPLOYMENT_PATCH.md -> archive/benchmark/governance/reports/historical/PAGES_DEPLOYMENT_PATCH.md
SUBMISSION_READINESS.md -> archive/benchmark/governance/reports/historical/SUBMISSION_READINESS.md
TEAM_HANDOFF_CHECKLIST.md -> archive/benchmark/governance/reports/historical/TEAM_HANDOFF_CHECKLIST.md
afriswitch_asr_benchmark.py -> archive/benchmark/tools/afriswitch_asr_benchmark.py
afriswitch_import.py -> archive/benchmark/tools/afriswitch_import.py
benchmark_data/README.md -> archive/benchmark/datasets/benchmark_data/README.md
benchmark_data/inference_metadata.json -> archive/benchmark/datasets/benchmark_data/inference_metadata.json
benchmark_data/manifest.csv -> archive/benchmark/datasets/benchmark_data/manifest.csv
benchmark_report.json -> archive/benchmark/reports/historical/benchmark_report.json
benchmark_suite.py -> archive/benchmark/tools/benchmark_suite.py
clinical_validation_evaluator.py -> archive/benchmark/tools/clinical_validation_evaluator.py
clinical_validation_report.json -> archive/benchmark/reports/historical/clinical_validation_report.json
clinical_validation_upload.py -> archive/benchmark/tools/clinical_validation_upload.py
convert_benchmark_audio.py -> archive/benchmark/tools/convert_benchmark_audio.py
data/ground_truth_template.json -> archive/benchmark/datasets/ground_truth_template.json
evaluation_report_summary.json -> archive/benchmark/reports/historical/evaluation_report_summary.json
generate_benchmark_hypotheses.py -> archive/benchmark/tools/generate_benchmark_hypotheses.py
requirements-benchmark.txt -> archive/benchmark/tools/requirements-benchmark.txt
run_full_evaluation.py -> archive/benchmark/tools/run_full_evaluation.py
tests/test_benchmark_metrics.py -> archive/benchmark/tests/test_benchmark_metrics.py
```

## Excluded prior benchmark/governance files

These 84 files were additions in the pre-existing benchmark/governance changeset, not product-cleanup changes. They are deliberately absent from this branch and are preserved by the holding branch:

```text
archive/benchmark/datasets/benchmark_intake/AfriHealth_AI_Clinical_Ground_Truth_NEW.xlsx
archive/benchmark/docs/benchmarks/README.md
archive/benchmark/governance/reports/historical/ANNOTATION_QA_CLOSURE_RECORD.md
archive/benchmark/governance/reports/historical/ANNOTATION_QA_EVIDENCE_COMPLETION.md
archive/benchmark/governance/reports/historical/ANNOTATION_QA_SIGNOFF.md
archive/benchmark/governance/reports/historical/ARCHITECTURE_ALIGNMENT_REPORT.md
archive/benchmark/governance/reports/historical/ARCHITECTURE_CONFLICT_REPORT.md
archive/benchmark/governance/reports/historical/AUDIO_LINK_VALIDATION_PLAN.md
archive/benchmark/governance/reports/historical/AUDIO_VALIDATION_CLOSURE.md
archive/benchmark/governance/reports/historical/AUDIO_VALIDATION_SIGNOFF.md
archive/benchmark/governance/reports/historical/BENCHMARK_CONTAMINATION_AUDIT.md
archive/benchmark/governance/reports/historical/BENCHMARK_FULL_RESET_PLAN.md
archive/benchmark/governance/reports/historical/BENCHMARK_INVENTORY.md
archive/benchmark/governance/reports/historical/BENCHMARK_RESTART_DECISION.md
archive/benchmark/governance/reports/historical/BENCHMARK_RESTART_READINESS.md
archive/benchmark/governance/reports/historical/BENCHMARK_SOURCE_ACCEPTANCE_REPORT.md
archive/benchmark/governance/reports/historical/BENCHMARK_SOURCE_ACCEPTANCE_UPDATE.md
archive/benchmark/governance/reports/historical/BENCHMARK_SOURCE_REMEDIATION_CHECKLIST.md
archive/benchmark/governance/reports/historical/BENCHMARK_V2_DATA_DEPENDENCY_DECLARATION.md
archive/benchmark/governance/reports/historical/BENCHMARK_V2_ISOLATION_CERTIFICATION.md
archive/benchmark/governance/reports/historical/BENCHMARK_V2_REBUILD_PREREQUISITES.md
archive/benchmark/governance/reports/historical/BLOCKER_CLOSURE_ANALYSIS.md
archive/benchmark/governance/reports/historical/CLINICAL_COVERAGE_AUDIT.md
archive/benchmark/governance/reports/historical/CRITICAL_NUMBER_STANDARDIZATION_PLAN.md
archive/benchmark/governance/reports/historical/CURRENT_REPOSITORY_STATE.md
archive/benchmark/governance/reports/historical/DEPLOYMENT_ALIGNMENT_REPORT.md
archive/benchmark/governance/reports/historical/DOCUMENTATION_CONSISTENCY_REPORT.md
archive/benchmark/governance/reports/historical/DOCUMENTATION_UPDATE_PLAN.md
archive/benchmark/governance/reports/historical/ENTITY_ANNOTATION_GUIDE_DRAFT.md
archive/benchmark/governance/reports/historical/FINAL_ANNOTATION_CERTIFICATION.md
archive/benchmark/governance/reports/historical/FINAL_BENCHMARK_SOURCE_SIGNOFF.md
archive/benchmark/governance/reports/historical/FINAL_BLOCKER_RECONCILIATION.md
archive/benchmark/governance/reports/historical/FINAL_BLOCKER_STATUS.md
archive/benchmark/governance/reports/historical/FINAL_CERTIFICATION_REVIEW.md
archive/benchmark/governance/reports/historical/FINAL_GOVERNANCE_CERTIFICATION.md
archive/benchmark/governance/reports/historical/FINAL_GOVERNANCE_CLOSURE_REPORT.md
archive/benchmark/governance/reports/historical/FINAL_GOVERNANCE_VALIDATION.md
archive/benchmark/governance/reports/historical/FINAL_SOURCE_ACCEPTANCE_ASSESSMENT.md
archive/benchmark/governance/reports/historical/FINAL_SOURCE_BINDING_VALIDATION.md
archive/benchmark/governance/reports/historical/FINAL_TRACEABILITY_ASSESSMENT.md
archive/benchmark/governance/reports/historical/GOVERNANCE_EVIDENCE_REVIEW.md
archive/benchmark/governance/reports/historical/INTENT_ANNOTATION_GUIDE_DRAFT.md
archive/benchmark/governance/reports/historical/LEGACY_BENCHMARK_ARCHIVING_PLAN.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_ANNOTATION_ANALYSIS.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_DATA_QUALITY_AUDIT.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_GOVERNANCE_ALIGNMENT.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_INTAKE_REPORT.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_SCHEMA_AUDIT.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_SOURCE_ACCEPTANCE.md
archive/benchmark/governance/reports/historical/NEW_WORKBOOK_STATISTICS_AUDIT.md
archive/benchmark/governance/reports/historical/OFFICIAL_BENCHMARK_SOURCE_CERTIFICATION.md
archive/benchmark/governance/reports/historical/OFFICIAL_BENCHMARK_SOURCE_DECISION.md
archive/benchmark/governance/reports/historical/PHASE0_COMPLETION_REPORT.md
archive/benchmark/governance/reports/historical/PHASE0_EXECUTIVE_REPORT.md
archive/benchmark/governance/reports/historical/PHASE0_FINAL_ARCHITECTURE_DECISIONS.md
archive/benchmark/governance/reports/historical/PHASE0_IMPLEMENTATION_PLAN.md
archive/benchmark/governance/reports/historical/PHASE1A_REPORT.md
archive/benchmark/governance/reports/historical/PHASE1B_APPROVAL_PACKAGE.md
archive/benchmark/governance/reports/historical/PHASE1B_DEPENDENCY_MAP.md
archive/benchmark/governance/reports/historical/PHASE1B_ISOLATION_IMPACT.md
archive/benchmark/governance/reports/historical/PHASE1_BENCHMARK_ISOLATION_PLAN.md
archive/benchmark/governance/reports/historical/PHASE1_BENCHMARK_PRESERVATION_PLAN.md
archive/benchmark/governance/reports/historical/POST_RESET_EXECUTIVE_SUMMARY.md
archive/benchmark/governance/reports/historical/POST_RESET_GAP_ANALYSIS.md
archive/benchmark/governance/reports/historical/POST_RESET_STABILIZATION_PLAN.md
archive/benchmark/governance/reports/historical/PRODUCT_ALIGNMENT_REPORT.md
archive/benchmark/governance/reports/historical/PROJECT_INVENTORY.md
archive/benchmark/governance/reports/historical/PROJECT_STRATEGIC_BASELINE.md
archive/benchmark/governance/reports/historical/PUBLICATION_APPROVAL_ASSESSMENT.md
archive/benchmark/governance/reports/historical/PUBLICATION_RELEASE_DECISION.md
archive/benchmark/governance/reports/historical/REFERENCE_EVIDENCE_INVENTORY.md
archive/benchmark/governance/reports/historical/RELEASE_READINESS_ASSESSMENT.md
archive/benchmark/governance/reports/historical/SOURCE_GOVERNANCE_REQUIREMENTS.md
archive/benchmark/governance/reports/historical/STRATEGIC_DECISIONS_AUDIT.md
archive/benchmark/governance/reports/historical/TECHNICAL_DEBT_REGISTER.md
archive/benchmark/governance/reports/historical/WORKBOOK_ANNOTATION_AUDIT.md
archive/benchmark/governance/reports/historical/WORKBOOK_APPROVAL_BINDING_RECORD.md
archive/benchmark/governance/reports/historical/WORKBOOK_BENCHMARK_READINESS.md
archive/benchmark/governance/reports/historical/WORKBOOK_INTAKE_REPORT.md
archive/benchmark/governance/reports/historical/WORKBOOK_REMEDIATION_PLAN.md
archive/benchmark/governance/reports/historical/WORKBOOK_SCHEMA_AUDIT.md
archive/benchmark/governance/reports/historical/WORKBOOK_STATISTICS_AUDIT.md
archive/benchmark/legacy_benchmark/BENCHMARK_V1_MANIFEST.md
archive/benchmark/legacy_benchmark/README.md
```

The earlier worktree also contained a one-line change in `afriswitch_asr_benchmark.py` changing its install hint. That content change is excluded; the archived version in this cleanup is byte-for-byte the `main` version.

## Release guardrails

- No benchmark/governance additions from the older changeset are included.
- The 26 archived files above are relocations of files already tracked on `main`.
- `.github/workflows/deploy.yml`, PWA assets, and package/dependency manifests remain unchanged.
- The holding branch preserves the earlier mixed commit without altering its commit object.

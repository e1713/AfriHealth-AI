# Final Product Repository Audit

**Audited branch:** `cleanup/product-separation`  
**Audited commit:** `9565bb0221b8413b0bd8d11750e0f899f8bf82b4`  
**Base (`main`):** `e385725d7eb3a21d9972ee5eeb24e5e10bf7aa36`  
**Scope:** Active product source, tests, docs, deployment references, and the intentional `archive/` tree. No files from the protected workflow/PWA/dependency paths were changed.

## Executive result

The active product has no benchmark route, benchmark dashboard/tab, benchmark report or manifest loader, or benchmark scoring/provider implementation. The app imported successfully and registered 22 routes; required product routes were present, and no route containing “benchmark” was registered.

Remaining references are protective tests, deployment packaging safeguards, legacy local-file ignore rules, the changeset inventory, and historical files under `archive/benchmark/`. These are not live product benchmark functionality.

## Classification

| Classification | Finding | Action |
|---|---|---|
| `REMOVE_NOW` | None identified. | No removals warranted by this audit. |
| `KEEP_PRODUCT` | Negative route/UI regression assertions in tests; the deployment package safeguard preventing a `benchmark` directory from entering the Pages staging directory. | Retain. These references prevent regressions or accidental publication. The deployment workflow is protected. |
| `ARCHIVAL_REFERENCE` | 26 files under `archive/benchmark/`; benchmark history/path inventory in `CLEANUP_CHANGESET_REPORT.md`; old local benchmark-data ignore patterns in `.gitignore`. | Retain as historical preservation and local-data safeguards, not runtime dependencies. |
| `REQUIRES_MANUAL_REVIEW` | None required to continue product development. | If the archive or local ignore policy is ever removed, review the retained records and any locally supplied benchmark data first. |

## Active references and disposition

### Regression tests — `KEEP_PRODUCT`

- [tests/test_safety.py](/workspaces/AfriHealth-AI/tests/test_safety.py:86) asserts the benchmark API route is absent while checking that product routes remain registered.
- [tests/test_dashboard_content.py](/workspaces/AfriHealth-AI/tests/test_dashboard_content.py:89)–[tests/test_dashboard_content.py](/workspaces/AfriHealth-AI/tests/test_dashboard_content.py:91) asserts that the benchmark tab and endpoint are absent and that challenge alignment content has no benchmark wording.

These are intentional negative assertions, not benchmark functionality.

### Deployment and local-file safeguards — `KEEP_PRODUCT` / `ARCHIVAL_REFERENCE`

- [.github/workflows/deploy.yml](/workspaces/AfriHealth-AI/.github/workflows/deploy.yml:56) lists a directory named `benchmark` among directories blocked from the Pages staging package. It does not call or serve benchmark functionality; it prevents accidental publication. The workflow is protected and unchanged.
- [.gitignore](/workspaces/AfriHealth-AI/.gitignore:9)–[.gitignore](/workspaces/AfriHealth-AI/.gitignore:17) ignores local clinical-validation downloads and generated evaluation outputs. No corresponding `clinical_validation` directory was found at the audited workspace depth. The rules are non-runtime and are retained as safeguards for local data.

### Changeset record — `ARCHIVAL_REFERENCE`

- [CLEANUP_CHANGESET_REPORT.md](/workspaces/AfriHealth-AI/CLEANUP_CHANGESET_REPORT.md) documents the prior benchmark/governance work, its exclusion from the cleanup commit, and the 26 tracked benchmark artifacts relocated into the archive. Its benchmark terms are inventory/history, not product claims or code dependencies.

## Archived benchmark references — `ARCHIVAL_REFERENCE`

All 26 files in the archive are classified as preserved historical artifacts, not active product dependencies:

```text
archive/benchmark/datasets/BENCHMARK_METADATA_TEMPLATE.csv
archive/benchmark/datasets/CLINICAL_REFERENCE_TRANSCRIPTS.csv
archive/benchmark/datasets/benchmark_data/README.md
archive/benchmark/datasets/benchmark_data/inference_metadata.json
archive/benchmark/datasets/benchmark_data/manifest.csv
archive/benchmark/datasets/ground_truth_template.json
archive/benchmark/governance/reports/historical/CLINICAL_RECORDING_PROTOCOL.md
archive/benchmark/governance/reports/historical/FINAL_SUBMISSION_GUIDE.md
archive/benchmark/governance/reports/historical/PAGES_DEPLOYMENT_PATCH.md
archive/benchmark/governance/reports/historical/SUBMISSION_READINESS.md
archive/benchmark/governance/reports/historical/TEAM_HANDOFF_CHECKLIST.md
archive/benchmark/notebooks/AfriHealth_Sahara_Benchmark.ipynb
archive/benchmark/reports/historical/BENCHMARK_RESULTS.md
archive/benchmark/reports/historical/benchmark_report.json
archive/benchmark/reports/historical/clinical_validation_report.json
archive/benchmark/reports/historical/evaluation_report_summary.json
archive/benchmark/tests/test_benchmark_metrics.py
archive/benchmark/tools/afriswitch_asr_benchmark.py
archive/benchmark/tools/afriswitch_import.py
archive/benchmark/tools/benchmark_suite.py
archive/benchmark/tools/clinical_validation_evaluator.py
archive/benchmark/tools/clinical_validation_upload.py
archive/benchmark/tools/convert_benchmark_audio.py
archive/benchmark/tools/generate_benchmark_hypotheses.py
archive/benchmark/tools/requirements-benchmark.txt
archive/benchmark/tools/run_full_evaluation.py
```

No archive file is imported by the product application or included as a product runtime dependency. The benchmark-named archive test is outside the active `tests/` tree and is excluded from product test execution.

## Required-file findings

- `main.py`, `index.html`, and `config.py`: no live benchmark route, UI, score computation, provider adapters, or benchmark-data loading was found.
- Product documentation (`README.md`, `ARCHITECTURE.md`, `DEPLOYMENT.md`, `RESPONSIBLE_AI.md`, `STRATEGY_DOCUMENT.md`, `docs/`, challenge/demo docs): no obsolete product-facing benchmark feature claims or broken local links were identified.
- Product tests contain only the negative assertions described above.
- Broad case-insensitive substring searches for `WER`/`CER` can match unrelated words such as “however” or “certification”; those are not metric references. The classification above uses whole-word matching and direct source inspection.

## Validation evidence

- Git: branch and commit matched the stated audit target; `main` remained at its original base; worktree was clean before report creation; protected paths had no staged or unstaged changes.
- Import/startup: `main` and `config` imported; Python compilation passed.
- Routes: 22 routes registered; required product routes passed; no benchmark route was registered.
- Frontend: `index.html` parsed; 106 IDs and 8 local references were checked; no missing local references or benchmark navigation/panel IDs were found.
- Documentation: 33 relative and absolute local Markdown links checked; none were broken.
- Product tests: 41 tests passed across `tests.test_safety`, `tests.test_dashboard_content`, and `tests.test_edge_persistence`.

Existing Starlette/httpx deprecation and temporary-file resource warnings appeared during tests; they did not fail the suite.

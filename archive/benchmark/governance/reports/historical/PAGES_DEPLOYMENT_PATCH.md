# Pages Deployment Patch

**Status at report creation:** Implemented locally; no Pages deployment had run for this patch.
**Goal:** Upload only browser runtime assets to GitHub Pages and fail the workflow if the staged tree contains unapproved files, protected directories, disallowed data extensions, or symlinks.

## Files Copied into `_site/`

The workflow stages exactly these six files:

| Path | Use |
|---|---|
| `index.html` | Web app entry point. |
| `assets/logo.svg` | Page logo. |
| `manifest.json` | Pre-cached by the service worker. |
| `sw.js` | Registered service worker. |
| `offline-sync-worker.js` | Offline queue Web Worker. |
| `pcm-processor.js` | Audio worklet module. |

`_site/` is generated during the workflow and ignored by Git via `/_site/`; no duplicate checked-in frontend tree is required. The page's links to local repository Markdown and test files now point to GitHub URLs. The direct benchmark-manifest CSV link was removed, so those documents, tests, and data do not need to be copied into the deployment.

## Excluded from the Artifact

The workflow does not copy any repository directories wholesale. The allowlist rejects these directories anywhere inside `_site/`:

- `raw_audio/`
- `cleaned_audio/`
- `benchmark/`
- `transcripts/`
- `docs/`
- `governance/`

It also rejects files ending in `.wav`, `.csv`, `.xlsx`, `.xls`, `.pdf`, or `.docx`; rejects every symlink; requires `assets/` to be the only subdirectory; and requires the file set to equal the six-file allowlist exactly. Other repository content, including `.env.example`, code, tests, results, and governance materials, is not copied into `_site/`.

## Workflow Diff

The workflow now stages and verifies the public site before upload, and changes the artifact path from `.` to `_site`:

```diff
       - name: Setup Pages
         uses: actions/configure-pages@v4

+      - name: Stage frontend-only site
+        shell: bash
+        run: |
+          mkdir -p _site/assets
+          cp index.html manifest.json sw.js offline-sync-worker.js pcm-processor.js _site/
+          cp assets/logo.svg _site/assets/
+
+      - name: Verify Pages allowlist
+        shell: bash
+        run: |
+          python3 - <<'PY'
+          from pathlib import Path
+
+          site = Path("_site")
+          expected = {
+              "index.html",
+              "manifest.json",
+              "sw.js",
+              "offline-sync-worker.js",
+              "pcm-processor.js",
+              "assets/logo.svg",
+          }
+          expected_directories = {"assets"}
+          blocked_directories = {
+              "raw_audio",
+              "cleaned_audio",
+              "benchmark",
+              "transcripts",
+              "docs",
+              "governance",
+          }
+          blocked_extensions = {".wav", ".csv", ".xlsx", ".xls", ".pdf", ".docx"}
+          if not site.is_dir():
+              raise SystemExit("Pages staging directory _site/ is missing")
+
+          paths = list(site.rglob("*"))
+          symlinks = [
+              path.relative_to(site).as_posix()
+              for path in paths
+              if path.is_symlink()
+          ]
+          blocked = [
+              path.relative_to(site).as_posix()
+              for path in paths
+              if path.is_dir() and path.name in blocked_directories
+          ]
+          blocked.extend(
+              path.relative_to(site).as_posix()
+              for path in paths
+              if path.is_file() and path.suffix.lower() in blocked_extensions
+          )
+          actual = {
+              path.relative_to(site).as_posix()
+              for path in paths
+              if path.is_file()
+          }
+          actual_directories = {
+              path.relative_to(site).as_posix()
+              for path in paths
+              if path.is_dir() and not path.is_symlink()
+          }
+          if blocked or symlinks or actual != expected or actual_directories != expected_directories:
+              print("Blocked paths:", sorted(blocked))
+              print("Symlinks:", sorted(symlinks))
+              print("Unexpected directories:", sorted(actual_directories - expected_directories))
+              print("Missing files:", sorted(expected - actual))
+              print("Unexpected files:", sorted(actual - expected))
+              raise SystemExit("Pages artifact violates the frontend allowlist")
+          PY
+
       - name: Upload Artifact
         uses: actions/upload-pages-artifact@v3
         with:
-          path: '.'
+          path: _site
```

The workflow source contains expanded diagnostics for blocked paths, symlinks, unexpected directories, missing files, and unexpected files.

## Security Rationale

The previous `path: '.'` packaged repository content, including all four protected data directories. The new job constructs the upload tree only from an explicit list, rejects unexpected content before upload, and prevents the Pages tar step from following symlinks to files outside that list. The service worker, manifest, PCM worklet, offline worker, and logo remain available at their existing relative paths.

## Dry-Run Validation

- Workflow YAML parsed successfully; both `run` blocks passed `bash -n`.
- The local staging and allowlist steps completed successfully.
- `_site/` contains exactly six files: `index.html`, `assets/logo.svg`, `manifest.json`, `sw.js`, `offline-sync-worker.js`, and `pcm-processor.js`.
- Local HTML reference scan found **0 broken references** within `_site/` after repository-only links were redirected or removed.
- A local HTTP smoke test returned **HTTP 200** for `index.html`, `sw.js`, `manifest.json`, `pcm-processor.js`, `offline-sync-worker.js`, and `assets/logo.svg`.
- The current `approvals.csv` and `benchmark/metadata/BENCHMARK_MANIFEST.csv` have no tracked changes. No audio, benchmark, transcript, or governance files were edited.
- No manual GitHub Actions run or Pages deployment was triggered for this patch; a push to `main` triggers the configured workflow. No inference or scoring was run.

## Remaining Deployment Risks

- At report creation, the previously deployed root-wide artifact remained live. The Pages security fix takes effect only after this change is pushed and the new Pages run succeeds.
- The workflow change only removes data from the Pages artifact. If the repository itself is public, tracked audio, benchmark data, and transcripts may still be available through GitHub repository browsing or clone/download.
- Prior Pages artifacts, browser caches, CDN caches, or downloaded copies may persist. Review them and follow incident/takedown procedures where exposure is confirmed.
- HTML links to documentation and tests now point to the repository's `main` branch. Those pages remain governed by repository visibility and may expose repository content outside the Pages artifact.
- Tailwind, Font Awesome, Chart.js, and Google Fonts remain external frontend dependencies; this patch does not add a content-security policy or self-host those resources.
- The API/backend and its live speech-data handling are unchanged. This deployment patch does not satisfy governance approval or authorize real model testing.
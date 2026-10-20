# Phase 36 — Tested recovery, source privacy guardrails and controlled family-access cutover

**Date:** 19 October 2026 (US Eastern)  
**Existing deploy verified before work:** Phase 35 commit `427867375db9691e3ce11e98cf768bc7605a6149` is `live` in Render service `Beverage-Family`. GitHub repository `csully1234/Beverage-Family` is **public**; Render is linked to `main` with auto-deploy disabled. No open PRs before this phase.

## Why this is the highest priority

The family-site password currently gates the Streamlit interface but **cannot protect public GitHub history and raw repository contents**. The public source includes living-family records and the complete 305-page, ~22.9 MB authorized digital edition of Lowell P. Beveridge Jr.'s *The Colony*. The copyright permission supplied by the user applies specifically to the family website, not unlimited public redistribution. The repository also includes a `LEGACY_COMPATIBILITY_PASSWORD` fallback in tracked application code. No existing login secrets are printed or changed in this work.

`.streamlit/config.toml` currently enables Streamlit static file serving. A file reachable through a direct static URL may bypass Streamlit's application-level password screen; **the actual anonymous book asset URL has not yet been manually tested**. Moving the repository to private alone would therefore not establish end-to-end confidentiality. Prior public clones or cached copies will not be recalled by a future visibility change.

## Delivered in Phase 36

### Verified recovery instead of an unchecked ZIP

Existing `tools/create_release_backup.py` snapshots tracked site code, genealogy data, original-research notes, the authorized book and tests, but the previous workflow stored its ZIP for just **14 days** without a restore test.

New `tools/verify_release_backup.py` checks every archive entry against the embedded SHA-256 manifest, validates archived file sizes and manifest inventory, rejects duplicate paths, forbidden filenames, traversal/absolute paths, POSIX symbolic links, encryption and oversized archives. It also optionally verifies every byte against the checked-out release and safely restores only into an empty dedicated directory.

GitHub Actions now performs the restore drill **after** successful tests, checks the recovered app, people index and full book PDF are present, and uploads both the backup and its small verification report. Requested artifact retention increases to **90 days**, subject to GitHub repository/organization maximum retention. The workflow fails closed rather than publishing a ZIP that has not survived validation.

**Limitations:** This is a short-to-medium-term **GitHub-hosted** recovery copy, not an independent off-site backup. It contains the same public-source data; it excludes Render environment settings, offline court scans, untracked files, Git commit history, and third-party archives. An off-platform encrypted backup retained under family control remains essential for true long-term preservation. Tests do not prove that any external archival link remains reachable.

### Guardrail against newly tracked credentials

`tools/privacy_audit.py` checks Git-tracked paths for common secret/private source files: `.env`, `secrets.toml`, private scans, `id_rsa`, `.key`, `.pem`, database backups, service-account credentials and similar. Dummy `.streamlit/secrets.toml.example` is explicitly allowed. It checks the AST for the family-login call occurring **before** archive-data load in the Streamlit main path. No credential value is inspected or printed.

`.gitignore` is extended to prevent common private files, scan directories and the local backup output directory from being casually added. **Gitignore is not a security control for already tracked or previously committed material**, and file-name checks do not catch private content hidden in ordinary JSON/Markdown. Existing source exposure is explicitly flagged as a warning, not magically marked resolved.

### Automated release gates

The regular Python 3.12/3.13 validation adds the filename/login privacy check; the post-merge backup workflow verifies the snapshot and performs a test restore before upload. New tests cover tampering, mismatched release content, hidden malicious ZIP members, duplicate entries, path traversal, denied overwrite, ordinary source files, and the live app's login call order.

## Current state and explicit nonchanges

- **No password, Render environment variable, GitHub visibility, static-asset route, or deployment credential was modified.**
- No removal, republication, rewriting, or re-licensing of *The Colony* PDF.
- No genealogy profile, evidence citation, original probate image, relative address, or Boston Tea Party claim was changed.
- No attempt to treat a publicly committed file as private simply because it has a UI password.
- All site sections remain accessible to logged-in family visitors under the **same login arrangement**.

## Coordinated privacy migration — separate change requiring owner approval

**Gate A — Prepare a recoverable baseline.** Confirm the new 90-day verified snapshot was produced and downloaded to encrypted offline storage under family control. Check that all original materials and 305 book pages are present. Record the current Render live commit, have a rollback route, and schedule a time for the switch.

**Gate B — Verify production auth secret without sharing it in chat or logs.** Confirm Render `APP_PASSWORD` exists through authorized dashboard checks. Keep the current visitor password functional throughout the transition. Rotate the hardcoded fallback once a secret-managed login has been verified; prevent reintroduction in future commits. Do not paste the current or new password into source code, a chat message or GitHub PR.

**Gate C — Close direct asset exposure.** Move copyrighted book and family-only document serving off Streamlit's unauthenticated static directory or implement a verified authenticated asset delivery path, including direct URL tests from a fresh unauthenticated browser. Simply making GitHub private will not close potential public Render static asset URLs.

**Gate D — GitHub visibility and Render integration.** After reviewing permissions and access needs, turn the repo private, verify that the GitHub App/integration still authorizes Render to fetch private source, and perform a controlled redeploy with a known-good rollback. Check Actions backup permissions/retention and ensure family visitors can still log in without individual GitHub accounts.

**Gate E — Repair lingering exposure.** Review repository and fork history and external copies. Publicly available Git objects/clones are not retroactively deleted by setting private. Plan legacy password rotation and any notices after assessing who could previously read the files. Preserve legal author credits, restoration hashes and historical evidence.

## Verification after this PR is merged

1. Confirm Python 3.12/3.13 regression, release audit, privacy guard and JavaScript family-tree/map checks pass.
2. Merge the checked SHA, then confirm post-merge **Verified source backup (main)** succeeds, including the **restore drill** and 90-day retention setting.
3. Deploy only after CI is green to the existing Render service with `autoDeploy=no`, and confirm `live` with the expected merge SHA.
4. Test that the old family login works; all trees, person evidence, timeline, 305-page book and photo index remain available to authorized family visitors.
5. Confirm the repository remains intentionally public until a separate, reviewed visibility/authentication cutover. **This phase is a safety foundation, not the full privacy migration.**

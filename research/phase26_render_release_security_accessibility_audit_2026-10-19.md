# Phase 26 — Render production, mobile usability, access and archive-integrity audit

**Audited:** 19 October 2026  
**Production:** [Beverage-Family on Render](https://beverage-family.onrender.com), workspace `My Workspace` (`csullivan@logoitup.com`).  
**Service:** `srv-d4ku3lhr0fns738dmsbg`  
**Baseline:** GitHub `main` merge commit `72c1fba3fd320e94db3c6b77586d1a0845dd718d` (Phase 25, PR #45).

## Confirmed production state

Render's service API reports **live** for deploy `dep-dbb6g1ajnfac73f5oqjg`, running the exact Phase 25 merge commit above. The matching GitHub `main` workflow completed successfully on Python 3.12 and 3.13. This proves the code was deployed and a process started; it **does not** independently establish that every authenticated click or phone layout works in the actual visitor browser.

Render's service is in Oregon on the free plan and is **not suspended**. `autoDeploy` is **disabled**. Future GitHub merges require a deliberately triggered Render deployment. Available Render application logs reported successful install, Streamlit startup and an Uvicorn listener on port 10000. A sampled error-level log query returned no errors; that is not a full history or a proof of zero runtime exceptions. Render's sampled HTTP latency and request-count metrics were empty for the selected window. These limits should be preserved in any external status statement.

The secured Streamlit experience was tested previously through `streamlit.testing.v1.AppTest`, not through an independently logged-in phone/browser connected to production. Readable `/_stcore/health` and the live URL could not be fetched by the available public HTTP inspection mechanisms; the service API is the primary production verification source here.

## Original media availability

The **305-page optimized *The Colony* PDF** is **already checked into** `static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf` on GitHub `main`. File size is **22,944,649 bytes**. This corrects an old README instruction saying it still needed uploading. The CI release audit now opens the actual PDF with PyMuPDF and requires page count to equal the manifest's 305.

The archive contains editorial metadata on 31 received Waldo probate scan copies (30 unique hashes). **No images from that probate-office ZIP have been uploaded to the publicly readable repository**, since their reuse permission was not confirmed. The local `data/media_manifest.json` contains no approved miscellaneous historical image entries; if images appear through the family book, they come from that distinct already-authorized book PDF, not the unrelated image manifest.

A **public GitHub repository and its static PDF URLs are not private file storage**, even when the Streamlit interface requires a family password. Avoid uploading unlicensed or sensitive copies to the repository.

## Code changes

- Full-family custom component now clamps the tall SVG explorer to the viewport on narrow screens, recalculating when the screen rotates or the window resizes; desktop retains its existing height and interactivity.
- Better mobile line wrapping, minimum-width handling for cards and horizontal layouts, **44px touch targets**, and clear keyboard focus outlines.
- Citation routing rejects non-HTTP(S), URL-credential, malformed-port, script, data and whitespace-injected destination strings instead of rendering dangerous links.
- Family-book fallback messages and README now describe **deployment availability**, not a binary that's still supposedly missing from GitHub.
- Offline `tools/release_audit.py` verifies that every expected book file is present, that the page count matches source metadata, that source routes correspond to the app's page table and that only approved local images are presented as available. It does not test arbitrary outside archive URLs; those can change independently.
- `tools/create_release_backup.py` creates a versioned, checksum-indexed ZIP of **tracked public code, data, research files, source images, and book PDF**, intentionally excluding Render variables, untracked probate scans and local secrets. The final `main` validation now uploads a 14-day GitHub Actions backup artifact for recovery. Repository Git history remains the permanent code record.

## Required security cutover — **not yet executed**

`app.py` currently contains a **hardcoded legacy password fallback** in public source code. This is a real access-control weakness. The Render connector supports **updating** environment variables but does not expose a **read** action for existing variables. Therefore we cannot determine from this API whether the production `APP_PASSWORD` is already configured.

**Do not blindly remove the fallback and merge/deploy**: if there is no configured Render password, legitimate relatives could be locked out. Equally, setting a surprise replacement password could disrupt family access. Correct production rollout:

1. Owner chooses a fresh, strong unique family password, coordinates its change with permitted visitors, and sets **`APP_PASSWORD`** in the Render service **Environment** settings (without putting its value in GitHub).
2. Verify a fresh browser can log in with that new password and the older hardcoded one no longer works; keep a separate admin recovery record.
3. Remove the legacy fallback from Python, change a missing password to an explicit closed configuration state, and add tests that production cannot accept a known default password.
4. Re-run tests, merge once, manually deploy (autoDeploy is off), verify credentials and links, and watch errors. Do not print secrets in CI artifacts.

This is intentionally marked an **open release blocker** for full authentication hardening rather than falsely claiming that passwords were rotated.

## Manual browser/device verification still needed

- Verify at 375px and 430px widths: login, homepage primary choices, People dropdown, Matthew and Clarissa exhibits, zoom/pan/tap the full-family SVG, returning to Focused Tree while preserving selection, person timeline and original-citation links.
- Open a book page with a user-held login, check page count 305, printed caption and zoomed scanned image; verify unapproved probate scans are not served as pretend original files.
- Test on one larger tablet or desktop, including keyboard-only focus progression. Automation validates route state but cannot prove screen-reader operation.
- During the next rollout, verify the new **manual** Render deployment uses the exact merged commit SHA and reaches status `live`, then confirm affected pages through actual browser sessions.

## Rollback and recovery

The current known-good production deployment is `dep-dbb6g1ajnfac73f5oqjg` at commit `72c1fba3...`. GitHub tracks all historical and research files. A release snapshot artifact is created after the new version passes `main` CI. A failed Phase 26 rollout should revert the merge commit or redeploy the known-good revision through Render's deployment controls, then verify logins and navigation. The Render connector's available deployment trigger deploys **current main**, not a historic SHA, so older-version rollback cannot be honestly claimed via that trigger alone.

**Publication boundary:** no genealogy, relative residential addresses, Boston Tea Party claim, book copyright marker, or probate image rights flag were changed.

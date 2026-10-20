# Phase 37 — Close the predictable family-book static URL without changing login

**Date:** October 19, 2026 (US Eastern); implementation commits may have UTC timestamps on October 20.  
**Base:** Phase 36 complete tracked-site recovery snapshot, merge `a6710ee90773451bb8cd73b8c72b17f27b9fa0e2`, verified live in Render before beginning this work.  
**Project:** `csully1234/Beverage-Family`, public repository, Render service `srv-d4ku3lhr0fns738dmsbg`.

## What was exposing the book

1. `.streamlit/config.toml` explicitly set `[server] enableStaticServing = true`. Official Streamlit documentation says this serves `./static` under `/app/static/[filename]`, regardless of the Streamlit app's `check_password()` UI. This is a **public static-file pathway**, not a family-authenticated book endpoint.
2. `family_books.py` created the exact book URL ending `/app/static/books/The_Colony_Lowell_Beveridge_2016_Web_Optimized.pdf#page=...`; the reader embedded it in an `st.iframe` and offered an external new-tab link. The name is guessable and is present in the public repository.
3. This was especially concerning because the user's reproduction permission is for the **family website**, not unbounded redistribution. The raw **GitHub repository remains public**, and files previously publicly retrievable could have been copied independently.
4. An automated external probe of the specific Render URL did not produce a usable HTTP response in our source environment. The exposure mechanism is confirmed by app code plus the upstream Streamlit static-serving documentation, but the exact current anonymous HTTP status **was not independently determined**. After deployment, test in an incognito session without the family password.

## Changes made

- Disable Streamlit static file serving explicitly (`enableStaticServing = false`).
- Change the 305-page book reader from the direct `/app/static` URL iframe to **`st.pdf(local_pdf_path)`**, using the official Streamlit 1.62 PDF integration; install it by pinning `streamlit[pdf]==1.62.0`. The PDF is rendered only during the family's normal password-gated app flow. The existing read-all-pages viewer, page-number selector, high-resolution original page scan, image gallery, source page captions, OCR/source links and family-book indexing remain.
- Remove the predictable full PDF static URL generator and "Open full PDF in new tab" link. Readers can use the native embedded viewer after login; the page selector still shows the chosen scan alongside the complete edition.
- Extend `tools/privacy_audit.py` to **fail CI** if a future change re-enables `enableStaticServing=true` or removes the explicit false setting. Keep the existing secret-filename, login-order, original-source rights and data validation checks.
- Add regression tests for the static configuration, local book path allowlist, intact ~22.9 MB book file, embedded PDF dependency, absence of the old link generator/iframe, and retention of family login semantics.

## Limits — not a claim of full confidentiality

This resolves **one predictable, anonymous web URL** for the live app if production honors the checked-in Streamlit config. It **does not** establish that every Streamlit media URL is session-authenticated: Streamlit's `st.pdf` implementation may create runtime media file links, and session-level UI gating alone does not provide independently enforced HTTP authorization for every response. A complete privacy cutover still requires a properly authenticated document-serving boundary or proxy and an unauthenticated-browser/network test, not only an embedded viewer.

More importantly, the 305-page PDF, genealogy records and hardcoded legacy login fallback **remain readable in the public GitHub repository**. Disabling static serving cannot reverse previous public availability, protect source clones, or revoke copied files.

**Do not change the current shared family password without the owner's explicit coordinated approval.** Do not silently turn the repository private before verifying that Render's GitHub integration can build from a private repository and a validated rollback exists. No password, Render secrets, GitHub permissions, family relationships, book copyrights, family addresses or Boston Tea Party claims were modified by this PR.

## Release and next cutover gate

- Before merge: Python 3.12/3.13 regression suites, 305-page book asset/page-count checks, static privacy audit, route audit, JavaScript tree/map interactions.
- After merge: verify source backup and restore tests, trigger Render deploy manually (auto deploy disabled), confirm the exact merge SHA is live and no immediate error-level logs.
- Human visit: anonymously request the historic static PDF URL and confirm it is unavailable; verify the same shared-password login, full 305-page in-app reader, page scans and research crosswalk all work when logged in; test mobile.
- **Next major privacy move:** coordinate GitHub repo private visibility + Render integration, move or restrict document deliveries behind HTTP-layer authorization, verify live login, then rotate the historical fallback as part of a planned cutover. Keep the existing simple family-member experience.

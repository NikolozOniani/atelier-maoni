# Atelier MAONI / ატელიე მაონი

A bilingual portfolio for a custom dressmaking atelier in Tbilisi. Georgian is the default language. Each language has a home, work and contact page. The website is plain HTML, CSS and JavaScript: no npm installation, server application or publishing build is required.

## View the website

Run `python3 -m http.server 8000` from this folder and open the local server in your own browser. Use the `/ka/` or `/en/` path to choose a language. Any static web server works; directory navigation expects a web server rather than direct file URLs. All six pages are already written and ready to serve. The portfolio and contact information are readable even with JavaScript disabled.

## Before making it public

Read **MISSING-INFORMATION.md** and **PHOTO-SELECTION.md**. Confirm permission for the selected photographs, especially identifiable customers. No identifiable children are included in the website assets.

The original `Atelier_Maoni_pics` archive and `_studio` review materials are retained. `_config.yml` excludes them, the tests and internal documentation from the standard GitHub Pages branch deployment. **Do not add a `.nojekyll` file or use a hosting process that copies the whole repository**: either would bypass this protection. These exclusions do not hide files in a public GitHub repository. Existing source photographs remain visible to anyone who can read that repository. No source file was deleted or made private.

## Publish with GitHub Pages

1. Review the finished commit and merge it into `main` on the connected GitHub repository.
2. Decide the real website address. In `_studio/data/site.json`, set `siteUrl` to the complete HTTPS site root, including `/atelier-maoni` if using a GitHub project site, without a trailing slash. Leave it blank until the address is confirmed.
3. Ask Codex to run `python3 _studio/render.py` and commit the refreshed HTML, `sitemap.xml` and `robots.txt`. This completes absolute canonicals, social preview image URLs and sitemap entries. The current empty sitemap deliberately contains no invented production URL.
4. After photo permission and privacy review, open **Settings → Pages → Deploy from a branch → main → /(root)**, then save. This is the owner's publication step; it has not been enabled by this task.
5. After the Pages deployment completes, confirm that all six pages and images work. Check that `/Atelier_Maoni_pics/112n.jpg`, `/_studio/review/index.html` and `/PHOTO-SELECTION.md` return 404 on the published site. Stop release if they do not. The local development server intentionally does not apply Jekyll exclusions.

## Change business details

The source of truth is `_studio/data/site.json`. It contains the address, telephone, directions link, Facebook, WhatsApp and website URL. Edit it, then ask Codex to run `python3 _studio/render.py`. The phone display and `telephone` value are separate: the latter is the international number without spaces. No secrets belong in this file. Working hours are not published because they have not been confirmed. WhatsApp is derived from the supplied Georgian mobile number using WhatsApp's standard `wa.me` format; account availability still needs the owner's confirmation.

## Change wording or add a language

English and Georgian text lives in `_studio/data/translations.json`. Project titles, descriptions and image descriptions live in `_studio/data/portfolio.json`. Ask Codex to update the relevant language and refresh the static pages. No translation service runs in the visitor's browser.

## Add a photograph or reorder the work

Ask Codex to:

1. Keep the new original in the source archive. Confirm image rights and any customer or guardian permission.
2. Visually review the actual image, group it with its existing garment if appropriate, and record it in `_studio/data/photo-inventory.json` and PHOTO-SELECTION.md.
3. Create metadata-free, orientation-correct WebP copies at suitable widths under `assets/images`. Preserve natural colors and the full garment; do not enlarge small originals. Update the inventory's `variants` with the real sizes.
4. Add or update its project in `_studio/data/portfolio.json`, with Georgian and English titles, descriptions and alt text. Move a project up or down in that list to change the gallery order. Set `featured` to `true` for the six homepage projects.
5. Run `python3 _studio/render.py`, check both languages and commit the changed files. The helper uses only Python's standard library; image optimization is a separate editing task. Hosting simply serves the committed files.

The private development contact sheet is `_studio/review/index.html`, with a full per-image inventory. It is deliberately not linked from the public website.

## Custom domain and search

After purchasing a domain, follow GitHub Pages' custom-domain instructions and the DNS settings provided by your registrar. The owner must approve changes to the domain and DNS. Then update `siteUrl` and refresh the static pages. No CNAME or domain setting has been added.

To use Google Search Console, add the confirmed domain or URL-prefix property, complete Google's ownership verification, and submit the refreshed `sitemap.xml`. Check both languages with URL Inspection. Technical SEO helps search engines understand the site; it cannot guarantee indexing, rankings or AI search visibility.

## Verification

See TEST-REPORT.md for the executed checks. `tests/static_checks.py` checks the written HTML and local paths without dependencies. `tests/browser.cjs` uses development-only Playwright and axe-core with Chromium; these tools are not part of the deployed website. It accepts `MAONI_BASE_URL` to test a project subdirectory. The site's sources, original images and review materials remain in this repository for future maintenance.

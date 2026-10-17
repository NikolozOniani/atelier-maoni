# Verification report

The update was tested locally with Chromium, Playwright and axe-core. No GitHub Pages setting or custom domain was changed, and no phone call or message was sent.

## Passed

- **1,062 static checks:** six localized pages, relative asset/navigation paths and project anchors, responsive image references, document languages, one main heading per page, correct phone links, complete portfolio data, deployment exclusions, crawler access, repeatable static rendering and unchanged SHA-256 hashes for all 34 originals.
- **276 browser checks at the website root**, and **276 at a project subdirectory** (`/atelier-maoni/`). Both runs passed.
- All six pages were exercised at **320, 390, 768 and 1440px** widths. No horizontal overflow or broken local image requests were observed. All displayed images were decoded during the checks.
- Each browser run included **12 page accessibility audits and two modal audits**, using axe-core WCAG 2 A/AA and WCAG 2.1 A/AA rules, with **zero reported violations**. These automated audits are checks of the tested pages, not an accessibility certification.
- All 33 garment photographs decoded and were accessible in both Georgian and English. Filters returned the expected 21 projects: eight evening, two everyday/separates, nine children’s, one bridal and one traditional. Live counts and query parameters matched the selected category. A language change preserved the work page and selected filter.
- The lightbox opened the correct project, moved between its photographs, wrapped with the previous control, responded to arrow keys and a simulated swipe, closed with Escape and its close button, kept Tab focus inside, and restored focus to the thumbnail. The four-image blue group order was exercised through every image. Landscape group photographs use uncropped containment. Single-image projects disabled the previous/next controls.
- Mobile navigation opened and closed correctly, including Escape. Georgian and English links targeted equivalent pages. The root entry selected Georgian.
- Both portfolio pages remained crawlable and usable with JavaScript disabled, including alternate-image links and mobile navigation.
- The telephone, Facebook, WhatsApp and supplied Maps URLs matched the configured details. No original source photo was linked from the public gallery.
- All **88 generated WebP variants** were checked for valid dimensions and absent EXIF/XMP metadata. The originals were not altered. Output copies preserve orientation, proportions and natural colors. All photographs have the owner’s publication approval, including parent or guardian consent where applicable.
- The homepages, portfolio, contact pages and image viewer were visually inspected in rendered desktop/mobile screenshots. Font loading succeeded for English and Georgian. JavaScript syntax checks passed.

## Publication items and untested external behavior

- Both contact pages were verified to use the exact supplied Maps destination: `https://maps.app.goo.gl/drJ2gnc8GKpYNQ599`. No coordinates or map embed were added.
- Phone routing, the existence of a WhatsApp account and live social-account availability were not tested by contacting anyone.
- `siteUrl` remains blank because the production address is unconfirmed. The renderer was tested with an isolated, non-production fixture and emits absolute canonicals, language alternates, social image URLs and sitemap entries when a real URL is supplied. No fixture URL was written into public pages. The current sitemap is intentionally empty.
- `_config.yml` archive/review exclusions were checked statically. A local Jekyll build and live GitHub Pages deployment were not run. Verify the actual Pages output excludes the archive and review files; do not add `.nojekyll` or upload the entire repository to another static host. A public GitHub repository can still expose the original archive independently of Pages.
- The owner confirmed publication permission for all 33 garment photographs, including relevant parent or guardian consent for photographs of children.
- Physical-device and screen-reader testing was not performed. Mobile touch behavior was exercised through browser events.

## Repeat the checks

From the repository root:

```sh
python3 _studio/render.py
python3 tests/static_checks.py
python3 -m http.server 8000 --bind 127.0.0.1
```

In another shell, with development-only browser tooling available:

```sh
npm install --prefix /tmp/maoni-qa --cache /tmp/maoni-npm-cache playwright @axe-core/playwright
NODE_PATH=/tmp/maoni-qa/node_modules node tests/browser.cjs
```

The browser check expects Chromium at `/usr/bin/chromium`; set `MAONI_CHROMIUM` if it is elsewhere. `MAONI_AXE_MODULE` can point to a separately installed axe Playwright module. These dependencies are solely for local QA. Visitors and GitHub Pages do not need Node or npm.

To repeat the project-subdirectory test, serve the parent folder on another port and set `MAONI_BASE_URL` to the corresponding local server plus `/atelier-maoni`. Both deployment forms use the same committed static files.

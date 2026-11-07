# Build sources (backup)

`site/` at the repo root is the built website that Netlify serves. This folder holds the scripts that produce it.
Nothing here is deployed (Netlify publishes `site/` only), so changing these files changes nothing live.

## Pipeline (run from a working folder that has these files plus `bundle/`, `photos/` and `insta/`)
1. `python3 daily/content.py`: writes the daily questions (`daily/parts/days.js`). Days are listed in `CURATED`/`RECEIPTS`/`EXTRA_BOARDS`.
2. Run the daily splices in order: `cd daily && for f in splice.py splice2.py … splice13.py splice14.py; do python3 $f; done`. (`splice14.py` = PR 1, honest Receipts.) Each one edits `src.html`, starting from `src.v1.html`.
3. `python3 daily/build.py`: writes `bundle/daily.html`.
4. `python3 site/site.py`: writes the home, party and brands pages into `bundle/`.
5. `python3 package_host.py`: writes the deployable folder (`host/`), which is copied to the repo's `site/`.

Server code is not here. It lives in `lib/` (crews.mjs, clubs.mjs) and runs as `netlify/functions/api.mjs`. Tests: `npm test`.

## Notes added in PR 1
- `og/`: how the link-preview image `site/og.jpg` was made. `og.html` covers the old image's prize tile and "??% said yes" line (`og-old.jpg`). Render with `node og/render.mjs <folder>`.
- `site/cabinets.html` and `.css` (the party page tiles) are now backed up here too.
- Not backed up here yet: the party game pages (`showdown.html`, `thecall.html`, `droppin.html`) and photos/icons. Those live in the build scratchpad's `bundle/` and are copied as they are. `package_host.py` post-processes them, including the Showdown "we asked 100" wording fix.

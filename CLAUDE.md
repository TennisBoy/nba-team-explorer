# CLAUDE.md

Guidance for working in this repo. Keep it short and current; update it when the
architecture or workflow changes.

## What this is

**NBA Team Explorer**: a self-contained static site to browse every NBA team's
roster (position, height, per-game stats), league leaderboards, and team-vs-NBA
averages, across 5 seasons (2021-22 → 2025-26). Deployed on Azure Static Web Apps.

Live: https://polite-flower-0eee8ee0f.7.azurestaticapps.net/
Repo: https://github.com/TennisBoy/nba-team-explorer

## Files

| File | Role |
|------|------|
| `index.html` | The whole app: markup + CSS + JS in one file. Reads `nba_data.js`. |
| `nba_data.js` | Generated dataset (`window.NBA_DATA`). ~700 KB. Do not hand-edit. |
| `build_data.py` | Fetches rosters + player/team stats from `nba_api`, writes `nba_data.js`. |
| `knicks_2026_champions.html` | Standalone Knicks champions page. Also reads `nba_data.js`. |
| `.github/workflows/azure-static-web-apps-*.yml` | Auto-deploy on push to `main`. |
| `README.md` | User-facing overview. |

## Data model (`window.NBA_DATA`)

```
{ seasons: ["2025-26", ...],           // newest first
  data: { "2025-26": { "NYK": {
    id, name, city, nickname, abbr, color, accent, champion,
    totals: { PTS, REB, AST, STL, BLK, TOV, FG_PCT, FG3_PCT, FT_PCT },  // team per-game
    players: [ { id, name, num, pos, height, weight, age, exp,
                 s: { GP, MIN, PTS, REB, AST, STL, BLK, FG_PCT, FG3_PCT, FT_PCT } } ]
  } } } }
```
`s` is `null` for players with no recorded games. `totals` may be `null` in older data.

## Regenerating data

```bash
pip install nba_api
python build_data.py     # ~2 min: 5 seasons x (30 rosters + player stats + team stats)
```
- Edit `SEASONS` and the `CHAMPIONS` map at the top of `build_data.py` to change coverage.
  Champions are hard-coded (nba_api has no "who won the title" endpoint); verify new ones
  against NBA.com/ESPN before adding.
- `COLORS` / `ACCENT` are per-team brand colors keyed by abbreviation.

## Conventions

- **Everything is data-driven**: never hard-code rosters/stats into HTML. Pull from
  `NBA_DATA`. (The Knicks page was converted away from hard-coded arrays; keep it that way.)
- **No em dashes or en dashes in prose** (user preference). Use hyphens or restructure.
- **Self-contained**: no build step, no framework, no external JS/CSS. Just open
  `index.html`. Only network dependency is player headshots from `cdn.nba.com`
  (graceful initials fallback via the `FALLBACK` onerror handler).
- The app is a hash-routed SPA: `#NYK` opens a team, empty hash is home. See `route()`.

## Verifying changes to `index.html` (no browser needed)

`index.html`'s script uses only `document`/`window`, so you can exercise it under a
lightweight DOM stub in the context-mode sandbox (bun). Pattern:
1. Read the file, extract the last `<script>` block.
2. `new Function(script)` for a syntax check.
3. Build a stub `document`/`window` (getElementById returning fake els with
   `innerHTML`/`classList`/`addEventListener`/`scrollIntoView`, plus
   `IntersectionObserver`, `window.scrollTo`, and a one-shot `setTimeout` so the
   typewriter doesn't loop forever), eval `nba_data.js` then the app, then assert on
   captured `innerHTML` and trigger `_h` handlers.

This catches render-time throws and logic regressions without Playwright. Do this before
every commit that touches `index.html`.

## Deployment

- Push to `main` → the Azure workflow builds and redeploys automatically (~1-2 min).
- Build settings in the workflow: `app_location: "/"`, `api_location: ""` (no backend),
  `output_location: "."`. There is no API; do not add one unless live data is required.
- Git normalizes LF↔CRLF on Windows; a 1-byte hash diff on `nba_data.js` between local
  and deployed is just the trailing newline, not a content difference.

## Gotchas

- `nba_api` rate-limits; `build_data.py` retries and sleeps between calls. Don't parallelize.
- ctx sandbox runs **bun**; `jsdom` fails there ("Proxy in global prototype chain").
  Use the hand-rolled DOM stub above, or Node if `jsdom` is truly needed.
- Headshots require network; the rest works fully offline.

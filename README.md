# 🏀 NBA Team Explorer

Browse every NBA team's roster and see each player's position, height, and per-game stats. The season's
champion is highlighted. Data comes from the NBA's official stats through the open-source
[`nba_api`](https://github.com/swar/nba_api).

![Seasons](https://img.shields.io/badge/seasons-2021--22%20%E2%86%92%202025--26-blue)
![Teams](https://img.shields.io/badge/teams-30-orange)

## Features

- All 30 teams on a color-coded, clickable home page
- Season selector for 2021-22 through 2025-26; rosters, champions, and leaderboards update when you switch
- The champion is pinned each season (🏆 NYK 2026, OKC 2025, BOS 2024, DEN 2023, GSW 2022)
- Leaderboards for the top 5 in points, rebounds, assists, and blocks per game
- Player cards with headshots, position, height, and per-game PTS/REB/AST plus GP/MIN/FG%/3P%
- Sort by jersey #, points, rebounds, assists, or height
- Group by position (Guards / Forwards / Centers)

## Usage

Open `index.html` in a browser. It's a self-contained static site with no build step and no server.
The dataset lives in `nba_data.js`, so everything works offline except player headshots, which load
from `cdn.nba.com`.

## Regenerating the data

```bash
pip install nba_api
python build_data.py
```

Edit the `SEASONS` list in `build_data.py` to change which seasons are fetched. The script writes
`nba_data.js` (all teams × seasons, rosters + per-game stats).

## Files

| File | Description |
|------|-------------|
| `index.html` | The app (home page + team detail views) |
| `nba_data.js` | Generated dataset: 5 seasons, all 30 teams |
| `build_data.py` | Fetches rosters + stats from `nba_api` and writes `nba_data.js` |
| `knicks_2026_champions.html` | Standalone page for the 2026 champion New York Knicks |

## Data sources

- Rosters & stats: [`nba_api`](https://github.com/swar/nba_api) (NBA official stats)
- Championship results: NBA.com / ESPN
- Headshots: `cdn.nba.com`

*Not affiliated with or endorsed by the NBA.*

# offcampus-server

The Off Campus server for **Crews**: friend groups that compare their daily scores.
Plain Node with no packages. `npm start` runs it, `npm test` checks it.

## Railway setup
1. New Project → Deploy from GitHub repo → `offcampus-server`.
2. Add a **Volume** to the service, mounted at `/data`.
3. Variables: `DATA_DIR` = `/data`.
4. Settings → Networking → **Generate Domain**. That address goes into the game (`CREWS_API` in daily.html).

## What it stores
Crews (name, members), players (a random id and a nickname, no accounts), and each player's score per day.
Saved to `DATA_DIR/offcampus-data.json` every 5 seconds, with a daily backup kept for 14 days.

## Endpoints
- `GET /health`
- `POST /api/score` `{ playerId, nick, day, total, pts[5] }` (first score of the day counts)
- `POST /api/crews` `{ playerId, nick, name }` creates a crew
- `POST /api/crews/CODE/join` `{ playerId, nick }`
- `GET /api/crews/CODE?playerId=` today's board
- `GET /api/me?playerId=` my crews
- `GET /api/stats` players today, players all time, crews

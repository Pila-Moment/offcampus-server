# Off Campus

The Off Campus site (offcampusontario.ca) and its Crews API. Netlify deploys this repo automatically when `main` changes.

- `site/` is the website: home, the Queen's Daily, party games, prizes, the brand page.
- `netlify/functions/api.mjs` answers everything under `/api/` (Crews). Data is saved in Netlify Blobs.
- `lib/crews.mjs` is the Crews logic. `npm test` checks it.

## Crews API
- `GET /api/health`
- `POST /api/score` `{ playerId, nick, day, total, pts[5] }` (the first score of the day counts)
- `POST /api/crews` `{ playerId, nick, name }` makes a crew
- `POST /api/crews/CODE/join` `{ playerId, nick }`
- `GET /api/crews/CODE?playerId=` today's board
- `GET /api/me?playerId=` my crews
- `GET /api/stats` players today, players all time, crews

Players have no accounts: a random id saved on their phone and a nickname.

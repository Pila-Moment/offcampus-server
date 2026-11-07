# House League (milestone 1)

**Page:** `/house.html`. **Invite link:** `/house.html?join=CODE`.

**Server:** `lib/houses.mjs`, hooked into `lib/crews.mjs`. **Tests:** `test-houses.mjs`, run by `npm test`.

## House vs crew
- **A house** is your official team in the Queen's House League. You're in one house at a time, and you count for one house per week.
- **A crew** is a casual scoreboard for any group of friends. Have as many as you like. Crews and club games are unchanged.

## Rules (all settings are at the top of `lib/houses.mjs`)
- **Weeks:** Monday 4am to Monday 4am, Toronto time, the same reset as the Daily.
- **Your score:** the first Daily score each day counts for your house automatically.
- **Getting ranked:** a house needs **3 different players** with a Daily that week. Until then it shows "2 of 3 players".
- **Daily %:** each Daily is a % of that day's maximum. Old 5,000-point records are read the honest way: 2,300 out of 3,000.
- **Player %:** the average of the days they played. Missed days are **not** zeros.
- **House %:** the average of its players' averages, so one very active player can't carry the house.
- **Ties:** same % (to 0.1), then more players, then more Dailies played. If it's still tied, the houses share the rank.
- **Switching houses mid-week:**
  - The first house you count for in a week keeps your week.
  - Your new house gets you from Monday, and the page says so.
- **Privacy:**
  - The league shows only house names, colours and numbers.
  - Only members see the roster and nicknames.
  - People outside a house see its name and size, nothing else.
- **House names:** names that look like a street address ("517 Earl St") are refused. No address or contact details are ever asked for.

## Pages
- **Home:** a House League tile.
- **Daily:**
  - The top tabs are OC / DAILY / HOUSES / PARTY GAMES. Clubs moved to the home page.
  - Players in a house see one line on the intro.
  - After a game, players see "TODAY COUNTED FOR [HOUSE]" with their standing and an INVITE button.
- **House page:**
  - Start a house: name, colour, optional motto, and a live crest preview.
  - Join from a link or code.
  - Your house: rank or "x of 3", the gap to the house above or below, this week's roster, invite, share card.
  - The league table and last week's House of the Week, with a share card.
  - Edit or leave the house.
- **Invite links** stay on the site they were opened from, so a preview's invites stay on that preview.

## Milestone 2 (polish)
- **Starting a house:**
  - Tap-to-use name ideas, and the crest pops as you type.
  - Creating the house shows a "HOUSE FOUNDED" moment that leads straight to an invite page: three seats, a big house code, COPY LINK, and INVITE MY ROOMMATES.
- **Invite page:** shows the seats ("You'd be player 2"), and the message says how many more players the house needs.
- **Celebrations, each shown once:** getting into the league, moving up the ranks, and winning House of the Week.
- **Rivalry:** a head-to-head card with the house above or below: bars, both %, and "X POINTS TO PASS".
- **Returning tomorrow:** once you've played, a countdown to the next five plus a gentle "NUDGE THE HOUSE" message, with no names called out.
- **After the Daily:** "TODAY COUNTED FOR…" shows **only when the server confirms today's score**. Otherwise it says "NOT COUNTED FOR [HOUSE] YET" with TRY AGAIN. The line under it gives the rank, the gap and "new five at 4am".
- **Switching houses:** "This week's scores stay with [OLD] until Monday. From Monday they count for [NEW]."
- **Scoring:** every day's score now saves its version and maximum (`v`, `max`). The House League reads each day as a % of its own max. See `docs/FROZEN_RECEIPTS_PLAN.md`.

## Known limits
- **Scores aren't verified:** Showdown and Pin points are still worked out on the phone, and identity is the browser. Fine for a no-prize league; not for a prize competition. There are **no prizes, sponsors or rewards** in the House League.
- **The standings are worked out on every visit,** which is fine for a pilot (tens of houses), not for thousands.
- **No moderation queue for house names yet,** beyond length, address and HTML filtering.
- **Small screens:** a player in both a house and a crew may scroll a little on the come-back screen of the smallest phones.

# Off Campus: technical handoff for Serge (Nov 5, 2026)

This file is the **technical** half of the handoff, and it's safe to keep in a public repo. The business half (strategy, plans, models, outreach, Josh's situation) is in Josh's "Off Campus full context pack." Josh shares it with you directly. It is deliberately **not** in this repo, because the repo is public.

## 1. Access (all read-only, no accounts needed)
- **Repo:** https://github.com/Pila-Moment/offcampus-server. It's **public**, so you can read it with any GitHub connection. No extra permissions are needed to read.
  - **Not this one:** `Pila-Moment/life-line` is the **old** LINE RUSH / RECEIPTS project (Railway, October). It is not Off Campus. Ignore its branches for current work.
- **Branches:**
  - `main` = production. Netlify deploys every push to `main` in about a minute.
  - Work happens on short-lived branches with a pull request. Netlify builds a free preview for each PR at `deploy-preview-<N>--rad-pothos-d03a2a.netlify.app`.
  - Last PR: #1 `club-release-v2`, merged Nov 5.
- **Production commit:** `2e4dcc6` (Nov 5, 2026, "Merge club games v2 + houses and retention batch"). To get the latest: `git log origin/main` or https://github.com/Pila-Moment/offcampus-server/commits/main
- **Live site:** https://offcampusontario.ca. Public; you can audit any page in a browser.
- **Public JSON you can read anytime:**
  - https://offcampusontario.ca/api/stats (totals and aggregates only, no personal data)
  - https://offcampusontario.ca/api/home
  - https://offcampusontario.ca/api/health
- **Analytics:** GoatCounter at offcampusontario.goatcounter.com. **Private**, only Josh logs in. Josh shares screenshots, or he can turn on GoatCounter's public dashboard setting if he wants.
- **Hosting:**
  - Netlify, free plan, project "rad-pothos-d03a2a", linked to GitHub `main`.
  - Data is stored in **Netlify Blobs** (key-value) through one Netlify Function at `/api/*`.
  - The domain points to Netlify.
  - No other services, no database server, no paid tools.
- **Environments:**
  - local (Claude's workspace: an in-memory API plus a static server)
  - PR previews (they use the **same** production data store)
  - production
  - No separate staging data.
- **Only in Claude's workspace until now:** the scripts that build the site. As of this commit they're backed up in `build-src/` (see `build-src/README.md`). The built site in `site/` was always committed.
- **Staying up to date:** watch commits on `main`. Every commit message says what changed in plain words. This file and `build-src/` get updated with major batches.

## 2. Where things live
| Thing | URL | Source |
|---|---|---|
| Home | `/` | `site/index.html`; built by `build-src/site/site.py` |
| Queen's Daily | `/daily.html` | `site/daily.html`; built from `build-src/daily/` (src.v1.html + splice*.py, questions in content.py) |
| Party games (3, one host screen) | `/party.html`, `/thecall.html`, `/showdown.html`, `/droppin.html` | `site/` (prebuilt) |
| Club games: exec page | `/clubs` | `site/clubs.html` |
| Club game: builder, play, results | `/club.html?new`, `/club/<name>` | `site/club.html`; server `lib/clubs.mjs` |
| Stats for Josh | `/stats.html` | `site/stats.html` |
| For brands | `/brands.html` | built by `build-src/site/brands_page.py` |
| Brand demo link maker | `/link.html` | `site/link.html` |
| Prize preview (not linked to players) | `/prizes.html` | `site/prizes.html` |
| Server (all API routes) | `/api/*` | `netlify/functions/api.mjs` → `lib/crews.mjs`, `lib/clubs.mjs` |
| Tests | n/a | `test.mjs` (`npm test`, about 150 checks) |
| Routing / redirects | n/a | `netlify.toml` (`/club/*` → club.html) |

## 3. Features (verified against the code)
Status key: **LIVE** = on production and covered by tests or a phone check. **PREVIEW** = built, not on main. **OFF** = in the code but switched off.

1. **Queen's Daily (LIVE).**
   - **Format:** 5 rounds, new at 4am Toronto, the same for everyone. Day 1 = Nov 3, 2026. Content is written through Dec 7 (day 35).
   - **Rounds:** Receipts, Survey Showdown, Receipts, Survey Showdown, Drop the Pin. Max 5,000.
   - One play per day per browser.
   - No scrolling on 360×640 up to 390×844 (tested in a phone emulator).
2. **Receipts (LIVE).**
   - The player answers YES/NO first, then guesses the % of Queen's who said yes.
   - **The number shown on the reveal is written by us** (editorial), not measured, and scoring uses it so everyone gets the same answer all day.
   - Real answers are saved, and shown as "REAL ANSWERS SO FAR: x OF n" once 5+ answered, plus the crew's split once 5+ crew members answered.
3. **Survey Showdown (LIVE).**
   - Since Nov 5, the player types their own answer first, which is saved as a real answer. Then they name the top answers on a board before 3 strikes.
   - **The board's answers and points are written by us.** The reveal says "SURVEY SAYS…" (the earlier "WE ASKED 100 QUEEN'S STUDENTS" was removed).
4. **Drop the Pin (LIVE).** A Kingston photo: place a pin on a map, then guess the year. 34 photos, used up by Dec 7.
5. **Identity (LIVE).**
   - No accounts. A random ID per browser.
   - Optional name + 4-digit PIN ("save your spot") to log in on another browser, e.g. Instagram's in-app browser vs Safari.
6. **Crews (LIVE).**
   - Create or join by link.
   - Board tabs: **TODAY** (scores), **WEEK** (Monday–Sunday totals plus a **stake**: "Winner: … / Loser: …", set by any member; added Nov 5), **LEAGUE** (30 days: wins, averages, streaks, best at each game).
   - Morning recap with SEND TO CHAT. On Mondays it names last week's winner and loser.
   - Smart button: INVITE / NUDGE THE N WHO HAVEN'T PLAYED / SEND THE RESULTS.
7. **Sharing (LIVE).**
   - CHALLENGE YOUR FRIENDS: score image + link (`?ref=share&s=&d=`), which opens "YOUR FRIEND GOT 3,212. CAN YOU BEAT IT?"
   - SEND THIS TO [friend type] on Receipts reveals.
   - Link previews (og.jpg).
8. **Suggest a question (LIVE, Nov 5).**
   - From the finish screen, the intro and the home page.
   - Receipts or Survey, optional @ for credit. Max 5 per player per day.
   - Josh sees them on /stats.html after claiming his admin key. Used questions can show "SUGGESTED BY @…"
9. **Come-back hooks (LIVE, Nov 5):**
   - tomorrow's question teased above the countdown
   - Add to Home Screen tip on a player's 2nd day (phones, not in Instagram)
   - home page "crew of the week" and "yesterday at Queen's" (real answers, shown at 10+)
10. **Club games v2 (LIVE, Nov 5).**
    - **Builder:** the exec picks 5 from a question bank by club type, with their inside info worked in.
    - **Card types:** yes/no + guess the %, most popular of 4, trivia.
    - **Members play in one visit.**
    - **The exec taps RELEASE THE RESULTS** (unlocks at 5 finished). Answers freeze, scores and the leaderboard go live.
    - **Late players** are scored instantly but never change the results.
    - **Real counts always** ("WE ASKED 25 … 16 OF 25 SAID YES"). Names show on the leaderboard.
    - **Extras:** optional JOIN [CLUB]'S DAILY CREW, an Instagram results image, and an admin key that can release any club.
11. **Stats (LIVE).**
    - /stats.html: players today, came back today, all time, crews, last 7 days.
    - **By source (`?ref=`)**, with back-next-day and back-within-7-days (from Nov 5 onward).
    - Club funnel (started, finished, played the daily, joined the crew).
    - The "I'M JOSH: LEAVE ME OUT" button hides Josh's browsers from the stats.
12. **Prizes (OFF).**
    - Prize spin, prize reel and the 2,500-point unlock exist in code, but `PRIZES_LIVE = false`.
    - **No prize talk is shown to players since Nov 4.**
    - **Brand demo links** (`daily.html?spot=…&offer=…`, made at /link.html) still show the sample prize spin. They're labelled as made-up spots.
13. **For brands (LIVE page).** Founding partners. Features that aren't built yet (one-use codes, live clock, weekly cap, weekly report) are worded as "built for our January launch." The interest form includes crew deal, sponsored question, club night, parents offer.
14. **Party games (LIVE).** The Call, Survey Showdown and Drop the Pin, on one shared screen, with a HOME button.

**Considered and postponed or rejected:**
- **Real prizes:** postponed. They need brand pledges, contest rules and a lawyer.
- **The "We asked 100 Queen's students" claim:** rejected (not true).
- **Club two-round flow** (answer, wait, return): replaced by one visit.
- **Typed club answers:** cut (moderation, privacy).
- **"This or that" club cards:** replaced by most popular of 4.
- **Exec timer (24h/48h):** replaced by the exec releasing manually.
- **Hiding small-group results:** Josh chose real counts always.
- **Leaderboard names off by default:** Josh chose names on.
- **Roommate chores app:** rejected.
- **Collect-the-set prizes, referral spins, winners feed, post-to-double, streak bonus, survey-for-a-spin:** designed, waiting for real prizes.
- **A/B tests and the 17-event schema:** postponed until there are enough players.

## 4. Analytics: what's measured
**GoatCounter** (correct name; Josh sometimes calls it "GoatTracker"). No cookies, no personal data. Pageviews, referrers, browsers and countries come automatically. Custom events have an `event-` prefix:
- **Daily:** `start`, `finish`, `share`, `send-q`, `follow`, `unlocked`, `teaser`
- **Saving / login:** `save-shown`, `save-done`, `login`
- **Crews:** `crew-start`, `crew-join`, `crew-invite`, `crew-open`, `crew-league`, `crew-week`, `crew-stake`, `crew-stake-send`, `crew-week-send`, `recap-send`
- **New on Nov 5:** `survey-own`, `suggest-open`, `suggest`, `hometip`
- **Clubs:** `club-make-1`, `club-make-2`, `club-made`, `club-start`, `club-finish`, `club-share`, `club-send`, `club-release`, `club-send-results`, `club-post`, `club-to-daily`, `club-crew-join`

**Server counts** (/api/stats, per browser ID, Josh hidden once he taps the button):
- players today and yesterday
- came back today (played yesterday and today)
- all-time players
- crews
- last 7 days
- **by source:** players, back next day (of how many), back within 7 days (only for players 7+ days old; starts Nov 5)
- the club funnel
- number of suggestions

**Verified numbers, Nov 5 evening:**
- **Server:** 15 all-time browser IDs. Day 1: 1 player, day 2: 8, day 3: 7. Came back on day 3: 2, both Josh and his girlfriend, so **0 independent returning players so far**.
- **GoatCounter (Oct 29–Nov 5):**
  - 162 visits
  - referrers: unknown 34, ig 16, insta 4, facebook.com 3
  - 20 `start`, 16 `finish` events (80%)
- **Instagram:** about 15 followers.
- **Limits:**
  - A browser ID is not a person: a cleared browser or a second browser counts again.
  - Josh's own plays are included before Nov 5.
  - Visits are not players.

**NOT MEASURED:**
- verified unique students
- age or school
- 7-day retention (no players old enough yet, measured from Nov 5)
- referral completions per sharer
- prize redemptions (prizes are off)
- revenue
- cost per player from paid channels (nothing has been spent)

## 5. Timeline
- **Oct (life-line repo):** RECEIPTS / LINE RUSH work on Railway, the earlier concept. Superseded.
- **Nov 3:**
  - new repo `offcampus-server`, moved to Netlify + Blobs
  - crews server
  - launched the Queen's Daily
  - party games HOME button
  - the OC logo as the app icon
  - more pin photos
- **Nov 4:**
  - repo made public (Netlify free plan needed it for deploys)
  - no-scroll pass
  - best questions moved into week 1
  - growth pass (challenge friends, send a question, crew league)
  - stats page
  - challenge links
  - content through Dec 7
  - real answers saved
  - nudge and results buttons
  - save your spot (name + PIN)
  - prize talk removed from player screens
  - club games v1, then v2 on preview
- **Nov 5:**
  - houses and retention batch (week + stakes, answer-first survey, suggest a question, teaser, home-screen tip, home live strip, stats by source)
  - merged to production with club v2
  - build sources backed up
- **Founder decision, Nov 5:** the Instagram profile picture changed to a pixelated-controller gaming logo. **Not yet on the website**, which still uses the "OC" logo.

## 6. Costs (actual)
- **Hosting:** $0 (Netlify free plan, Blobs included).
- **GoatCounter:** free.
- **Marketing:** $0 spent.
- **Domain:** offcampusontario.ca, cost not recorded here (ask Josh).
- **Before thousands of daily players:** expect a paid Netlify plan (tens of dollars a month), backups, a proper database, scores checked on the server (today a determined player could fake a daily score; it doesn't matter without prizes), and a load test.

## 7. Known risks and gaps
1. No backups of Blobs data yet.
2. Daily scores are trusted from the browser (fix before prizes).
3. Some stats routes list every record, which is fine for hundreds of players but slow at tens of thousands.
4. Previews write to production data.
5. The editorial %s on Receipts and the editorial Survey boards are not real survey results. Real-answer lines are shown separately.
6. Pin photos run out after Dec 7.

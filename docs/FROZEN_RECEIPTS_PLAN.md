# Frozen Receipts: design and scoring plan

**Status: built behind a switch that is OFF.** Nothing below collects data or changes any score until Josh approves turning it on.

**Goal:** Receipts score again, but only against real, frozen answers from Off Campus players. No made-up numbers, no live splits, and nobody's answer can be worked out.

## What's already in place (this branch)
- **Per-day scoring:** every day keeps its own maximum. `dayScore()` and `dayPct()` in `lib/crews.mjs` read:
  - **v1** (before Nov 6, no version): read as v2.
  - **v2** (now): `{ v:2, max:3000 }` saved on every new score.
  - **v3** (future): `{ v:3, t, p, max }`, read with its own max.
- **House League** already compares days as % of each day's own max. A test proves a v3 day of 4,000 out of 5,000 counts as 80%.
- **No stored record is rewritten,** and nothing writes v3 yet.

## 1. Questions with stable ids
- **Each Receipts question gets a permanent id** (`rq_0001` …) in `build-src/daily/content.py`. Wording changes bump a version, and answers to an old version never mix with a new one.
- **Server record:** `rq/<id>` = `{ id, v, text, firstDay, lastDay:firstDay+13, status:'collecting'|'frozen'|'expired', n, yes, frozen:{ n, yes, day } }`.
- **Answers:** `rqa/<id>/<player>` = `'Y'|'N'`. The first answer counts. The page gets "already answered" ids, so nobody is asked the same question twice.

## 2. Collecting across up to 14 days
- **Day of release:** a question is the Daily's answer-only round (round 1), as it is today.
- **Catch-up for 13 more days:** after the Daily, an optional "OPEN QUESTIONS" card offers up to 3 open questions this player hasn't answered. It's never scored and never blocks anything. This is what makes 30 answers reachable at today's ~10 players a day.
- **No live splits, ever.** The server only ever returns the count.

## 3. Freezing
- **At 30:** when a question reaches 30 different answers, the server freezes it once (`frozen = { n, yes, day }`). Later answers are stored but never change the frozen numbers.
- **Expiry:** at the end of `lastDay` with fewer than 30, it becomes `expired`. Its % is never published or used, and only "not enough answers" is shown.
- **Wording:** "19 of 34 Off Campus players who answered said YES". Never "Queen's students", and never presented as a survey.

## 4. Guessing a frozen result (server-scored)
- **The target:** each day, the first request after 4am picks one guess target, the oldest frozen question not yet used. It's saved as `target/<day>`, so everyone gets the same one.
- **If nothing is frozen,** round 3 stays answer-only, like today.
- **Round 3 when there's a target:** "Guess what % said YES". The page gets the question text only.
- **Server-side scoring:** `POST /api/receipts/guess { day, qid, guess }`.
  - The server scores it as `1000 − 25 × |guess − frozen%|`, floored at 0.
  - It saves `guess/<day>/<player>` (the first guess counts) and only then returns the frozen n/yes for the reveal.
  - **The target % is never sent before the guess.**
- **The score record:** `POST /api/score` on a v3 day ignores anything the page sends for Receipts rounds. The server fills them in from its own saved guess (0 if there was no guess), and saves `{ v:3, t, p, max }`.
  - The day's `max` is 1,000 × the scored rounds that day: **3,000 with no target, 4,000 with one.**
  - Showdown and Pin are still scored on the phone (unchanged, documented).

## 5. Keeping old and new scores comparable
- **House League:** already uses % of each day's own max. Nothing changes.
- **Crews:**
  - TODAY is the same day for everyone, so raw points stay fair.
  - WEEK, LEAGUE, streak best, Monday recap and crew of the week currently add raw points. With 3,000 and 4,000 days mixed, playing on 4,000 days would be an unfair advantage.
  - **Proposal:** WEEK and LEAGUE show the average % (like the House League), and "best" becomes the best %. Stakes and winners/losers use the same %.
- **Share text, score card, challenge links:** these show "out of [that day's max]". Challenge links only compare the same day, so they stay fair.
- **Old records:** never rewritten. v1 and v2 days are read as 3,000-point days.

## 6. Tests to add before switching on
- **Freezing:**
  - Freezes at exactly 30 different players; 29 doesn't freeze.
  - The 31st answer doesn't change the frozen numbers.
  - A duplicate answer doesn't count.
  - Expires on day 14 with 29 answers, and nothing is published.
- **Never sent early:** the frozen % never appears in any response before that player's guess, and never in `/api/home` while collecting.
- **Same target for everyone:** two players on the same day get the same target, including across the 4am rollover.
- **Can't be faked:**
  - A page sending made-up Receipts points gets them replaced by the server's.
  - A replayed guess is ignored.
- **Mixed days:**
  - 3,000 and 4,000 days in the same week rank correctly in the House League and the proposed crew WEEK %.
  - Old v1/v2 days are read correctly.
- **The game keeps going:** if the guess endpoint is offline, the round says so and lets the player continue, with no fake reveal.

## Decisions needed before building
1. **Day size:** 4,000-point days (one new answer-only question plus one frozen guess) or 5,000 (two guesses)? **Recommended: 4,000.** It keeps new questions collecting every day, and today's volume can't freeze two questions a day.
2. **Catch-up card:** OK to add the optional "OPEN QUESTIONS" card after the Daily? **Recommended: yes.** Without it, 30 answers in 14 days is unlikely at current volume.
3. **Crews:** OK to switch crews WEEK and LEAGUE from point totals to average %? **Recommended: yes, in the same release that turns v3 on.**
4. **Points per % off:** keep 25 per percentage point (a guess 40 points off scores 0)? **Recommended: keep it.**
5. **Wording:** "X of N Off Campus players who answered", confirmed as the wording for every reveal.


## Built (behind the switch), Nov 7

- **The switch:** `OC_FROZEN_RECEIPTS=1` (a Netlify setting). It's **not set anywhere**, so production and previews behave exactly as before.
  - With it off, `/api/rq/*` returns 404, every score is a normal 3,000-point day, and the Daily never asks.
  - To try it on a preview later, Josh would set it for **Deploy Previews only**.
- **Agreed design decisions:**
  - 4,000-point days when there's a frozen target, otherwise 3,000.
  - An optional OPEN QUESTIONS card (up to 3, unscored).
  - Crew WEEK and LEAGUE in average % with days played shown.
  - 25 points lost per percentage point off.
  - Reveal text: "X of N Off Campus responses said YES."
- **Server, `lib/receipts.mjs`:**
  - Questions have stable ids from `lib/rq-bank.mjs`, which is made by `build-src/daily/content.py` (69 questions, each with its first day and version).
  - Answers, the frozen result, the day's target, "used" and "public" markers, and guesses are each written once with **only-if-new** writes (Netlify Blobs `onlyIfNew`). So simultaneous answers or retries can't overwrite the first one, and everyone gets the same target that day.
  - The frozen result is always the **first 30 answers** (by time, then player), even if more arrive at the same moment.
- **Never a seen result:**
  - The home page shows a frozen result only after its guessing day is over, and marks it public.
  - A question that was public (or that the old home rule could have shown, 30+ answers on its own day) is **never** picked as a target.
  - The home cache key changes with the switch (`cache/home-v3`).
- **Version-aware scores:** crew TODAY, WEEK, LEAGUE, wins, streaks, Monday recaps, crew of the week and the House League all read each day against its own max (v1/v2 = 3,000, v3 = its own).
  - WEEK and LEAGUE show average %, with days played.
  - Wins still compare raw points on the same day (same max).
- **Phone, `build-src/daily/splice16.py`:**
  - Round 1 saves to the 14-day question: "N of 30 answers in".
  - Round 3 on a target day is the guess. The server scores it, and only then the meter fills and "21 of 34 Off Campus responses said YES" appears.
  - If the guess can't be sent: "COULDN'T SEND YOUR GUESS", TRY AGAIN or SKIP, and never a made-up reveal.
  - After the Daily: OPEN QUESTIONS (up to 3).
  - Score card, share text and the come-back screen use that day's max (4,000).

## Evidence
- **`test-frozen.mjs` (in `npm test`), on synthetic questions and players:**
  - Collecting, duplicates, and 6 copies of one answer arriving together (counted once).
  - 29 answers doesn't freeze. The 30th freezes it exactly once, and later answers never change it.
  - It isn't a target on the day it froze. At 3:59am there's no target; at 4:01am the target is the same for everyone.
  - No public endpoint (`/api/home`, `/api/stats`, `/api/rq/open`, `/api/me`, `/api/health`) shows the target's result before the guess.
  - Server-scored guess; a retry keeps the first guess; three guesses arriving together keep one; another day's guess is refused.
  - The v3 score uses the server's guess points (out of 4,000).
  - Shown on the home page after its day, and never a target twice.
  - A result that was public under the old rule is never a target.
  - 40 answers at once: 40 saved, frozen at exactly 30.
  - Expiry on day 15 with 29 answers, never shown anywhere.
  - Open questions: 3, text only.
  - A mixed 3,000/4,000 week end to end (crew TODAY, WEEK, LEAGUE, wins, streaks, Monday recap, crew of the week, House League).
- **On the phone:** a local server with the switch on and one synthetic frozen question (`apisrv3.mjs` in the build scratchpad).

## Before switching on (Josh's call)
- **Approve 14-day answer collection.** Answers are stored against a browser id, and only counts are ever shown.
- **Add real questions** for the bank's upcoming days. Questions that repeat in the 35-day plan are asked once per person.
- **Turn it on for a preview first,** with `OC_FROZEN_RECEIPTS=1` for Deploy Previews only.

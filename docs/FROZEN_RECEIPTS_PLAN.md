# Frozen Receipts: design and scoring plan (FOR REVIEW: nothing here is active)

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

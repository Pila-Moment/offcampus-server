# Honest Receipts and scores (PR 1)

## What players see
- **Receipts rounds (1 and 3) are answer-only.** Tap YES or NO, then LOCK IT IN. No % guess, no points, and the made-up percentages are no longer sent to the page.
  - "ANSWER LOCKED" shows **only after the server confirms the save**. It says "Your answer isn't shown to other players" (not "anonymous": answers are stored against a browser id), plus how many have answered so far today.
  - While waiting it says "SAVING YOUR ANSWER… You can keep playing". If there's no reply within 8 seconds, or the save fails, it says "COULDN'T SAVE YOUR ANSWER" with TRY AGAIN. The player can move on at any time and the game always finishes.
  - The rule shown is "A real result only shows if a question gets 30+ answers in one day. With fewer, no % is shown." That matches the server exactly: the home page shows yesterday's question only if it got 30+ answers that day. Cross-day collection doesn't exist yet and isn't mentioned.
- **A day is out of 3,000** (Showdown, Showdown, Drop the Pin, 1,000 each), on the score card, the share text and the share image.
- **No YES/NO split is ever shown for an open question,** for Queen's or for a crew. The API only returns the count.
- **Queen's Survey Showdown** keeps its name. Its board is labelled "OUR BOARD, NOT A SURVEY" all through the round, and "OUR BOARD SAYS… (NOT A SURVEY)" at the reveal. The party Showdown says "OFF CAMPUS BOARD · NOT A SURVEY".
- **Prize page retired** (`/prizes.html` redirects to `/`). The prize claims are gone from the home page description, link previews and the preview image.
- **Brand demo** (`daily.html?spot=…`, made with link.html):
  - A red "BRAND DEMO · SAMPLE ONLY · NOTHING IS REAL" band shows on every screen.
  - It runs on the 3,000 scale (the sample spin unlocks at 1,500).
  - No "beat X% of Queen's" claim: the stamp says "DEMO RUN · SAMPLE SCORE".
  - Wins say "SAMPLE: YOU WON", the code says "SAMPLE CODE · NOT REDEEMABLE", and redeeming says "DEMO: HOW STAFF WOULD REDEEM IT".
  - It sends nothing to the server.
- **Brands page:** an "EARLY CONCEPT" notice at the top. Every benefit, control, report, event and deal is worded as a proposal ("would", "could", "proposed", "not built yet"), and there are no January dates or "within a day" promises.
- **Home page cache:** stored under a new key (`cache/home-v2`), so anything worked out under the old rules (10+ answers, out of 5,000) is never served.

## Old scores (out of 5,000)
**Nothing stored is changed.** Every score record and player history stays exactly as saved.

When the server reads any score (today's board, week, league, streak best, recap, crew of the week), it works it out again from the three scored rounds only (`honestTotal` in `lib/crews.mjs`). For example, an old 4,100 (900, 800, 900, 700, 800) becomes 2,300 out of 3,000.

So every day, every week and every league compares on the same 3,000 scale, before and after the change. The points from guessing a made-up % are simply no longer counted.

**On the deploy day:** someone who played earlier that day on the old page keeps their single score, read the honest way.
- A phone with an old saved result shows it the honest way too.
- The phone's local "best" is reset once and then refilled from the server.
- A page left open from before the update still works: the server ignores any Receipts points it sends.

**Weekly stakes and last week's winner/loser** use the same honest totals. Last week's order stays the same in most cases. It can change if someone's lead came from Receipts guesses.

**The total sent by the page is no longer trusted.** The server adds up the three scored rounds itself. Each round is still limited to 0–1,000, and Showdown and Pin points are still worked out on the phone. That's the remaining, documented gap: server-checked rounds come in a later PR.

## What's next (not in this PR)
The 30-answer frozen-poll system:
- A question collects answers across days, up to 14.
- It freezes once it reaches 30 answers.
- Later Dailies use those frozen numbers as real guess targets, so Receipts scores again.

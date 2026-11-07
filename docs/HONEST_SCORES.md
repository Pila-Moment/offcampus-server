# Honest Receipts and scores (PR 1)

## What players see
- **Receipts rounds (1 and 3) are answer-only.**
  - You tap YES or NO, then LOCK IT IN, and see "ANSWER LOCKED · Saved anonymously" with how many people have answered today.
  - There's no % guess and no points.
  - The made-up percentages are no longer sent to the page at all.
- **A day is out of 3,000** (Showdown, Showdown, Drop the Pin, 1,000 each). This shows on the score card, the share text and the share image.
- **The real result of a Receipts question** shows on the home page the day after, but only once it has 30+ answers.
  - It reads "X% said yes · Y of N Off Campus players who answered".
  - The question is closed by then, so nobody's answer can be worked out from the number moving.
- **No YES/NO split is ever shown for an open question,** for Queen's or for a crew. The API only returns the count.
- **Showdown boards** say "OUR BOARD SAYS… (NOT A SURVEY)". The party Showdown no longer claims "We asked 100 Queen's students".
- **The prize page is retired.** `/prizes.html` redirects to `/`. Prize claims are gone from the home page description, link previews and the preview image.

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

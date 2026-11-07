# Competition integrity: what is and isn't verified

**Short version:** the Daily, crews and the House League are fine for bragging rights. **They are not verified and must not decide prizes.**

## Not verified
- **Players are browser ids.**
  - Anyone can make a new id by clearing the browser, using another browser or private tab, or sending requests with a made-up id.
  - So one person can be many "players". In particular, one person could fill a house's 3-player minimum alone.
  - Nicknames and the 4-digit PIN don't prove who someone is.
- **Showdown and Drop the Pin are scored on the phone.**
  - The server only checks each round is 0–1,000 and works out the total itself.
  - Someone sending requests by hand could claim 1,000 on those rounds.
- **There are no rate limits per person or network,** beyond the one-score-per-id-per-day rule.

## Verified on the server
- **One first score per id per day.** It's written once; concurrent or repeated submissions can't replace it.
- **The day's total** is added up on the server. Receipts points sent by the page are ignored.
- **Frozen Receipts guesses** (when switched on) are scored on the server against a result the page never sees first. The first guess counts.
- **One ranked house per id per week.**

## Guard rails in the code
- `VERIFIED = false` in `lib/houses.mjs`. `/api/league` always returns `verified:false, prizes:false`, and a test checks it.
- **Nothing gives out a prize.** The House League page says "Bragging rights only. There are no prizes in the House League." The prize spin only exists in the clearly labelled brand demo (`?spot=`), which sends nothing to the server.

## Before any leaderboard could carry a prize (all of these, and a legal review)
1. **Verified identity:** at least one real account per person (for example, a school email check) instead of browser ids.
2. **Every round scored on the server:** Showdown and Pin answers sent and checked there, like the frozen Receipts guess.
3. **Rate limits and duplicate-device checks.**
4. **Contest rules:** no purchase necessary, a skill-testing question, eligibility, and Ontario/Canada contest law reviewed.
5. **Change `VERIFIED` only after 1–4.** Until then, any sponsored "challenge" can be for fun and recognition only.

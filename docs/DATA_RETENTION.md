# Answers: what's stored, for how long, and the proposal (FOR JOSH'S DECISION)

Nothing here is switched on. `OC_FROZEN_RECEIPTS` is off everywhere, so no 14-day collection happens.

## How a player is identified
- A random id is made in the browser (`oc-pid` in local storage). There's no name, email or account.
- A player can add a nickname (shown to their crew or house) and a 4-digit PIN to log in on another phone. The PIN is stored hashed.

## What's stored today (live, before any frozen Receipts)
| Key | What | How long now |
|---|---|---|
| `ans/DAY/ID` | Each Receipts YES/NO and typed Showdown answers, for that day, by browser id | **Kept with no end date** |
| `agg/DAY/ROUND` | YES and total counts for a day's question | Kept |
| `score/DAY/ID`, `player/ID` | Scores, nickname, crews, house, the last 60 days of history | Kept (history trimmed to 60 days) |
| `src/SOURCE/ID`, `sug/…` | Where a player first came from; question suggestions (optional @ for credit) | Kept |
| `clubp/…` | Club game answers and guesses | Kept |

Already today, individual Receipts answers (`ans/`) sit next to a browser id with no deletion. That's worth fixing even if frozen Receipts never ships.

## Frozen Receipts as built (switch off)
- `rqa/QID/ID` = `{ a:'Y'|'N', day, at }`. One record per player per question. **The code does not delete these.**
- They're used for three things:
  1. counting (n and YES) while the question collects,
  2. making sure nobody is counted twice,
  3. not offering a question again to someone who answered.
- `rqf/QID` (the frozen n and YES) has **no player ids** in it. `rqg/DAY/ID` stores a player's guess and its points, which is part of their score.

## Proposal: keep individual answers only while they're needed
1. **While a question collects** (up to 14 days): keep `rqa/QID/ID`. It's needed for counting and for not counting anyone twice.
2. **Once it freezes or expires:** delete every `rqa/QID/*` for it within 1 day. A small daily clean-up runs on the first request after 4am.
   - Keep only the frozen numbers (`rqf`: n and YES, no ids).
   - An expired question keeps nothing but a note that it expired.
3. **Not counting anyone twice after deletion:** it isn't needed.
   - A closed question takes no more answers (the server refuses), and the OPEN QUESTIONS card never offers closed ones.
   - If a question **repeats** later in the Daily, it becomes a new collection only if we decide so (new version `v`). Otherwise a closed question's repeat is answer-only and isn't saved.
4. **Guesses (`rqg`):** keep them with the day's score, trimmed like score history (60 days).
5. **The same rule for the existing `ans/DAY/ID`:** delete individual answers once the day is over and its counts (`agg`) are saved, within 1 day.
   - Typed Showdown answers: keep only the text with no id, or delete after 30 days. Josh to choose.
6. **Players can ask for deletion:** a "delete my answers" button, matched by their browser id. It removes `ans/*/ID`, `rqa/*/ID` and `rqg/*/ID` (frozen numbers stay, they hold no ids). Today the only way would be a manual request.

## What players should be told (draft, for a privacy page and next to the first Receipts question)
> Your answers are saved with a random code stored on this phone, not your name. Other players never see your answer, only totals, and only once 30 or more people have answered. We delete individual answers once a question closes (within 15 days). The totals stay. You can delete your answers any time from the menu.

Showing this requires the privacy page, which is still on the to-do list.

## Decisions for Josh
- Approve the retention rule above, or a shorter one.
- Approve deleting the existing `ans/` individual answers older than 1 day in production. That's a one-off clean-up and needs a backup first.
- Typed Showdown answers: delete after 30 days, or keep the text only.
- Then, separately, whether to switch on frozen Receipts collection at all.

// FROZEN RECEIPTS (behind a switch, OFF by default). Design: docs/FROZEN_RECEIPTS_PLAN.md
//
// A Receipts question collects real YES/NO answers for up to 14 days. When 30 different players have answered, the result
// freezes once and never moves. From the next Daily on, it can be the day's guessing target: everyone gets the same one,
// the server scores the guess, and the real result is only shown after you guess. With fewer than 30 by day 14 it expires
// and its % is never shown anywhere.
//
// Keys (each written once, "only if new", so two answers or guesses arriving together can't overwrite each other):
//   rqa/QID/PLAYER  -> { a:'Y'|'N', day, at }   one answer per player per question (the first one counts)
//   rqf/QID         -> { n, yes, day, at }      the frozen result
//   rqt/DAY         -> { id }                   that day's guessing target (id null = none that day)
//   rqu/QID         -> { day }                  this question was already used as a target
//   rqg/DAY/PLAYER  -> { guess, points, at }    the first guess counts
//   rqpub/QID       -> { day }                  this result has been shown publicly (home page)
import BANK0 from './rq-bank.mjs';

// ---------- settings you can change ----------
export const FREEZE_AT = 30;        // different players needed to freeze a result
export const WINDOW_DAYS = 14;      // days a question collects answers (its first day + 13)
export const PTS_PER_PCT_OFF = 25;  // every 1 point off the real % costs 25 (out of 1,000)
export const OPEN_MAX = 3;          // optional open questions offered after the Daily
export const GUESS_ROUND = 2;       // the Daily's 3rd round becomes the guess when there's a target
const LEGACY_PUBLIC_MIN = 30;       // a question the old home page could already have shown (30+ answers in its day)

let enabled = (() => { try { return globalThis.process && process.env && process.env.OC_FROZEN_RECEIPTS === '1'; } catch (e) { return false; } })();
export const frozenEnabled = () => enabled;
export const setFrozenEnabled = v => { enabled = !!v; };   // tests and the local demo server only
let BANK = BANK0, byId = new Map(BANK.map(q => [q.id, q]));
export const setBank = list => { BANK = list; byId = new Map(list.map(q => [q.id, q])); };   // tests only

const r1 = x => Math.round(x * 10) / 10;
const lastDay = q => q.firstDay + WINDOW_DAYS - 1;
const once = async (store, key, value) => { const r = await store.setJSON(key, value, { onlyIfNew:true }); return !r || r.modified !== false; };

async function answersOf(store, id){
  const keys = (await store.list({ prefix:`rqa/${id}/` })).blobs.map(b => b.key);
  return (await Promise.all(keys.map(async k => ({ k, a:await store.get(k, { type:'json' }) })))).filter(x => x.a);
}
const tally = list => ({ n:list.length, yes:list.filter(x => x.a.a === 'Y').length });
// The frozen result is always the first FREEZE_AT answers (by time, then player), even if many arrive at once.
const firstN = list => list.slice().sort((x, y) => x.a.at - y.a.at || x.k.localeCompare(y.k)).slice(0, FREEZE_AT);
async function statusOf(store, q, day){
  const f = await store.get('rqf/' + q.id, { type:'json' });
  if (f) return { st:'frozen', f };
  if (day < q.firstDay) return { st:'upcoming' };
  if (day > lastDay(q)) return { st:'expired' };
  return { st:'collecting' };
}
async function wasPublic(store, q){
  if (await store.get('rqpub/' + q.id, { type:'json' })) return true;
  const a = await store.get(`agg/${q.firstDay}/${q.round}`, { type:'json' });   // the old home page showed closed days with 30+
  return !!(a && a.n >= LEGACY_PUBLIC_MIN);
}
// The day's guessing target: picked once (the first request that day), the same for everyone.
export async function targetOf(store, day){
  const have = await store.get('rqt/' + day, { type:'json' }); if (have) return have.id;
  const cands = [];
  for (const q of BANK) {
    const f = await store.get('rqf/' + q.id, { type:'json' });
    if (!f || f.day >= day) continue;                                    // frozen before today only
    if (await store.get('rqu/' + q.id, { type:'json' })) continue;       // never the same target twice
    if (await wasPublic(store, q)) continue;                              // never a result people could already have seen
    cands.push({ q, f });
  }
  cands.sort((a, b) => a.f.day - b.f.day || a.q.firstDay - b.q.firstDay || a.q.id.localeCompare(b.q.id));
  const pick = cands[0] ? cands[0].q.id : null;
  if (await once(store, 'rqt/' + day, { id:pick, at:Date.now() }) && pick) await once(store, 'rqu/' + pick, { day });
  return ((await store.get('rqt/' + day, { type:'json' })) || {}).id ?? null;   // whatever was saved first wins
}
// Points for the day's guess round, for POST /api/score (null = there's no target today: the round stays answer-only)
export async function guessPointsFor(store, day, pid){
  if (!enabled) return null;
  const t = await targetOf(store, day); if (!t) return null;
  const g = await store.get(`rqg/${day}/${pid}`, { type:'json' }); return g ? g.points : 0;
}
// Closed results the home page may show: targets whose day is over. Marks them public.
export async function revealable(store, day){
  const out = [];
  for (const q of BANK) {
    const u = await store.get('rqu/' + q.id, { type:'json' }); if (!u || u.day >= day) continue;
    const f = await store.get('rqf/' + q.id, { type:'json' }); if (!f) continue;
    await once(store, 'rqpub/' + q.id, { day }); out.push({ q:q.text, yes:f.yes, n:f.n, day:u.day });
  }
  return out.sort((a, b) => b.day - a.day).slice(0, 2);
}

export async function receiptRoutes({ req, store, url, p, body, json, validId, day, now }){
  if (!p.startsWith('/api/rq/')) return null;
  if (!enabled) return json(404, { error:'not enabled' });
  // POST /api/rq/answer { playerId, qid, yes }   one answer per player per question; only the count comes back
  if (req.method === 'POST' && p === '/api/rq/answer') {
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const q = byId.get(String(b.qid || '')); if (!q) return json(404, { error:'unknown question' });
    if (typeof b.yes !== 'boolean') return json(400, { error:'yes or no' });
    const s = await statusOf(store, q, day);
    if (s.st === 'upcoming') return json(409, { error:'not open yet' });
    if (s.st === 'expired') return json(409, { error:'closed' });
    const fresh = await once(store, `rqa/${q.id}/${b.playerId}`, { a:b.yes ? 'Y' : 'N', day, at:now });
    if (s.st === 'frozen') return json(200, { ok:true, already:!fresh, frozen:true });   // saved (so you're never asked again) but the result is fixed
    const all = await answersOf(store, q.id), c = tally(all);
    if (c.n >= FREEZE_AT) { const f = tally(firstN(all)); await once(store, 'rqf/' + q.id, { n:f.n, yes:f.yes, day, at:now }); return json(200, { ok:true, already:!fresh, frozen:true }); }
    return json(200, { ok:true, already:!fresh, n:c.n, need:FREEZE_AT, lastDay:lastDay(q) });   // a count only, never a split
  }
  // GET /api/rq/today?playerId=   today's target question (text only). The result comes back only if you've already guessed.
  if (req.method === 'GET' && p === '/api/rq/today') {
    const id = url.searchParams.get('playerId'); const t = await targetOf(store, day);
    const q = t ? byId.get(t) : null; const g = q && validId(id) ? await store.get(`rqg/${day}/${id}`, { type:'json' }) : null;
    const res = g ? await store.get('rqf/' + q.id, { type:'json' }) : null;
    return json(200, { enabled:true, day, round:GUESS_ROUND, max:q ? 4000 : 3000, target:q ? { qid:q.id, text:q.text } : null,
      guessed:g ? { guess:g.guess, points:g.points, n:res.n, yes:res.yes, pct:r1(100 * res.yes / res.n) } : null });
  }
  // POST /api/rq/guess { playerId, day, guess }   scored here; a retry gets the first guess back
  if (req.method === 'POST' && p === '/api/rq/guess') {
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    if (Number(b.day) !== day) return json(409, { error:'wrong day', day });
    const g = Math.round(Number(b.guess)); if (!Number.isFinite(g) || g < 0 || g > 100) return json(400, { error:'guess 0-100' });
    const t = await targetOf(store, day); if (!t) return json(409, { error:'no target today' });
    const f = await store.get('rqf/' + t, { type:'json' }); const pct = 100 * f.yes / f.n;
    const fresh = await once(store, `rqg/${day}/${b.playerId}`, { guess:g, points:Math.max(0, Math.round(1000 - PTS_PER_PCT_OFF * Math.abs(g - pct))), at:now });
    const first = await store.get(`rqg/${day}/${b.playerId}`, { type:'json' });
    return json(200, { ok:true, already:!fresh, guess:first.guess, points:first.points, n:f.n, yes:f.yes, pct:r1(pct), qid:t });
  }
  // GET /api/rq/open?playerId=   up to 3 open questions you haven't answered (text only, never counts)
  if (req.method === 'GET' && p === '/api/rq/open') {
    const id = url.searchParams.get('playerId'); if (!validId(id)) return json(400, { error:'bad player' });
    const out = [];
    for (const q of [...BANK].sort((a, b) => lastDay(a) - lastDay(b))) {   // closest to its deadline first
      if (out.length >= OPEN_MAX) break;
      if (q.firstDay >= day || day > lastDay(q)) continue;                 // today's own questions are in today's Daily
      if (await store.get('rqf/' + q.id, { type:'json' })) continue;
      if (await store.get(`rqa/${q.id}/${id}`, { type:'json' })) continue;
      out.push({ qid:q.id, text:q.text, daysLeft:lastDay(q) - day });
    }
    return json(200, { open:out });
  }
  return json(404, { error:'not found' });
}

import { clubRoutes, clubStats } from './clubs.mjs';
// Crews: friend groups that compare their daily scores.
// The store is Netlify Blobs in production (see netlify/functions/api.mjs) and an in-memory map in the tests.
// Keys:  crew/CODE -> { name, members[], by, at }   player/ID -> { nick, crews[], at }   score/DAY/ID -> { total, pts[], at }
//
// HONEST SCORES (PR 1): Receipts rounds (1 and 3 of the five) are answer-only until real, frozen results exist.
// Only Showdown, Showdown and Drop the Pin score, so a day is out of 3,000.
// Older score records (out of 5,000, with points against made-up Receipts %) are never changed:
// every board, week, league and streak works the score out again from the three scored rounds when it reads it.

// ---------- settings you can change ----------
export const FIRST_DAY = '2026-11-03';   // must match FIRST_DAY in the game (daily.html)
export const SCORED_ROUNDS = [1, 3, 4];   // Showdown, Showdown, Drop the Pin. Receipts (0 and 2) score nothing for now.
export const DAY_MAX = SCORED_ROUNDS.length * 1000;   // 3,000
const MAX_CREW_MEMBERS = 60;
const MAX_CREWS_PER_PLAYER = 10;
const NICK_MAX = 16, CREW_NAME_MAX = 28;
const STREAK_LOOKBACK = 30;
const LEAGUE_DAYS = 30;          // the crew league counts the last 30 days
const HIST_KEEP = 60;            // days of scores kept on each player for the league
const TEXT_MAX = 60, TEXTS_PER_ROUND = 10;
const LOGIN_TRIES = 5, LOCK_MINUTES = 15;   // wrong PINs allowed before a name is locked for a while
const STAKE_MAX = 40;            // characters for "winner gets" / "loser has to"
const SUGGEST_PER_DAY = 5, SUGGEST_MAX = 160, SUGGEST_LIST = 200;   // question suggestions: per player per day, length, how many Josh sees
const HOME_MIN = 30;             // real answers needed before a closed (yesterday's) Receipts result shows on the home page
const CREW_OF_WEEK_MIN = 3;      // players needed in a crew this week to be crew of the week
const HOME_CACHE_MS = 5 * 60e3;  // the home page numbers are worked out at most every 5 minutes

export function torontoDay(now = Date.now()){   // Daily number: No. 1 on FIRST_DAY, a new one at 4am Toronto time
  const s = new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date(now - 4 * 3600e3));
  return Math.max(1, Math.round((Date.parse(s) - Date.parse(FIRST_DAY)) / 864e5) + 1);
}
// Weeks run Monday to Sunday. Day 1 (FIRST_DAY) is a Tuesday.
const FIRST_DOW = new Date(FIRST_DAY + 'T12:00:00Z').getUTCDay();   // 0 = Sunday
export const dowOf = d => (FIRST_DOW + d - 1) % 7;
export const mondayOf = d => d - ((dowOf(d) + 6) % 7);
const CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
const cleanText = (s, max) => String(s || '').replace(/[\u0000-\u001f<>]/g, '').replace(/\s+/g, ' ').trim().slice(0, max);
const validId = id => typeof id === 'string' && /^[a-z0-9]{12,40}$/i.test(id);
const json = (status, body) => new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' } });

async function newCode(store){
  for (let tries = 0; tries < 20; tries++) {
    const b = crypto.getRandomValues(new Uint8Array(6)); let c = ''; for (let i = 0; i < 6; i++) c += CODE_CHARS[b[i] % CODE_CHARS.length];
    if (!(await store.get('crew/' + c, { type:'json' }))) return c;
  }
  throw new Error('no code');
}
// The honest version of a day's points: Receipts rounds become null, the total is the three scored rounds.
export const honestPts = p => Array.from({ length:5 }, (_, i) => SCORED_ROUNDS.includes(i) ? Math.max(0, Math.min(1000, Math.round(Number((p || [])[i]) || 0))) : null);
export const honestTotal = p => honestPts(p).reduce((a, x) => a + (x || 0), 0);
const honestHist = h => Object.fromEntries(Object.entries(h || {}).map(([d, x]) => [d, { t:honestTotal(x.p), p:honestPts(x.p) }]));
async function getPlayer(store, id){ return (await store.get('player/' + id, { type:'json' })) || { nick:'Player', crews:[], at:Date.now() }; }
async function streakOf(store, id, day){
  let n = 0, d = day;
  if (!(await store.get(`score/${d}/${id}`, { type:'json' }))) d--;
  for (; d > 0 && n < STREAK_LOOKBACK; d--) { if (await store.get(`score/${d}/${id}`, { type:'json' })) n++; else break; }
  return n;
}
async function crewView(store, code, day, me){
  const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
  const members = await Promise.all(c.members.map(async id => {
    const [p, s, streak] = await Promise.all([getPlayer(store, id), store.get(`score/${day}/${id}`, { type:'json' }), streakOf(store, id, day)]);
    return { nick:p.nick || 'Player', you:id === me, total:s ? honestTotal(s.pts) : null, pts:s ? honestPts(s.pts) : null, streak };
  }));
  members.sort((a, b) => (b.total ?? -1) - (a.total ?? -1));
  return { code, name:c.name, day, played:members.filter(m => m.total !== null).length, size:members.length, members };
}

// Round order in the daily game is Receipts, Showdown, Receipts, Showdown, Pin. Each game's number is points per round (out of 1,000).
// Receipts has no "best at" while it's answer-only.
const GAMES = { showdown:[1, 3], pin:[4] };
async function histOf(store, id, day){
  const pl = await getPlayer(store, id);
  if (pl.hist) return { pl, hist:honestHist(pl.hist) };
  const hist = {};   // players from before the league existed: read their score records
  await Promise.all(Array.from({ length:Math.min(LEAGUE_DAYS, day) }, (_, k) => day - k).map(async d => { const s = await store.get(`score/${d}/${id}`, { type:'json' }); if (s) hist[d] = { t:honestTotal(s.pts), p:honestPts(s.pts) }; }));
  return { pl, hist };
}
async function leagueView(store, code, day, me){
  const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
  const rows = await Promise.all(c.members.map(async id => ({ id, ...(await histOf(store, id, day)) })));
  const from = day - LEAGUE_DAYS + 1;
  const wins = {};   // a win = top score in the crew that day (ties both win)
  for (let d = from; d <= day; d++) {
    const best = Math.max(-1, ...rows.map(r => r.hist[d] ? r.hist[d].t : -1));
    if (best >= 0 && rows.filter(r => r.hist[d]).length >= 2) rows.forEach(r => { if (r.hist[d] && r.hist[d].t === best) wins[r.id] = (wins[r.id] || 0) + 1; });
  }
  const members = rows.map(r => {
    const days = Object.keys(r.hist).map(Number).filter(d => d >= from && d <= day);
    const tot = days.reduce((a, d) => a + r.hist[d].t, 0);
    const game = g => { const v = days.flatMap(d => GAMES[g].map(i => (r.hist[d].p || [])[i] ?? 0)); return v.length ? Math.round(v.reduce((a, b) => a + b, 0) / v.length) : null; };
    let streak = 0, d = r.hist[day] ? day : day - 1; while (d > 0 && r.hist[d] && streak < STREAK_LOOKBACK) { streak++; d--; }
    return { nick:r.pl.nick || 'Player', you:r.id === me, played:days.length, wins:wins[r.id] || 0, avg:days.length ? Math.round(tot / days.length) : null,
      best:days.length ? Math.max(...days.map(d => r.hist[d].t)) : null, streak, showdown:game('showdown'), pin:game('pin') };
  });
  members.sort((a, b) => b.wins - a.wins || (b.avg ?? -1) - (a.avg ?? -1));
  const king = g => { const q = members.filter(m => m[g] !== null && m.played >= 1).sort((a, b) => b[g] - a[g]); return q.length ? { nick:q[0].nick, you:q[0].you, score:q[0][g] } : null; };
  return { code, name:c.name, day, days:LEAGUE_DAYS, members, best:{ showdown:king('showdown'), pin:king('pin') } };
}

// ---------- the crew's week: totals Monday to Sunday, and the stake ----------
// crew.stakes = { MONDAY_DAY: { win, lose } }  the latest one set on or before a week counts for that week
const stakeFor = (c, mon) => { const ks = Object.keys(c.stakes || {}).map(Number).filter(k => k <= mon).sort((a, b) => b - a); return ks.length ? { win:c.stakes[ks[0]].win, lose:c.stakes[ks[0]].lose } : null; };   // never sends who set it
function weekTable(rows, from, to){
  const members = rows.map(r => { const days = Object.keys(r.hist).map(Number).filter(d => d >= from && d <= to);
    return { id:r.id, nick:r.pl.nick || 'Player', total:days.reduce((a, d) => a + r.hist[d].t, 0), played:days.length }; });
  members.sort((a, b) => b.total - a.total || b.played - a.played);
  return members;
}
async function weekView(store, code, day, me){
  const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
  const rows = await Promise.all(c.members.map(async id => ({ id, ...(await histOf(store, id, day)) })));
  const mon = mondayOf(day), last = mon - 7;
  const strip = m => ({ nick:m.nick, you:m.id === me, total:m.total, played:m.played });
  const thisWeek = weekTable(rows, Math.max(1, mon), day);
  let lastWeek = null;
  if (last + 6 >= 1) {
    const t = weekTable(rows, Math.max(1, last), last + 6).filter(m => m.played > 0);
    if (t.length >= 2) {
      const top = t[0].total, bottom = t[t.length - 1].total;
      lastWeek = { winners:t.filter(m => m.total === top).map(strip), losers:t.filter(m => m.total === bottom).map(strip), stake:stakeFor(c, last), played:t.length, size:c.members.length };
    }
  }
  return { code, name:c.name, day, from:Math.max(1, mon), to:mon + 6, daysLeft:mon + 6 - day, stake:stakeFor(c, mon), members:thisWeek.map(strip), played:thisWeek.filter(m => m.played).length, size:c.members.length, lastWeek };
}

// ---------- Josh: hidden from the stats + the admin key ----------
// admin/key -> { key, by }   admin/hidden -> { ids:[...] }
async function hiddenIds(store){ const h = await store.get('admin/hidden', { type:'json' }); return new Set(h ? h.ids : []); }
async function hide(store, id){ const h = (await store.get('admin/hidden', { type:'json' })) || { ids:[] }; if (!h.ids.includes(id)) { h.ids.push(id); await store.setJSON('admin/hidden', h); } }
export async function isAdmin(store, k){
  if (!k || typeof k !== 'string') return false;
  try { if (globalThis.process && process.env && process.env.OC_ADMIN_KEY && k === process.env.OC_ADMIN_KEY) return true; } catch (e) {}
  const a = await store.get('admin/key', { type:'json' }); return !!(a && a.key === k);
}

// ---------- save your spot: nickname + 4-digit PIN ----------
// nick/<name> -> { id }   player record gets { salt, pinHash }   fail/<name> -> { n, until }
const nickKey = n => 'nick/' + cleanText(n, NICK_MAX).toLowerCase().replace(/\s+/g, ' ');
const validPin = p => typeof p === 'string' && /^\d{4}$/.test(p);
async function hashPin(pin, salt){ const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(salt + ':' + pin)); return Array.from(new Uint8Array(d), b => b.toString(16).padStart(2, '0')).join(''); }
function summary(pl, day){   // what a new browser needs to pick up where this player left off
  const hist = honestHist(pl.hist), days = Object.keys(hist).map(Number).sort((a, b) => a - b);
  let n = 0, d = hist[day] ? day : day - 1; while (d > 0 && hist[d]) { n++; d--; }
  return { today:hist[day] ? { total:hist[day].t, pts:hist[day].p } : null, streak:{ last:days.length ? days[days.length - 1] : 0, n, best:days.reduce((m, x) => Math.max(m, hist[x].t), 0), days:days.length } };
}

// ---------- real answers ----------
// ans/DAY/ID -> { yn:{ round:'Y'|'N' }, txt:{ round:[...] } }   agg/DAY/ROUND -> { yes, n }
// No crew or campus YES/NO split is ever sent for an open question: a split that moves with each vote gives away the newest vote.
// yesterday (or any day) for one crew, without streaks: who played, who won, by how much
async function dayResults(store, code, d, me){
  const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
  const rows = (await Promise.all(c.members.map(async id => { const [p, s] = await Promise.all([getPlayer(store, id), store.get(`score/${d}/${id}`, { type:'json' })]); return { nick:p.nick || 'Player', you:id === me, total:s ? honestTotal(s.pts) : null }; })))
    .filter(r => r.total !== null).sort((a, b) => b.total - a.total);
  const meRow = rows.findIndex(r => r.you);
  return { day:d, played:rows.length, size:c.members.length, top:rows[0] || null, second:rows[1] || null, myRank:meRow >= 0 ? meRow + 1 : null, myTotal:meRow >= 0 ? rows[meRow].total : null };
}

export async function handle(req, store, now = Date.now()){
  const url = new URL(req.url);
  const p = url.pathname.replace(/\/+$/, '');
  const day = torontoDay(now);
  const body = async () => { const t = await req.text(); if (t.length > 16384) throw new Error('too big'); return t ? JSON.parse(t) : {}; };
  try {
    if (p === '/api/health') return json(200, { ok:true, day });
    if (p.startsWith('/api/clubs')) { const r = await clubRoutes({ req, store, now, url, p, body, json, cleanText, validId, newCode, getPlayer }); if (r) return r; }

    // POST /api/score  { playerId, nick, day, pts[5] }  (the first score of the day counts)
    // Receipts rounds may be null (answer-only). Anything sent for them is ignored, and the total is worked out here, not taken from the page.
    if (req.method === 'POST' && p === '/api/score') {
      const b = await body();
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      if (Number(b.day) !== day) return json(409, { error:'wrong day', day });
      const raw = Array.isArray(b.pts) ? b.pts : [];
      if (raw.length !== 5 || raw.some((x, i) => SCORED_ROUNDS.includes(i) ? !(Number.isFinite(Number(x)) && x !== null && Number(x) >= 0 && Number(x) <= 1000) : !(x === null || x === undefined || (Number.isFinite(Number(x)) && Number(x) >= 0 && Number(x) <= 1000))))
        return json(400, { error:'bad score' });
      const pts = honestPts(raw), total = honestTotal(raw);
      const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, NICK_MAX); if (nick) pl.nick = nick;
      if (!pl.src) {   // where this player first came from (?ref= on the link they opened)
        pl.src = String(b.src || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 24) || 'direct'; pl.first = day;
        await store.setJSON(`src/${pl.src}/${b.playerId}`, { first:day });
      }
      await store.setJSON('player/' + b.playerId, pl);
      const key = `score/${day}/${b.playerId}`; const had = await store.get(key, { type:'json' });
      if (!had) {
        await store.setJSON(key, { total, pts, max:DAY_MAX, at:now });
        pl.hist = pl.hist || {}; pl.hist[day] = { t:total, p:pts };
        for (const d of Object.keys(pl.hist)) if (+d <= day - HIST_KEEP) delete pl.hist[d];
        await store.setJSON('player/' + b.playerId, pl);
      }
      return json(200, { ok:true, day, total:had ? honestTotal(had.pts) : total, max:DAY_MAX });
    }

    // POST /api/pin  { playerId, nick, pin }   saves your spot: this nickname + PIN logs you in anywhere
    if (req.method === 'POST' && p === '/api/pin') {
      const b = await body();
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      if (!validPin(b.pin)) return json(400, { error:'pin must be 4 numbers' });
      const nick = cleanText(b.nick, NICK_MAX); if (nick.length < 2) return json(400, { error:'pick a nickname' });
      const owner = await store.get(nickKey(nick), { type:'json' });
      if (owner && owner.id !== b.playerId) return json(409, { error:'that name is taken' });
      const pl = await getPlayer(store, b.playerId);
      if (pl.nick && pl.pinHash && nickKey(pl.nick) !== nickKey(nick)) await store.setJSON(nickKey(pl.nick), { id:null });   // renamed: free the old name
      pl.nick = nick; pl.salt = pl.salt || crypto.getRandomValues(new Uint32Array(2)).join('-'); pl.pinHash = await hashPin(b.pin, pl.salt);
      await store.setJSON('player/' + b.playerId, pl); await store.setJSON(nickKey(nick), { id:b.playerId });
      return json(200, { ok:true, nick });
    }

    // POST /api/login  { nick, pin }   back in on a new phone or browser
    if (req.method === 'POST' && p === '/api/login') {
      const b = await body(); const nk = nickKey(b.nick || '');
      if (!validPin(b.pin) || nk === 'nick/') return json(400, { error:'name and 4-number pin' });
      const fk = 'fail/' + nk.slice(5), f = (await store.get(fk, { type:'json' })) || { n:0, until:0 };
      if (f.until > now) return json(429, { error:'too many tries, wait a few minutes' });
      const owner = await store.get(nk, { type:'json' }); const pl = owner && owner.id ? await store.get('player/' + owner.id, { type:'json' }) : null;
      if (!pl || !pl.pinHash || (await hashPin(b.pin, pl.salt)) !== pl.pinHash) {
        f.n++; if (f.n >= LOGIN_TRIES) { f.n = 0; f.until = now + LOCK_MINUTES * 60e3; } await store.setJSON(fk, f);
        return json(401, { error:'wrong name or pin' });
      }
      if (f.n) await store.setJSON(fk, { n:0, until:0 });
      return json(200, { ok:true, playerId:owner.id, nick:pl.nick, ...summary(pl, day) });
    }

    // POST /api/answer  { playerId, day, round, yes }  or  { playerId, day, round, texts:[...] }
    // Saves a real answer (first answer per round counts). Sends back only how many have answered: never a YES/NO split
    // while the question is open, for the campus or for any crew.
    if (req.method === 'POST' && p === '/api/answer') {
      const b = await body();
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      if (Number(b.day) !== day) return json(409, { error:'wrong day', day });
      const round = Number(b.round); if (!Number.isInteger(round) || round < 0 || round > 9) return json(400, { error:'bad round' });
      const key = `ans/${day}/${b.playerId}`, a = (await store.get(key, { type:'json' })) || { yn:{}, txt:{} };
      if (Array.isArray(b.texts)) {
        if (!a.txt[round]) { a.txt[round] = b.texts.slice(0, TEXTS_PER_ROUND).map(t => cleanText(t, TEXT_MAX)).filter(Boolean); await store.setJSON(key, a); }
        return json(200, { ok:true });
      }
      if (typeof b.yes !== 'boolean') return json(400, { error:'yes or no' });
      const aggKey = `agg/${day}/${round}`, agg = (await store.get(aggKey, { type:'json' })) || { yes:0, n:0 };
      if (!a.yn[round]) {
        a.yn[round] = b.yes ? 'Y' : 'N'; await store.setJSON(key, a);
        agg.n++; if (b.yes) agg.yes++; if (!agg.q && b.q) agg.q = cleanText(b.q, 160); await store.setJSON(aggKey, agg);
      }
      return json(200, { ok:true, queens:{ n:agg.n, hidden:true }, crews:[] });   // hidden + empty crews keep pages opened before this update working
    }

    // POST /api/crews  { playerId, nick, name }  makes a crew and joins it
    if (req.method === 'POST' && p === '/api/crews') {
      const b = await body();
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      const name = cleanText(b.name, CREW_NAME_MAX); if (!name) return json(400, { error:'name your crew' });
      const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, NICK_MAX); if (nick) pl.nick = nick;
      if (pl.crews.length >= MAX_CREWS_PER_PLAYER) return json(400, { error:'too many crews' });
      const code = await newCode(store);
      await store.setJSON('crew/' + code, { name, members:[b.playerId], by:b.playerId, at:now });
      pl.crews.push(code); await store.setJSON('player/' + b.playerId, pl);
      return json(200, await crewView(store, code, day, b.playerId));
    }

    // POST /api/crews/CODE/join  { playerId, nick }
    let m = p.match(/^\/api\/crews\/([A-Z0-9]{6})\/join$/);
    if (req.method === 'POST' && m) {
      const b = await body(); const c = await store.get('crew/' + m[1], { type:'json' });
      if (!c) return json(404, { error:'crew not found' });
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, NICK_MAX); if (nick) pl.nick = nick;
      if (!c.members.includes(b.playerId)) {
        if (c.members.length >= MAX_CREW_MEMBERS) return json(400, { error:'crew is full' });
        if (pl.crews.length >= MAX_CREWS_PER_PLAYER) return json(400, { error:'too many crews' });
        c.members.push(b.playerId); await store.setJSON('crew/' + m[1], c);
        pl.crews.push(m[1]);
      }
      await store.setJSON('player/' + b.playerId, pl);
      return json(200, await crewView(store, m[1], day, b.playerId));
    }

    // GET /api/crews/CODE/week?playerId=   this week's totals (Monday to Sunday), the stake, and last week's winner and loser
    m = p.match(/^\/api\/crews\/([A-Z0-9]{6})\/week$/);
    if (req.method === 'GET' && m) {
      const v = await weekView(store, m[1], day, url.searchParams.get('playerId')); if (!v) return json(404, { error:'crew not found' });
      return json(200, v);
    }
    // POST /api/crews/CODE/stake  { playerId, win, lose }   any member sets this week's stake
    m = p.match(/^\/api\/crews\/([A-Z0-9]{6})\/stake$/);
    if (req.method === 'POST' && m) {
      const b = await body(); const c = await store.get('crew/' + m[1], { type:'json' }); if (!c) return json(404, { error:'crew not found' });
      if (!validId(b.playerId) || !c.members.includes(b.playerId)) return json(403, { error:'members only' });
      const win = cleanText(b.win, STAKE_MAX), lose = cleanText(b.lose, STAKE_MAX); if (!win && !lose) return json(400, { error:'add a stake' });
      c.stakes = c.stakes || {}; c.stakes[mondayOf(day)] = { win, lose, by:b.playerId, at:now }; await store.setJSON('crew/' + m[1], c);
      return json(200, await weekView(store, m[1], day, b.playerId));
    }

    // GET /api/crews/CODE/league?playerId=   the crew's league table: wins, average, streak, and who's best at each game
    m = p.match(/^\/api\/crews\/([A-Z0-9]{6})\/league$/);
    if (req.method === 'GET' && m) {
      const v = await leagueView(store, m[1], day, url.searchParams.get('playerId')); if (!v) return json(404, { error:'crew not found' });
      return json(200, v);
    }

    // GET /api/crews/CODE?playerId=   today's board
    m = p.match(/^\/api\/crews\/([A-Z0-9]{6})$/);
    if (req.method === 'GET' && m) {
      const v = await crewView(store, m[1], day, url.searchParams.get('playerId')); if (!v) return json(404, { error:'crew not found' });
      return json(200, v);
    }

    // GET /api/me?playerId=   all my crews with today's boards
    if (req.method === 'GET' && p === '/api/me') {
      const id = url.searchParams.get('playerId'); if (!validId(id)) return json(400, { error:'bad player' });
      const pl = await store.get('player/' + id, { type:'json' }); if (!pl) return json(200, { day, nick:null, crews:[] });
      const crews = (await Promise.all(pl.crews.map(c => crewView(store, c, day, id)))).filter(Boolean);
      if (url.searchParams.get('recap') && day > 1) await Promise.all(crews.map(async c => {
        c.yesterday = await dayResults(store, c.code, day - 1, id);
        if (dowOf(day) === 1) { const w = await weekView(store, c.code, day, id); c.lastWeek = w && w.lastWeek; }   // Mondays: last week's winner and loser
      }));
      return json(200, { day, nick:pl.nick, saved:!!pl.pinHash, crews });
    }

    // GET /api/stats   players today, crews, where players came from and who came back (for Josh). Josh's own browsers are left out.
    if (req.method === 'GET' && p === '/api/stats') {
      const hidden = await hiddenIds(store), cache = {};
      const ids = async d => cache[d] || (cache[d] = new Set((await store.list({ prefix:`score/${d}/` })).blobs.map(x => x.key.split('/')[2]).filter(id => !hidden.has(id))));
      const week = await Promise.all(Array.from({ length:Math.min(7, day) }, (_, k) => day - k).map(async d => ({ day:d, ids:await ids(d) })));
      const t = week[0].ids, y = week[1] ? week[1].ids : new Set();
      const crews = await store.list({ prefix:'crew/' }); const players = (await store.list({ prefix:'player/' })).blobs.filter(x => !hidden.has(x.key.slice(7)));
      // by source: new players, back the next day, back within 7 days
      const srcRows = (await store.list({ prefix:'src/' })).blobs.map(x => { const [, src, id] = x.key.split('/'); return { src, id }; }).filter(r => !hidden.has(r.id));
      const firsts = await Promise.all(srcRows.map(async r => ({ ...r, first:((await store.get(`src/${r.src}/${r.id}`, { type:'json' })) || {}).first || 0 })));
      const bySrc = {};
      for (const r of firsts) {
        const o = bySrc[r.src] = bySrc[r.src] || { src:r.src, players:0, d1:{ of:0, back:0 }, d7:{ of:0, back:0 } }; o.players++;
        if (r.first && r.first + 1 <= day) { o.d1.of++; if ((await ids(r.first + 1)).has(r.id)) o.d1.back++; }
        if (r.first && r.first + 7 <= day) { o.d7.of++; for (let d = r.first + 1; d <= r.first + 7; d++) if ((await ids(d)).has(r.id)) { o.d7.back++; break; } }
      }
      const suggestions = (await store.list({ prefix:'sug/' })).blobs.length;
      return json(200, { day, playersToday:t.size, playersYesterday:y.size,
        cameBackToday:[...t].filter(id => y.has(id)).length,          // played yesterday AND today
        playersAllTime:players.length, crews:crews.blobs.length, answeredToday:(await store.list({ prefix:`ans/${day}/` })).blobs.length,
        last7Days:week.map(w => ({ day:w.day, players:w.ids.size })), sources:Object.values(bySrc).sort((a, b) => b.players - a.players), suggestions,
        hiddenBrowsers:hidden.size, adminClaimed:!!(await store.get('admin/key', { type:'json' })),
        clubs:await clubStats(store, code => store.get('crew/' + code, { type:'json' })) });
    }

    // POST /api/hideme { playerId }   leave this browser out of the stats (Josh's own phones)
    if (req.method === 'POST' && p === '/api/hideme') {
      const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
      await hide(store, b.playerId); return json(200, { ok:true });
    }
    // POST /api/admin/claim { playerId }   the first person to claim gets the admin key (Josh, once). After that it's locked.
    if (req.method === 'POST' && p === '/api/admin/claim') {
      const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
      if (await store.get('admin/key', { type:'json' })) return json(409, { error:'already claimed' });
      const key = Array.from(crypto.getRandomValues(new Uint8Array(12)), x => x.toString(16).padStart(2, '0')).join('');
      await store.setJSON('admin/key', { key, by:b.playerId, at:now }); await hide(store, b.playerId);
      return json(200, { ok:true, key });
    }

    // POST /api/suggest { playerId, kind:'receipts'|'survey', q, credit }   a question idea from a player
    if (req.method === 'POST' && p === '/api/suggest') {
      const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
      const kind = b.kind === 'survey' ? 'survey' : 'receipts', q = cleanText(b.q, SUGGEST_MAX);
      if (q.length < 8) return json(400, { error:'write a question' });
      const credit = cleanText(b.credit, 30).replace(/^@+/, '').replace(/[^A-Za-z0-9._]/g, '');
      const ck = `sugc/${day}/${b.playerId}`, cnt = (await store.get(ck, { type:'json' })) || { n:0 };
      if (cnt.n >= SUGGEST_PER_DAY) return json(429, { error:'that\'s plenty for today' });
      cnt.n++; await store.setJSON(ck, cnt);
      const id = String(9e15 - now).padStart(16, '0') + '-' + Math.random().toString(36).slice(2, 7);   // newest first when listed
      await store.setJSON('sug/' + id, { kind, q, credit, day, at:now });
      return json(200, { ok:true });
    }
    // GET /api/suggestions?k=ADMIN_KEY   Josh's private list, newest first
    if (req.method === 'GET' && p === '/api/suggestions') {
      if (!(await isAdmin(store, url.searchParams.get('k')))) return json(403, { error:'admin only' });
      const keys = (await store.list({ prefix:'sug/' })).blobs.map(x => x.key).sort().slice(0, SUGGEST_LIST);
      return json(200, { list:(await Promise.all(keys.map(k => store.get(k, { type:'json' })))).filter(Boolean) });
    }

    // GET /api/home   for the home page: yesterday's real result and the crew of the week (worked out at most every 5 minutes)
    if (req.method === 'GET' && p === '/api/home') {
      const c = await store.get('cache/home', { type:'json' });
      if (c && c.day === day && now - c.at < HOME_CACHE_MS) return json(200, c.data);
      // Yesterday's Receipts questions are closed (answers are only taken on their own day), so their counts can't move any more.
      const closed = [];
      if (day > 1) for (const r of [0, 2]) { const a = await store.get(`agg/${day - 1}/${r}`, { type:'json' }); if (a && a.n >= HOME_MIN && a.q) closed.push({ q:a.q, yes:a.yes, n:a.n }); }
      const yesterday = closed.length ? closed.reduce((x, y) => (y.n > x.n ? y : x)) : null;
      let crewOfWeek = null; const mon = Math.max(1, mondayOf(day));
      for (const k of (await store.list({ prefix:'crew/' })).blobs.map(x => x.key.slice(5))) {
        const cr = await store.get('crew/' + k, { type:'json' }); if (!cr || cr.club) continue;
        const rows = await Promise.all(cr.members.map(async id => ({ id, ...(await histOf(store, id, day)) })));
        const act = weekTable(rows, mon, day).filter(m => m.played > 0); if (act.length < CREW_OF_WEEK_MIN) continue;
        const avg = Math.round(act.reduce((a, m) => a + m.total / m.played, 0) / act.length);
        if (!crewOfWeek || avg > crewOfWeek.avg) crewOfWeek = { name:cr.name, avg, players:act.length };
      }
      const data = { day, yesterday, closed, max:DAY_MAX, crewOfWeek };
      await store.setJSON('cache/home', { day, at:now, data });
      return json(200, data);
    }
    return json(404, { error:'not found' });
  } catch (e) { return json(400, { error:'bad request' }); }
}

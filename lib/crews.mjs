import { clubRoutes, clubStats } from './clubs.mjs';
// Crews: friend groups that compare their daily scores.
// The store is Netlify Blobs in production (see netlify/functions/api.mjs) and an in-memory map in the tests.
// Keys:  crew/CODE -> { name, members[], by, at }   player/ID -> { nick, crews[], at }   score/DAY/ID -> { total, pts[], at }

// ---------- settings you can change ----------
export const FIRST_DAY = '2026-11-03';   // must match FIRST_DAY in the game (daily.html)
const MAX_SCORE = 5000;
const MAX_CREW_MEMBERS = 60;
const MAX_CREWS_PER_PLAYER = 10;
const NICK_MAX = 16, CREW_NAME_MAX = 28;
const STREAK_LOOKBACK = 30;
const LEAGUE_DAYS = 30;          // the crew league counts the last 30 days
const HIST_KEEP = 60;            // days of scores kept on each player for the league
const REAL_MIN = 5;              // real answers needed before we show a split ("x of n said yes")
const CREW_MIN = 5;              // crew answers needed before a crew split shows (so nobody's answer can be worked out)
const TEXT_MAX = 60, TEXTS_PER_ROUND = 10;
const LOGIN_TRIES = 5, LOCK_MINUTES = 15;   // wrong PINs allowed before a name is locked for a while

export function torontoDay(now = Date.now()){   // Daily number: No. 1 on FIRST_DAY, a new one at 4am Toronto time
  const s = new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date(now - 4 * 3600e3));
  return Math.max(1, Math.round((Date.parse(s) - Date.parse(FIRST_DAY)) / 864e5) + 1);
}
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
    return { nick:p.nick || 'Player', you:id === me, total:s ? s.total : null, pts:s ? s.pts : null, streak };
  }));
  members.sort((a, b) => (b.total ?? -1) - (a.total ?? -1));
  return { code, name:c.name, day, played:members.filter(m => m.total !== null).length, size:members.length, members };
}

// Round order in the daily game is Receipts, Showdown, Receipts, Showdown, Pin. Each game's number is points per round (out of 1,000).
const GAMES = { receipts:[0, 2], showdown:[1, 3], pin:[4] };
async function histOf(store, id, day){
  const pl = await getPlayer(store, id);
  if (pl.hist) return { pl, hist:pl.hist };
  const hist = {};   // players from before the league existed: read their score records
  await Promise.all(Array.from({ length:Math.min(LEAGUE_DAYS, day) }, (_, k) => day - k).map(async d => { const s = await store.get(`score/${d}/${id}`, { type:'json' }); if (s) hist[d] = { t:s.total, p:s.pts }; }));
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
      best:days.length ? Math.max(...days.map(d => r.hist[d].t)) : null, streak, receipts:game('receipts'), showdown:game('showdown'), pin:game('pin') };
  });
  members.sort((a, b) => b.wins - a.wins || (b.avg ?? -1) - (a.avg ?? -1));
  const king = g => { const q = members.filter(m => m[g] !== null && m.played >= 1).sort((a, b) => b[g] - a[g]); return q.length ? { nick:q[0].nick, you:q[0].you, score:q[0][g] } : null; };
  return { code, name:c.name, day, days:LEAGUE_DAYS, members, best:{ receipts:king('receipts'), showdown:king('showdown'), pin:king('pin') } };
}

// ---------- save your spot: nickname + 4-digit PIN ----------
// nick/<name> -> { id }   player record gets { salt, pinHash }   fail/<name> -> { n, until }
const nickKey = n => 'nick/' + cleanText(n, NICK_MAX).toLowerCase().replace(/\s+/g, ' ');
const validPin = p => typeof p === 'string' && /^\d{4}$/.test(p);
async function hashPin(pin, salt){ const d = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(salt + ':' + pin)); return Array.from(new Uint8Array(d), b => b.toString(16).padStart(2, '0')).join(''); }
function summary(pl, day){   // what a new browser needs to pick up where this player left off
  const hist = pl.hist || {}, days = Object.keys(hist).map(Number).sort((a, b) => a - b);
  let n = 0, d = hist[day] ? day : day - 1; while (d > 0 && hist[d]) { n++; d--; }
  return { today:hist[day] ? { total:hist[day].t, pts:hist[day].p } : null, streak:{ last:days.length ? days[days.length - 1] : 0, n, best:days.reduce((m, x) => Math.max(m, hist[x].t), 0), days:days.length } };
}

// ---------- real answers ----------
// ans/DAY/ID -> { yn:{ round:'Y'|'N' }, txt:{ round:[...] } }   agg/DAY/ROUND -> { yes, n }
async function crewSplits(store, id, day, round){
  const pl = await store.get('player/' + id, { type:'json' }); if (!pl || !pl.crews || !pl.crews.length) return [];
  return (await Promise.all(pl.crews.slice(0, 3).map(async code => {
    const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
    const answers = (await Promise.all(c.members.map(m => store.get(`ans/${day}/${m}`, { type:'json' })))).map(a => a && a.yn ? a.yn[round] : null).filter(Boolean);
    const n = answers.length;
    return n >= CREW_MIN ? { name:c.name, n, yes:answers.filter(a => a === 'Y').length } : { name:c.name, n, hidden:true };
  }))).filter(Boolean);
}
// yesterday (or any day) for one crew, without streaks: who played, who won, by how much
async function dayResults(store, code, d, me){
  const c = await store.get('crew/' + code, { type:'json' }); if (!c) return null;
  const rows = (await Promise.all(c.members.map(async id => { const [p, s] = await Promise.all([getPlayer(store, id), store.get(`score/${d}/${id}`, { type:'json' })]); return { nick:p.nick || 'Player', you:id === me, total:s ? s.total : null }; })))
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

    // POST /api/score  { playerId, nick, day, total, pts[5] }  (the first score of the day counts)
    if (req.method === 'POST' && p === '/api/score') {
      const b = await body();
      if (!validId(b.playerId)) return json(400, { error:'bad player' });
      if (Number(b.day) !== day) return json(409, { error:'wrong day', day });
      const pts = Array.isArray(b.pts) ? b.pts.map(Number) : [];
      if (pts.length !== 5 || pts.some(x => !Number.isFinite(x) || x < 0 || x > 1000)) return json(400, { error:'bad score' });
      const total = pts.reduce((a, c) => a + Math.round(c), 0);
      if (total > MAX_SCORE || Math.abs(total - Number(b.total)) > 5) return json(400, { error:'bad score' });
      const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, NICK_MAX); if (nick) pl.nick = nick;
      await store.setJSON('player/' + b.playerId, pl);
      const key = `score/${day}/${b.playerId}`; const had = await store.get(key, { type:'json' });
      if (!had) {
        await store.setJSON(key, { total, pts:pts.map(Math.round), at:now });
        pl.hist = pl.hist || {}; pl.hist[day] = { t:total, p:pts.map(Math.round) };
        for (const d of Object.keys(pl.hist)) if (+d <= day - HIST_KEEP) delete pl.hist[d];
        await store.setJSON('player/' + b.playerId, pl);
      }
      return json(200, { ok:true, day, total:had ? had.total : total });
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
    // Saves a real answer (first answer per round counts) and sends back the real counts so far.
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
        agg.n++; if (b.yes) agg.yes++; await store.setJSON(aggKey, agg);
      }
      const queens = agg.n >= REAL_MIN ? { n:agg.n, yes:agg.yes } : { n:agg.n, hidden:true };
      return json(200, { ok:true, queens, crews:await crewSplits(store, b.playerId, day, round) });
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
      if (url.searchParams.get('recap') && day > 1) await Promise.all(crews.map(async c => { c.yesterday = await dayResults(store, c.code, day - 1, id); }));
      return json(200, { day, nick:pl.nick, saved:!!pl.pinHash, crews });
    }

    // GET /api/stats   players today, crews (for Josh)
    if (req.method === 'GET' && p === '/api/stats') {
      const ids = async d => new Set((await store.list({ prefix:`score/${d}/` })).blobs.map(x => x.key.split('/')[2]));
      const week = await Promise.all(Array.from({ length:Math.min(7, day) }, (_, k) => day - k).map(async d => ({ day:d, ids:await ids(d) })));
      const t = week[0].ids, y = week[1] ? week[1].ids : new Set();
      const crews = await store.list({ prefix:'crew/' }); const players = await store.list({ prefix:'player/' });
      return json(200, { day, playersToday:t.size, playersYesterday:y.size,
        cameBackToday:[...t].filter(id => y.has(id)).length,          // played yesterday AND today
        playersAllTime:players.blobs.length, crews:crews.blobs.length, answeredToday:(await store.list({ prefix:`ans/${day}/` })).blobs.length,
        last7Days:week.map(w => ({ day:w.day, players:w.ids.size })),
        clubs:await clubStats(store, code => store.get('crew/' + code, { type:'json' })) });
    }
    return json(404, { error:'not found' });
  } catch (e) { return json(400, { error:'bad request' }); }
}

// HOUSE LEAGUE: your house vs every house at Queen's.
// A house is an official team (one per player per week). A crew is a casual friend group (as many as you like).
//
// Keys:  house/CODE -> { name, color, motto, members:[ids], by, at, weeks:{ MONDAY:[ids who count for this house that week] } }
//        player/ID  -> ...existing fields, plus house:CODE|null and rep:{ MONDAY:CODE }  (which house they count for each week)
//
// How a week is scored (Monday 4am to the next Monday 4am, Toronto):
//   1. Each player's Daily scores that week become percentages of the day's maximum (honest scores: out of 3,000 today).
//   2. Each player's average % = the average of the days they played. Days they didn't play are not zeros.
//   3. The house's % = the average of its players' averages, so one very active player can't carry the house alone.
//   4. A house needs MIN_PLAYERS different players with at least one Daily that week to be ranked.
//   5. Ties: same % (to 0.1) -> more players -> more days played. Still tied -> same rank.
// Showdown and Pin points are still worked out on the phone, so this is fine for a no-prize league, not for prizes.
import { dayPct as dayPctOf, DAY_MAX, mondayOf } from './crews.mjs';

// ---------- settings you can change ----------
export const MIN_PLAYERS = 3;     // players a house needs in a week to be ranked
const MAX_MEMBERS = 20;
const NAME_MAX = 24, MOTTO_MAX = 40;
export const COLORS = ['gold', 'mint', 'red', 'blue', 'pin', 'pink', 'good', 'cream'];   // house colours (CSS variables on the pages)
const CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
// A house name is a nickname, never a street address ("517 Earl St" is refused; "517" or "The Earl Street Boys" is fine).
const ADDRESS = /\b\d{1,5}[a-z]?\s+[a-z.' -]{2,30}\s(st|street|ave|avenue|rd|road|cres|crescent|blvd|dr|drive|ln|lane|way|ct|court|pl|place|terr|terrace|row|sq)\b\.?/i;

const dayPct = h => dayPctOf(h);   // one day, as a % of THAT day's own max (v2 days: 3,000; future v3 days carry their own max)
const avg = a => a.reduce((x, y) => x + y, 0) / a.length;
const round1 = x => Math.round(x * 10) / 10;

async function newHouseCode(store){
  for (let i = 0; i < 20; i++) { const b = crypto.getRandomValues(new Uint8Array(6)); let c = ''; for (let k = 0; k < 6; k++) c += CODE_CHARS[b[k] % CODE_CHARS.length];
    if (!(await store.get('house/' + c, { type:'json' }))) return c; }
  throw new Error('no code');
}
// This player counts for `code` this week, unless they already count for another house this week.
async function claimWeek(store, pl, id, code, day){
  const mon = mondayOf(day); pl.rep = pl.rep || {};
  if (pl.rep[mon]) return pl.rep[mon] === code;
  const h = await store.get('house/' + code, { type:'json' }); if (!h) return false;
  pl.rep[mon] = code; h.weeks = h.weeks || {}; h.weeks[mon] = h.weeks[mon] || [];
  if (!h.weeks[mon].includes(id)) h.weeks[mon].push(id);
  await store.setJSON('house/' + code, h);
  return true;
}
// Called by POST /api/score after the day's first score is saved (pl is saved by the caller)
export async function houseOnScore(store, pl, id, day){ if (pl.house) await claimWeek(store, pl, id, pl.house, day); }

async function playerWeek(store, id, from, to){
  const pl = await store.get('player/' + id, { type:'json' }); if (!pl) return null;
  const days = Object.keys(pl.hist || {}).map(Number).filter(d => d >= from && d <= to).sort((a, b) => a - b);
  return { id, nick:pl.nick || 'Player', days:days.length, pct:days.length ? round1(avg(days.map(d => dayPct(pl.hist[d])))) : null, played:new Set(days) };
}
async function houseWeek(store, code, h, mon, today){
  const from = Math.max(1, mon), to = Math.min(mon + 6, today);
  const rows = (await Promise.all(((h.weeks || {})[mon] || []).map(id => playerWeek(store, id, from, to)))).filter(r => r && r.days > 0);
  return { code, name:h.name, color:h.color, mono:monoOf(h.name), players:rows.length, days:rows.reduce((a, r) => a + r.days, 0),
    pct:rows.length ? round1(avg(rows.map(r => r.pct))) : null, rows };
}
export const monoOf = n => { const w = String(n).split(/\s+/).filter(x => /[a-z0-9]/i.test(x)); return (w.length > 1 ? w[0][0] + w[1][0] : String(n).replace(/[^a-z0-9]/gi, '').slice(0, 2)).toUpperCase() || 'H'; };
// Every house's week. Ranked = 3+ players, best first.
async function standings(store, mon, today){
  const codes = (await store.list({ prefix:'house/' })).blobs.map(b => b.key.slice(6));
  const all = (await Promise.all(codes.map(async c => { const h = await store.get('house/' + c, { type:'json' }); return h ? houseWeek(store, c, h, mon, today) : null; }))).filter(Boolean);
  const ranked = all.filter(x => x.players >= MIN_PLAYERS).sort((a, b) => b.pct - a.pct || b.players - a.players || b.days - a.days || a.name.localeCompare(b.name));
  ranked.forEach((x, i) => { const p = ranked[i - 1]; x.rank = p && p.pct === x.pct && p.players === x.players && p.days === x.days ? p.rank : i + 1; });
  const forming = all.filter(x => x.players < MIN_PLAYERS);
  return { ranked, forming };
}
const pub = x => ({ rank:x.rank ?? null, name:x.name, color:x.color, mono:x.mono, pct:x.pct, players:x.players, days:x.days });

function cleanHouse(b, cleanText){
  const name = cleanText(b.name, NAME_MAX), motto = cleanText(b.motto, MOTTO_MAX);
  if (name.length < 2) return { error:'name your house' };
  if (ADDRESS.test(name) || ADDRESS.test(motto)) return { error:'use a house nickname, not your address' };
  return { name, motto, color:COLORS.includes(b.color) ? b.color : COLORS[0] };
}
async function leaveHouse(store, pl, id){
  if (!pl.house) return;
  const h = await store.get('house/' + pl.house, { type:'json' });
  if (h) { h.members = h.members.filter(x => x !== id); await store.setJSON('house/' + pl.house, h); }
  pl.house = null;
}
async function houseView(store, code, me, day){
  const h = await store.get('house/' + code, { type:'json' }); if (!h) return null;
  const mon = mondayOf(day), member = !!me && h.members.includes(me);
  const base = { code, name:h.name, color:h.color, motto:h.motto || '', mono:monoOf(h.name), size:h.members.length, member, minPlayers:MIN_PLAYERS };
  if (!member) return base;   // people outside the house never see who is in it
  const wk = await houseWeek(store, code, h, mon, day);
  const counted = new Set(((h.weeks || {})[mon] || []));
  const members = await Promise.all(h.members.map(async id => {
    const pw = await playerWeek(store, id, Math.max(1, mon), Math.min(mon + 6, day));
    return { nick:pw ? pw.nick : 'Player', you:id === me, countsHere:counted.has(id), days:counted.has(id) && pw ? pw.days : 0,
      pct:counted.has(id) && pw ? pw.pct : null, today:!!(pw && pw.played.has(day)) };
  }));
  members.sort((a, b) => (b.pct ?? -1) - (a.pct ?? -1) || b.days - a.days);
  const mePl = await store.get('player/' + me, { type:'json' }); const myRep = mePl && mePl.rep ? mePl.rep[mon] : null;
  const repH = myRep && myRep !== code ? await store.get('house/' + myRep, { type:'json' }) : null;
  return { ...base, week:{ pct:wk.pct, players:wk.players, days:wk.days }, members, countsElsewhere:!!(myRep && myRep !== code), countsFor:repH ? repH.name : null };
}

export async function houseRoutes({ req, store, now, url, p, body, json, cleanText, validId, getPlayer, day }){
  // POST /api/houses { playerId, nick, name, color, motto }   start a house (you leave any house you were in)
  if (req.method === 'POST' && p === '/api/houses') {
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const c = cleanHouse(b, cleanText); if (c.error) return json(400, c);
    const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, 16); if (nick) pl.nick = nick;
    await leaveHouse(store, pl, b.playerId);
    const code = await newHouseCode(store);
    await store.setJSON('house/' + code, { ...c, members:[b.playerId], by:b.playerId, at:now, weeks:{} });
    pl.house = code; const counts = await claimWeek(store, pl, b.playerId, code, day);
    await store.setJSON('player/' + b.playerId, pl);
    return json(200, { ...(await houseView(store, code, b.playerId, day)), countsFromNow:counts });
  }
  let m = p.match(/^\/api\/houses\/([A-Z0-9]{6})(\/(join|leave|edit))?$/);
  if (m) {
    const code = m[1], what = m[3] || '';
    // GET /api/houses/CODE?playerId=   members see the roster and this week; anyone else sees the name and size (for the invite page)
    if (req.method === 'GET' && !what) { const v = await houseView(store, code, url.searchParams.get('playerId'), day); return v ? json(200, v) : json(404, { error:'house not found' }); }
    if (req.method !== 'POST') return json(404, { error:'not found' });
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const h = await store.get('house/' + code, { type:'json' }); if (!h) return json(404, { error:'house not found' });
    const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, 16); if (nick) pl.nick = nick;
    if (what === 'join') {
      if (!h.members.includes(b.playerId)) {
        if (h.members.length >= MAX_MEMBERS) return json(400, { error:'house is full' });
        await leaveHouse(store, pl, b.playerId);
        const fresh = await store.get('house/' + code, { type:'json' }); fresh.members.push(b.playerId); await store.setJSON('house/' + code, fresh);
        pl.house = code;
      }
      const counts = await claimWeek(store, pl, b.playerId, code, day);
      await store.setJSON('player/' + b.playerId, pl);
      return json(200, { ...(await houseView(store, code, b.playerId, day)), countsFromNow:counts });
    }
    if (!h.members.includes(b.playerId)) return json(403, { error:'members only' });
    if (what === 'leave') { await leaveHouse(store, pl, b.playerId); await store.setJSON('player/' + b.playerId, pl); return json(200, { ok:true }); }
    if (what === 'edit') {
      const c = cleanHouse({ name:b.name ?? h.name, color:b.color ?? h.color, motto:b.motto ?? h.motto }, cleanText); if (c.error) return json(400, c);
      await store.setJSON('house/' + code, { ...h, ...c }); return json(200, await houseView(store, code, b.playerId, day));
    }
  }
  // GET /api/league?playerId=   this week's standings, your house, the house just above you, last week's winner
  if (req.method === 'GET' && p === '/api/league') {
    const me = url.searchParams.get('playerId'), mon = mondayOf(day);
    const { ranked, forming } = await standings(store, mon, day);
    const pl = validId(me) ? await store.get('player/' + me, { type:'json' }) : null;
    const myCode = pl && pl.house, mine = myCode ? (ranked.find(x => x.code === myCode) || forming.find(x => x.code === myCode)) : null;
    let rival = null;
    if (mine && mine.rank) {
      const i = ranked.indexOf(mine), above = ranked.slice(0, i).reverse().find(x => x.pct > mine.pct), below = ranked.slice(i + 1).find(x => x.pct < mine.pct);
      if (above) rival = { dir:'chase', name:above.name, color:above.color, mono:above.mono, rank:above.rank, gap:round1(above.pct - mine.pct) };
      else if (below) rival = { dir:'lead', name:below.name, color:below.color, mono:below.mono, rank:below.rank, gap:round1(mine.pct - below.pct) };
    }
    let lastWeek = null;
    if (mon - 7 + 6 >= 1) { const lw = await standings(store, mon - 7, mon - 1); if (lw.ranked.length) lastWeek = { from:Math.max(1, mon - 7), to:mon - 1, winner:pub(lw.ranked[0]), ranked:lw.ranked.length, yours:myCode ? (lw.ranked.find(x => x.code === myCode) || null) && pub(lw.ranked.find(x => x.code === myCode)) : null }; }
    return json(200, { day, week:{ from:Math.max(1, mon), to:mon + 6, daysLeft:mon + 6 - day }, minPlayers:MIN_PLAYERS, max:DAY_MAX,
      ranked:ranked.map(x => ({ ...pub(x), you:x.code === myCode })), forming:forming.length,
      mine:mine ? { ...pub(mine), code:myCode, qualified:!!mine.rank, need:Math.max(0, MIN_PLAYERS - mine.players), countsElsewhere:!!(pl.rep && pl.rep[mon] && pl.rep[mon] !== myCode),
        countsFor:pl.rep && pl.rep[mon] && pl.rep[mon] !== myCode ? (((await store.get('house/' + pl.rep[mon], { type:'json' })) || {}).name || null) : null,
        playedToday:!!(pl.hist && pl.hist[day]), todayCounted:!!(pl.hist && pl.hist[day] && pl.rep && pl.rep[mon] === myCode) } : null,
      playedToday:!!(pl && pl.hist && pl.hist[day]),
      rival, lastWeek });
  }
  return null;
}

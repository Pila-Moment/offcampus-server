// Requests arriving at the same moment: the first score of the day, House League weeks. Run: npm test
import { handle } from './lib/crews.mjs';
const mem = new Map(), tick = () => new Promise(r => setTimeout(r, Math.random() * 4));   // every store call pauses a little, so requests interleave
const store = {
  async get(k){ await tick(); return mem.has(k) ? JSON.parse(mem.get(k)) : null; },
  async setJSON(k, v, o = {}){ await tick(); if (o.onlyIfNew && mem.has(k)) return { modified:false }; mem.set(k, JSON.stringify(v)); return { modified:true }; },
  async list({ prefix }){ await tick(); return { blobs:[...mem.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })) }; },
};
const noon = d => Date.parse('2026-11-03T17:00:00Z') + (d - 1) * 864e5;
const call = async (m, path, body, d) => { const r = await handle(new Request('https://x' + path, { method:m, body:body ? JSON.stringify(body) : undefined }), store, noon(d)); return { s:r.status, b:await r.json() }; };
const ok = (c, msg) => { if (!c) { console.error('FAIL:', msg); process.exit(1); } console.log('ok -', msg); };
const P = n => ('cc' + n).padEnd(16, 'x');
// ---------- 8 copies of a first score arriving together ----------
const A = P(1); await call('POST', '/api/houses', { playerId:A, nick:'Ana', name:'Race House' }, 7);
const H = (await call('GET', `/api/me?playerId=${A}`, null, 7)).b.house.code;
const posts = await Promise.all(Array.from({ length:8 }, (_, i) => call('POST', '/api/score', { playerId:A, nick:'Ana', day:7, pts:[null, 100 * (i + 1), null, 500, 500] }, 7)));
const rec = JSON.parse(mem.get(`score/7/${A}`)), totals = new Set(posts.map(x => x.b.total));
ok(posts.every(x => x.s === 200) && totals.size === 1 && [...totals][0] === rec.total, `8 at once: one score saved (${rec.total}), every reply gives that same score`);
const pl = JSON.parse(mem.get('player/' + A));
ok(pl.hist[7].t === rec.total && pl.rep && pl.rep[7] === H, 'the player history and the House League week match the saved score');
ok([...mem.keys()].filter(k => k.startsWith(`hw/${H}/7/`)).length === 1, 'the house week has this player once');
// ---------- 6 roommates finishing at the same moment ----------
const mates = [2, 3, 4, 5, 6, 7].map(P);
for (const id of mates) await call('POST', `/api/houses/${H}/join`, { playerId:id, nick:'M' }, 7);
await Promise.all(mates.map((id, i) => call('POST', '/api/score', { playerId:id, day:7, pts:[null, 400 + i * 10, null, 400, 400] }, 7)));
const L = (await call('GET', `/api/league?playerId=${A}`, null, 7)).b;
ok(L.mine.players === 7 && L.mine.qualified, 'six roommates finishing together: all seven players count (nobody erased)');
ok(mates.every(id => JSON.parse(mem.get('player/' + id)).hist[7]), 'everyone keeps their own history');
// ---------- Monday: the new week, everyone's first score arrives together (each one claims the week) ----------
await Promise.all([A, ...mates].map((id, i) => call('POST', '/api/score', { playerId:id, day:14, pts:[null, 500 + i * 20, null, 500, 500] }, 14)));
const L14 = (await call('GET', `/api/league?playerId=${A}`, null, 14)).b;
ok(L14.week.from === 14 && L14.mine.players === 7 && [...mem.keys()].filter(k => k.startsWith(`hw/${H}/14/`)).length === 7, 'Monday, 7 first scores at once: all 7 count for the new week');
// ---------- a lost history is repaired from the saved score ----------
const B = P(8); await call('POST', '/api/score', { playerId:B, day:7, pts:[null, 900, null, 900, 900] }, 7);
const pb = JSON.parse(mem.get('player/' + B)); delete pb.hist[7]; mem.set('player/' + B, JSON.stringify(pb));
const again = (await call('POST', '/api/score', { playerId:B, day:7, pts:[null, 0, null, 0, 0] }, 7)).b;
ok(again.total === 2700 && JSON.parse(mem.get('player/' + B)).hist[7].t === 2700, 'a later resend repairs a lost history from the saved score, never replaces it');
// ---------- the league says it isn't verified ----------
ok(L.verified === false && L.prizes === false, 'the league always says: not verified, no prizes');
console.log('concurrency tests passed');

// House League tests (in-memory store). Run: npm test
import { handle } from './lib/crews.mjs';

const mem = new Map();
const store = {
  async get(k){ return mem.has(k) ? JSON.parse(mem.get(k)) : null; },
  async setJSON(k, v){ mem.set(k, JSON.stringify(v)); },
  async list({ prefix }){ return { blobs:[...mem.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })) }; },
};
const at = d => Date.parse('2026-11-03T17:00:00Z') + (d - 1) * 864e5;   // noon Toronto on day d (day 7 = Monday Nov 9)
const call = async (m, path, body, d) => { const r = await handle(new Request('https://x' + path, { method:m, body:body ? JSON.stringify(body) : undefined }), store, at(d)); return { s:r.status, b:await r.json() }; };
const ok = (c, msg) => { if (!c) { console.error('FAIL:', msg); process.exit(1); } console.log('ok -', msg); };
const P = n => ('p' + n).padEnd(16, 'x');
// a Daily with honest points: Showdown, Showdown, Pin (Receipts null). pct = (a+b+c)/3000
const play = (id, d, a, b, c, nick) => call('POST', '/api/score', { playerId:id, nick, day:d, pts:[null, a, null, b, c] }, d);

// ---------- making and joining ----------
ok((await call('POST', '/api/houses', { playerId:P(1), nick:'Josh', name:'517 Earl St' }, 7)).s === 400, 'a street address is refused as a house name');
ok((await call('POST', '/api/houses', { playerId:P(1), nick:'Josh', name:'x' }, 7)).s === 400, 'a house needs a real name');
const A = (await call('POST', '/api/houses', { playerId:P(1), nick:'Josh', name:'The Earl Street Boys', color:'mint', motto:'Loudest on Earl' }, 7)).b;
ok(/^[A-Z0-9]{6}$/.test(A.code) && A.member && A.size === 1 && A.color === 'mint' && A.mono === 'TE' && A.countsFromNow, 'start a house');
const asStranger = (await call('GET', `/api/houses/${A.code}?playerId=${P(99)}`, null, 7)).b;
ok(!asStranger.member && asStranger.size === 1 && !('members' in asStranger) && !JSON.stringify(asStranger).includes('Josh'), 'someone outside the house sees the name and size, never who is in it');
for (const [n, nick] of [[2, 'Maya'], [3, 'Sam']]) await call('POST', `/api/houses/${A.code}/join`, { playerId:P(n), nick }, 7);
await call('POST', `/api/houses/${A.code}/join`, { playerId:P(2), nick:'Maya' }, 7);
ok((await call('GET', `/api/houses/${A.code}?playerId=${P(1)}`, null, 7)).b.size === 3, 'joining twice does not add you twice');
const B = (await call('POST', '/api/houses', { playerId:P(4), nick:'Lee', name:'Aberdeen Ave Legends', color:'red' }, 7)).b;
for (const [n, nick] of [[5, 'Ana'], [6, 'Raj'], [7, 'Kim']]) await call('POST', `/api/houses/${B.code}/join`, { playerId:P(n), nick }, 7);
ok(!JSON.stringify(B).includes('Josh'), 'houses are separate');

// ---------- low participation: 2 players is not enough ----------
await play(P(1), 7, 900, 900, 900, 'Josh'); await play(P(2), 7, 600, 600, 600, 'Maya');
let L = (await call('GET', `/api/league?playerId=${P(1)}`, null, 7)).b;
ok(L.ranked.length === 0 && L.mine && !L.mine.qualified && L.mine.players === 2 && L.mine.need === 1 && L.minPlayers === 3, 'two players: not ranked yet, "1 more needed"');
ok(L.week.from === 7 && L.week.to === 13 && L.week.daysLeft === 6, 'the week runs Monday to Sunday');
// ---------- 3 players: ranked. Averages of averages, absent days are not zeros ----------
await play(P(3), 7, 300, 300, 300, 'Sam');                                   // A today: 90%, 60%, 30%
for (const n of [4, 5, 6]) await play(P(n), 7, 700, 700, 700);              // B today: 70% x3 (Kim hasn't played)
await play(P(1), 8, 900, 900, 900); await play(P(1), 9, 900, 900, 900);     // Josh plays 3 days at 90%: still counts once
L = (await call('GET', `/api/league?playerId=${P(1)}`, null, 9)).b;
const a = L.ranked.find(x => x.name === 'The Earl Street Boys'), bb = L.ranked.find(x => x.name === 'Aberdeen Ave Legends');
ok(a && a.pct === 60 && a.players === 3 && a.days === 5, 'house % = average of each player\'s average (90, 60, 30 -> 60), not dragged by Josh playing more');
ok(bb && bb.pct === 70 && bb.players === 3, 'Kim not playing is not a zero (70, 70, 70 -> 70)');
ok(L.ranked[0].name === 'Aberdeen Ave Legends' && L.ranked[0].rank === 1 && a.rank === 2 && a.you && !bb.you, 'ranked best first, your house marked');
ok(L.rival && L.rival.dir === 'chase' && L.rival.name === 'Aberdeen Ave Legends' && L.rival.gap === 10, 'the house just above you and the gap to catch it');
ok(!JSON.stringify(L).includes('Maya') && !JSON.stringify(L).includes(P(2)), 'the league never shows players or ids');
const hq = (await call('GET', `/api/houses/${A.code}?playerId=${P(2)}`, null, 9)).b;
ok(hq.members.length === 3 && hq.members[0].nick === 'Josh' && hq.members[0].pct === 90 && hq.members[0].days === 3 && hq.week.pct === 60, 'members see each other\'s week');
// ---------- switching houses mid-week: still counts for the old house until Monday ----------
const sw = (await call('POST', `/api/houses/${B.code}/join`, { playerId:P(3), nick:'Sam' }, 9)).b;
ok(sw.member && sw.countsFromNow === false && sw.countsElsewhere, 'switching houses mid-week: you count for your new house from Monday');
await play(P(3), 9, 1000, 1000, 1000);
L = (await call('GET', `/api/league?playerId=${P(3)}`, null, 9)).b;
ok(L.ranked.find(x => x.name === 'The Earl Street Boys').players === 3 && L.ranked.find(x => x.name === 'Aberdeen Ave Legends').players === 3, 'one ranked house per player per week: Sam still counts for Earl Street, not twice');
ok(L.mine.name === 'Aberdeen Ave Legends' && L.mine.countsElsewhere, 'Sam sees the new house and that this week counts elsewhere');
ok((await call('GET', `/api/houses/${A.code}?playerId=${P(1)}`, null, 9)).b.size === 2, 'the old house roster drops Sam');
// ---------- ties: same %, more players wins; fully tied = same rank ----------
const C = (await call('POST', '/api/houses', { playerId:P(8), name:'Tie One' }, 9)).b, D = (await call('POST', '/api/houses', { playerId:P(11), name:'Tie Two' }, 9)).b;
for (const n of [9, 10]) await call('POST', `/api/houses/${C.code}/join`, { playerId:P(n) }, 9);
for (const n of [12, 13, 14]) await call('POST', `/api/houses/${D.code}/join`, { playerId:P(n) }, 9);
for (const n of [8, 9, 10, 11, 12, 13, 14]) await play(P(n), 9, 500, 500, 500);   // all 50%
L = (await call('GET', '/api/league', null, 9)).b;
const t1 = L.ranked.find(x => x.name === 'Tie One'), t2 = L.ranked.find(x => x.name === 'Tie Two');
ok(t1.pct === 50 && t2.pct === 50 && t2.rank < t1.rank, 'tie on %: the house with more players ranks higher');
const E = (await call('POST', '/api/houses', { playerId:P(15), name:'Tie Three' }, 9)).b;
for (const n of [16, 17]) await call('POST', `/api/houses/${E.code}/join`, { playerId:P(n) }, 9);
for (const n of [15, 16, 17]) await play(P(n), 9, 500, 500, 500);
L = (await call('GET', '/api/league', null, 9)).b;
ok(L.ranked.find(x => x.name === 'Tie Three').rank === L.ranked.find(x => x.name === 'Tie One').rank, 'same %, players and days: same rank');
// ---------- weekly reset: Monday starts fresh, last week's winner shows ----------
L = (await call('GET', `/api/league?playerId=${P(1)}`, null, 14)).b;
ok(L.week.from === 14 && L.ranked.length === 0 && L.lastWeek && L.lastWeek.winner.name === 'The Earl Street Boys' && L.lastWeek.winner.pct === 71.7 && L.lastWeek.yours.rank === 1, 'Monday: new week, nobody ranked yet, last week\'s winner shown (Sam\'s 100% day still counted for Earl Street: 90, 60, 65 -> 71.7)');
await play(P(3), 14, 800, 800, 800);
ok((await call('GET', `/api/houses/${B.code}?playerId=${P(3)}`, null, 14)).b.members.find(m => m.you).countsHere, 'next week Sam counts for the new house');
// ---------- old 5,000-point records count the honest way ----------
const O = P(30); await store.setJSON('player/' + O, { nick:'Old', crews:[], at:1, hist:{ 14:{ t:4100, p:[900, 800, 900, 700, 800] } } });
await store.setJSON(`score/14/${O}`, { total:4100, pts:[900, 800, 900, 700, 800], at:1 });
const F = (await call('POST', '/api/houses', { playerId:O, name:'Old Timers' }, 14)).b;
const fo = (await call('GET', `/api/houses/${F.code}?playerId=${O}`, null, 14)).b;
ok(fo.members[0].pct === 76.7 && (await store.get('player/' + O)).hist[14].t === 4100, 'a 5,000-point record counts as 2,300 of 3,000 (76.7%), record untouched');
// ---------- leaving, members-only actions ----------
ok((await call('POST', `/api/houses/${A.code}/edit`, { playerId:P(99), name:'Hacked' }, 14)).s === 403, 'only members can edit a house');
ok((await call('POST', `/api/houses/${A.code}/edit`, { playerId:P(1), color:'gold', motto:'Earl forever' }, 14)).b.color === 'gold', 'a member can change the colour and motto');
await call('POST', `/api/houses/${A.code}/leave`, { playerId:P(2) }, 14);
ok((await call('GET', `/api/houses/${A.code}?playerId=${P(1)}`, null, 14)).b.size === 1 && (await call('GET', `/api/me?playerId=${P(2)}`, null, 14)).b.house === null, 'leave a house');
ok((await call('GET', `/api/me?playerId=${P(1)}`, null, 14)).b.house.name === 'The Earl Street Boys', '/api/me says which house you are in');
ok((await call('GET', '/api/houses/ZZZZZZ', null, 14)).s === 404, 'unknown house');
// ---------- today's contribution is only claimed once the server has the score ----------
const N = P(40), G = (await call('POST', '/api/houses', { playerId:N, name:'Proof House' }, 15)).b;
let lg = (await call('GET', `/api/league?playerId=${N}`, null, 15)).b;
ok(lg.mine.playedToday === false && lg.mine.todayCounted === false, 'before the score reaches the server: not counted');
await play(N, 15, 500, 500, 500);
lg = (await call('GET', `/api/league?playerId=${N}`, null, 15)).b;
ok(lg.mine.playedToday && lg.mine.todayCounted, 'after the server saves it: counted');
const sw2 = (await call('GET', `/api/league?playerId=${P(3)}`, null, 9)).b;
ok(sw2.mine.countsFor === 'The Earl Street Boys' && sw2.mine.countsElsewhere, 'switcher: the league names the house you still count for');
// ---------- every day keeps its own max (future v3 days are read with their own max) ----------
const V = P(41); await store.setJSON('player/' + V, { nick:'Future', crews:[], at:1, hist:{ 15:{ t:4000, p:[800, 800, 800, 800, 800], v:3, max:5000 } } });
const Hv = (await call('POST', '/api/houses', { playerId:V, name:'Future House' }, 15)).b;
ok((await call('GET', `/api/houses/${Hv.code}?playerId=${V}`, null, 15)).b.members[0].pct === 80, 'a v3 day out of 5,000 counts as 80% (its own max), not out of 3,000');
const rec = await store.get(`score/15/${N}`); ok(rec.v === 2 && rec.max === 3000 && (await store.get('player/' + N)).hist[15].max === 3000, 'new scores save their version and max');
console.log('house league tests passed');

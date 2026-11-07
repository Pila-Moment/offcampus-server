// Frozen Receipts: the whole 14-day lifecycle on synthetic questions and players (in-memory store). Run: npm test
import { handle } from './lib/crews.mjs';
import { setFrozenEnabled, setBank } from './lib/receipts.mjs';

// In-memory store with "only if new" writes, and a tiny pause on every call so requests really interleave.
const mem = new Map(), tick = () => new Promise(r => setTimeout(r, Math.random() * 3));
const store = {
  async get(k){ await tick(); return mem.has(k) ? JSON.parse(mem.get(k)) : null; },
  async setJSON(k, v, o = {}){ await tick(); if (o.onlyIfNew && mem.has(k)) return { modified:false }; mem.set(k, JSON.stringify(v)); return { modified:true }; },
  async list({ prefix }){ await tick(); return { blobs:[...mem.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })) }; },
};
const noon = d => Date.parse('2026-11-03T17:00:00Z') + (d - 1) * 864e5;   // noon Toronto on day d
const four = (d, mins) => Date.parse('2026-11-03T09:00:00Z') + (d - 1) * 864e5 + mins * 60e3;   // 4am Toronto on day d, +/- minutes
const call = async (m, path, body, t) => { const r = await handle(new Request('https://x' + path, { method:m, body:body ? JSON.stringify(body) : undefined }), store, t); return { s:r.status, b:await r.json() }; };
const ok = (c, msg) => { if (!c) { console.error('FAIL:', msg); process.exit(1); } console.log('ok -', msg); };
const P = n => ('fz' + n).padEnd(16, 'x');
const ans = (n, qid, yes, d) => call('POST', '/api/rq/answer', { playerId:P(n), qid, yes }, noon(d));
const noNumbers = (o, what) => ok(!/"yes"|"pct"|"frozen":\{/.test(JSON.stringify(o)), `${what}: no YES/NO numbers`);

// ---------- switched off (the default): nothing changes ----------
ok((await call('GET', '/api/rq/today', null, noon(1))).s === 404, 'switch off: the frozen Receipts routes don\'t exist');
const off = (await call('POST', '/api/score', { playerId:P(900), day:1, pts:[null, 500, 1000, 500, 500] }, noon(1))).b;
ok(off.max === 3000 && off.total === 1500, 'switch off: a normal 3,000-point day, Receipts points ignored');

setFrozenEnabled(true);
setBank([
  { id:'rq_test_a', v:1, text:'TEST A: Have you ever cried in Stauffer?', firstDay:1, round:0, repeats:[] },
  { id:'rq_test_b', v:1, text:'TEST B: Have you ever slept in the ARC?', firstDay:1, round:2, repeats:[] },
  { id:'rq_test_c', v:1, text:'TEST C: Have you ever skipped a midterm?', firstDay:2, round:0, repeats:[] },
  { id:'rq_test_d', v:1, text:'TEST D: Have you ever been on Instagram live?', firstDay:3, round:0, repeats:[] },
]);

// ---------- collecting: one answer per player, counts only ----------
let r = await ans(1, 'rq_test_a', true, 1); ok(r.s === 200 && r.b.n === 1 && r.b.need === 30 && r.b.lastDay === 14, 'first answer: counted, 30 needed, collects until day 14');
noNumbers(r.b, 'answer reply');
ok((await ans(1, 'rq_test_a', false, 1)).b.already === true && (await ans(1, 'rq_test_a', true, 2)).b.n === 1, 'the same player again (even changing the answer): ignored, still 1');
await Promise.all(Array.from({ length:6 }, () => ans(2, 'rq_test_a', true, 1)));
ok([...mem.keys()].filter(k => k.startsWith('rqa/rq_test_a/' + P(2))).length === 1 && (await ans(3, 'rq_test_a', false, 1)).b.n === 3, '6 copies of one answer arriving together: counted once');
for (let i = 4; i <= 29; i++) await ans(i, 'rq_test_a', i % 3 !== 0, 1 + Math.floor(i / 7));   // answers spread over days 1 to 5
r = await ans(28, 'rq_test_a', true, 5);
ok(!mem.has('rqf/rq_test_a') && r.b.n === 29, '29 different players: not frozen');
ok((await call('GET', '/api/rq/today', null, noon(5))).b.target === null, 'nothing frozen yet: no guessing target, round 3 stays answer-only');
ok((await call('POST', '/api/rq/answer', { playerId:P(1), qid:'rq_nope', yes:true }, noon(5))).s === 404 && (await call('POST', '/api/rq/answer', { playerId:P(1), qid:'rq_test_d', yes:true }, noon(2))).s === 409, 'unknown question refused; a question can\'t be answered before its first day');
// ---------- the 30th answer freezes it, once ----------
r = await ans(30, 'rq_test_a', true, 5); const F = JSON.parse(mem.get('rqf/rq_test_a'));
ok(r.b.frozen === true && F.n === 30 && F.day === 5 && !('n' in r.b), 'the 30th player freezes it (day 5), and the reply has no numbers');
await ans(31, 'rq_test_a', false, 5); await ans(32, 'rq_test_a', false, 6);
ok(JSON.stringify(JSON.parse(mem.get('rqf/rq_test_a'))) === JSON.stringify(F), 'answers after the freeze never change the frozen result');
// ---------- the 4am rollover: the target is picked once, the same for everyone ----------
ok((await call('GET', '/api/rq/today', null, noon(5))).b.target === null, 'it froze today: not a target until tomorrow');
ok((await call('GET', '/api/rq/today', null, four(6, -1))).b.target === null, '3:59am: still day 5, no target');
const t1 = (await call('GET', `/api/rq/today?playerId=${P(50)}`, null, four(6, 1))).b, t2 = (await call('GET', `/api/rq/today?playerId=${P(51)}`, null, noon(6))).b;
ok(t1.day === 6 && t1.target.qid === 'rq_test_a' && t2.target.qid === 'rq_test_a' && t1.max === 4000, '4:01am: day 6 has a target, the same for everyone, and the day is out of 4,000');
noNumbers(t1, '/api/rq/today before guessing');
// ---------- nothing shows the target's result before you guess ----------
for (const [path, t] of [['/api/home', noon(6)], ['/api/stats', noon(6)], [`/api/rq/open?playerId=${P(50)}`, noon(6)], [`/api/me?playerId=${P(50)}&recap=1`, noon(6)], ['/api/health', noon(6)]]) {
  const o = (await call('GET', path, null, t)).b; ok(!JSON.stringify(o).includes('rq_test_a') && !JSON.stringify(o).includes('cried in Stauffer') || path.includes('open') && !JSON.stringify(o).includes('rq_test_a'), `${path.split('?')[0]}: the target's result isn't there`);
}
// ---------- the guess is scored on the server; a retry can't change it ----------
const pct = 100 * F.yes / F.n, g1 = (await call('POST', '/api/rq/guess', { playerId:P(50), day:6, guess:50 }, noon(6))).b;
ok(g1.points === Math.max(0, Math.round(1000 - 25 * Math.abs(50 - pct))) && g1.n === 30 && g1.yes === F.yes, `guess 50 vs real ${pct.toFixed(1)}%: ${g1.points} points, then the real result is shown`);
const g2 = (await call('POST', '/api/rq/guess', { playerId:P(50), day:6, guess:Math.round(pct) }, noon(6))).b;
ok(g2.already && g2.guess === 50 && g2.points === g1.points, 'retrying with a better guess: the first guess stands');
const both = await Promise.all([40, 41, 42].map(x => call('POST', '/api/rq/guess', { playerId:P(51), day:6, guess:x }, noon(6))));
ok(new Set(both.map(x => x.b.guess)).size === 1, 'three guesses from one player arriving together: one counts');
ok((await call('POST', '/api/rq/guess', { playerId:P(52), day:5, guess:50 }, noon(6))).s === 409, 'a guess for another day is refused');
ok((await call('GET', `/api/rq/today?playerId=${P(50)}`, null, noon(6))).b.guessed.points === g1.points, 'after guessing, a reload shows your result');
// ---------- the day's score: the server's guess points, out of 4,000 ----------
const sc = (await call('POST', '/api/score', { playerId:P(50), day:6, pts:[null, 800, 1000, 700, 900] }, noon(6))).b;
ok(sc.max === 4000 && sc.total === 800 + g1.points + 700 + 900, `score: the page claimed 1,000 for the guess, the server used ${g1.points}; out of 4,000`);
const rec = JSON.parse(mem.get(`score/6/${P(50)}`)); ok(rec.v === 3 && rec.max === 4000 && rec.pts[2] === g1.points, 'saved as a v3 day with its own max');
const noGuess = (await call('POST', '/api/score', { playerId:P(53), day:6, pts:[null, 500, 900, 500, 500] }, noon(6))).b;
ok(noGuess.total === 1500 && noGuess.max === 4000, 'no guess on a target day: 0 for that round, still out of 4,000');
// ---------- a mixed 3,000 / 4,000 week, end to end: crews (today, week, league, wins, streak, recap, crew of the week) and houses ----------
const [X, Y, Z] = [60, 61, 62].map(P);
const crew = (await call('POST', '/api/crews', { playerId:X, nick:'Xan', name:'Mixed Week' }, noon(5))).b.code;
for (const [id, n] of [[Y, 'Yas'], [Z, 'Zed']]) await call('POST', `/api/crews/${crew}/join`, { playerId:id, nick:n }, noon(5));
const hs = (await call('POST', '/api/houses', { playerId:X, nick:'Xan', name:'Mixed House' }, noon(5))).b.code;
for (const id of [Y, Z]) await call('POST', `/api/houses/${hs}/join`, { playerId:id }, noon(5));
for (const [id, v] of [[X, 900], [Y, 600], [Z, 300]]) await call('POST', '/api/score', { playerId:id, day:5, pts:[null, v, null, v, v] }, noon(5));     // day 5: 90%, 60%, 30% of 3,000
await call('POST', '/api/rq/guess', { playerId:X, day:6, guess:70 }, noon(6)); await call('POST', '/api/rq/guess', { playerId:Y, day:6, guess:30 }, noon(6));   // 1,000 and 0 points
await call('POST', '/api/score', { playerId:X, day:6, pts:[null, 600, 0, 600, 600] }, noon(6));   // 2,800 / 4,000 = 70%
await call('POST', '/api/score', { playerId:Y, day:6, pts:[null, 1000, 999, 1000, 1000] }, noon(6));   // 3,000 / 4,000 = 75% (guess was 0)
await call('POST', '/api/score', { playerId:Z, day:6, pts:[null, 1000, 1000, 1000, 1000] }, noon(6));   // no guess: 3,000 / 4,000 = 75%
const td = (await call('GET', `/api/crews/${crew}?playerId=${X}`, null, noon(6))).b;
ok(td.members.every(m => m.max === 4000) && td.members[0].total === 3000, 'crew TODAY on a 4,000 day: raw points, same max for everyone');
const wk6 = (await call('GET', `/api/crews/${crew}/week?playerId=${X}`, null, noon(6))).b;
ok(wk6.members.map(m => `${m.nick}:${m.pct}:${m.played}`).join(' ') === 'Xan:80:2 Yas:67.5:2 Zed:52.5:2', 'crew WEEK mixes a 3,000 and a 4,000 day as % (80, 67.5, 52.5), days played shown');
const lg6 = (await call('GET', `/api/crews/${crew}/league?playerId=${X}`, null, noon(6))).b;
ok(lg6.members.map(m => `${m.nick}:${m.wins}W:${m.avg}`).join(' ') === 'Xan:1W:80 Yas:1W:67.5 Zed:1W:52.5' && lg6.members.every(m => m.streak === 2), 'crew LEAGUE: wins by raw points on each day (Yas + Zed tie day 6), averages in %, streaks intact');
const cw = (await call('GET', '/api/home', null, noon(6) + 6 * 60e3)).b.crewOfWeek; ok(cw && cw.name === 'Mixed Week' && cw.pct === 66.7, 'crew of the week: average of each member\'s average % (66.7)');
const mon = (await call('GET', `/api/me?recap=1&playerId=${Z}`, null, noon(7))).b.crews.find(c => c.code === crew).lastWeek;
ok(mon && mon.winners[0].nick === 'Xan' && mon.winners[0].pct === 80 && mon.losers[0].nick === 'Zed' && mon.losers[0].you, 'Monday recap of the mixed week: winner and loser by %');
const hl = (await call('GET', `/api/league?playerId=${X}`, null, noon(6))).b; ok(hl.mine.pct === 66.7 && hl.mine.qualified, 'House League on the mixed week: 66.7%');
// ---------- after the target's day: shown on the home page, never a target again ----------
const h7 = (await call('GET', '/api/home', null, noon(7))).b;
ok(h7.closed.length === 1 && h7.closed[0].n === 30 && /cried in Stauffer/.test(h7.closed[0].q) && mem.has('rqpub/rq_test_a'), 'day 7: the home page shows the real result, marked public');
ok((await call('GET', '/api/rq/today', null, noon(7))).b.target === null, 'day 7: the same question is never a target twice');
// ---------- a result the old home page could already show is never a target ----------
await store.setJSON('agg/3/0', { n:34, yes:20, q:'TEST D' });
for (let i = 100; i < 130; i++) await ans(i, 'rq_test_d', true, 4);
ok(mem.has('rqf/rq_test_d') && (await call('GET', '/api/rq/today', null, noon(8))).b.target === null, 'frozen, but already public under the old rule: never a target');
// ---------- answers arriving together don't corrupt the count ----------
await Promise.all(Array.from({ length:40 }, (_, i) => ans(200 + i, 'rq_test_c', i % 2 === 0, 3)));
const FC = JSON.parse(mem.get('rqf/rq_test_c')), keysC = [...mem.keys()].filter(k => k.startsWith('rqa/rq_test_c/')).length;
ok(FC.n === 30 && keysC === 40, `40 answers at once: all 40 saved once, frozen once at exactly ${FC.n}`);
// ---------- expiry: 29 by the deadline is never published ----------
for (let i = 300; i < 329; i++) await ans(i, 'rq_test_b', true, 1 + (i % 14));
ok(!mem.has('rqf/rq_test_b'), 'question B: 29 answers over 14 days, not frozen');
ok((await ans(400, 'rq_test_b', true, 15)).s === 409, 'day 15: question B is closed, no more answers');
const o15 = (await call('GET', `/api/rq/open?playerId=${P(401)}`, null, noon(15))).b.open;
ok(!o15.some(q => q.qid === 'rq_test_b') && !JSON.stringify((await call('GET', '/api/home', null, noon(16))).b).includes('ARC'), 'an expired question is never offered, frozen, targeted or shown');
// ---------- open questions after the Daily: up to 3, never ones you answered, never counts ----------
setBank([...Array.from({ length:5 }, (_, i) => ({ id:'rq_open_' + i, v:1, text:'OPEN ' + i, firstDay:10, round:0, repeats:[] })), { id:'rq_test_a', v:1, text:'TEST A', firstDay:1, round:0, repeats:[] }]);
await ans(500, 'rq_open_0', true, 11);
const op = (await call('GET', `/api/rq/open?playerId=${P(500)}`, null, noon(11))).b.open;
ok(op.length === 3 && !op.some(q => q.qid === 'rq_open_0') && !op.some(q => q.qid === 'rq_test_a') && !/"n"|"yes"/.test(JSON.stringify(op)), 'open questions: 3, not the one you answered, not frozen ones, text only');
console.log('frozen receipts tests passed');

// Tests the Crews API with an in-memory store standing in for Netlify Blobs. Run: npm test
import { handle, torontoDay, dowOf, mondayOf } from './lib/crews.mjs';

const mem = new Map();
const store = {
  async get(k){ return mem.has(k) ? JSON.parse(mem.get(k)) : null; },
  async setJSON(k, v){ mem.set(k, JSON.stringify(v)); },
  async list({ prefix }){ return { blobs: [...mem.keys()].filter(k => k.startsWith(prefix)).map(key => ({ key })) }; },
};
const call = async (method, path, body, now) => { const r = await handle(new Request('https://offcampusontario.ca' + path, { method, body: body ? JSON.stringify(body) : undefined }), store, now); return { status: r.status, body: await r.json() }; };
const ok = (c, m) => { if (!c) { console.error('FAIL:', m); process.exit(1); } console.log('ok -', m); };

const day = torontoDay();
ok((await call('GET', '/api/health')).body.day === day, 'health');
const A = 'a'.repeat(16), B = 'b'.repeat(16), C = 'c'.repeat(16);
const made = await call('POST', '/api/crews', { playerId: A, nick: 'Josh', name: 'Princess St Crew' });
ok(made.status === 200 && /^[A-Z0-9]{6}$/.test(made.body.code), 'create crew');
const code = made.body.code;
ok((await call('POST', `/api/crews/${code}/join`, { playerId: B, nick: 'Maya' })).body.size === 2, 'join crew');
await call('POST', `/api/crews/${code}/join`, { playerId: B, nick: 'Maya' });
ok((await call('GET', `/api/crews/${code}`)).body.size === 2, 'joining twice does not duplicate');
ok((await call('POST', '/api/score', { playerId: A, day, total: 3450, pts: [900, 650, 800, 600, 500] })).status === 200, 'post score');
ok((await call('POST', '/api/score', { playerId: A, day, total: 5000, pts: [1000, 1000, 1000, 1000, 1000] })).body.total === 3450, 'first score of the day is kept');
ok((await call('POST', '/api/score', { playerId: B, day, total: 9000, pts: [1000, 1000, 1000, 1000, 5000] })).status === 400, 'reject impossible score');
ok((await call('POST', '/api/score', { playerId: B, day: day + 3, total: 100, pts: [20, 20, 20, 20, 20] })).status === 409, 'reject wrong day');
await call('POST', '/api/score', { playerId: B, day, total: 3600, pts: [900, 900, 800, 500, 500] });
const board = await call('GET', `/api/crews/${code}?playerId=${A}`);
ok(board.body.played === 2 && board.body.members[0].nick === 'Maya' && board.body.members[1].you === true, 'board ranks scores and marks you');
ok(!('id' in board.body.members[0]) && !JSON.stringify(board.body).includes(A), 'player ids are not exposed');
ok(board.body.members[1].streak === 1, 'streak counts today');
const me = await call('GET', `/api/me?playerId=${A}`); ok(me.body.crews.length === 1 && me.body.nick === 'Josh', 'my crews');
ok((await call('POST', '/api/crews/ZZZZZZ/join', { playerId: C, nick: 'x' })).status === 404, 'unknown crew');
ok((await call('POST', '/api/crews', { playerId: 'bad', name: 'x' })).status === 400, 'bad player id');
const evil = await call('POST', '/api/crews', { playerId: C, nick: '<b>x</b>', name: '<script>' });
ok(evil.status === 400 || !/[<>]/.test(evil.body.name || ''), 'strips < >');
ok((await call('GET', '/api/stats')).body.playersToday === 2, 'stats');
// tomorrow: Maya plays again, so her streak is 2; Josh hasn't played yet, so his streak still shows 1
const later = Date.now() + 864e5, day2 = torontoDay(later);
await call('POST', '/api/score', { playerId: B, day: day2, total: 100, pts: [20, 20, 20, 20, 20] }, later);
const b2 = (await call('GET', `/api/crews/${code}`, null, later)).body;
ok(b2.members.find(m => m.nick === 'Maya').streak === 2 && b2.members.find(m => m.nick === 'Josh').streak === 1 && b2.played === 1, 'streaks carry over to the next day');
const lg = (await call('GET', `/api/crews/${code}/league?playerId=${B}`, null, later)).body;
ok(lg.members.length === 2 && lg.members[0].nick === 'Maya' && lg.members[0].wins === 1 && lg.members[0].played === 2 && lg.members[0].you === true, 'league: wins and days played');
ok(lg.members.find(m => m.nick === 'Josh').avg === 3450 && lg.best.pin && lg.best.pin.nick === 'Josh' && lg.best.showdown.nick === 'Josh' && lg.members.find(m => m.nick === 'Maya').showdown === 360, 'league: averages and best at each game');
ok(!JSON.stringify(lg).includes(A) && !JSON.stringify(lg).includes(B), 'league hides player ids');
ok((await call('GET', '/api/crews/ZZZZZZ/league')).status === 404, 'league: unknown crew');
const st = (await call('GET', '/api/stats', null, later)).body;
ok(st.playersToday === 1 && st.playersYesterday === 2 && st.cameBackToday === 1 && st.last7Days.length >= 2, 'stats: came back the next day ' + JSON.stringify(st));
// real answers: first answer per round counts, Queen's split hidden under 5, crew split hidden under 5
const day3 = torontoDay(later); const ids = 'defgh'.split('').map(ch => ch.repeat(16));
for (const id of ids) await call('POST', `/api/crews/${code}/join`, { playerId:id, nick:'P' + id[0] }, later);
let ra = (await call('POST', '/api/answer', { playerId:A, day:day3, round:0, yes:true }, later)).body;
ok(ra.queens.hidden === true && ra.queens.n === 1 && ra.crews[0].hidden === true, 'answers: hidden while there are few');
await call('POST', '/api/answer', { playerId:A, day:day3, round:0, yes:false }, later);
for (const [k, id] of ids.entries()) ra = (await call('POST', '/api/answer', { playerId:id, day:day3, round:0, yes:k < 2 }, later)).body;
ok(ra.queens.n === 6 && ra.queens.yes === 3 && !ra.queens.hidden, "answers: real Queen's split once there are 5+ (and only the first answer counts)");
ok(ra.crews[0].n === 6 && ra.crews[0].yes === 3 && ra.crews[0].name === 'Princess St Crew', 'answers: crew split once 5+ in the crew answered');
ok((await call('POST', '/api/answer', { playerId:A, day:day3, round:1, texts:['  scroll <b>tiktok</b> ', 'nap'] }, later)).status === 200, 'answers: typed showdown answers saved');
ok((await call('POST', '/api/answer', { playerId:A, day:day3 + 1, round:0, yes:true }, later)).status === 409, 'answers: wrong day rejected');
ok((await call('POST', '/api/answer', { playerId:A, day:day3, round:0 }, later)).status === 400, 'answers: needs yes or no');
// recap: yesterday's crew results
const rc = (await call('GET', `/api/me?playerId=${A}&recap=1`, null, later)).body.crews[0].yesterday;
ok(rc.played === 2 && rc.top.nick === 'Maya' && rc.second.nick === 'Josh' && rc.myRank === 2 && rc.myTotal === 3450, 'recap: yesterday winner, my rank');
// save your spot + log in elsewhere
ok((await call('POST', '/api/pin', { playerId:A, nick:'Josh', pin:'12a4' }, later)).status === 400, 'pin: must be 4 numbers');
ok((await call('POST', '/api/pin', { playerId:A, nick:'Josh', pin:'4821' }, later)).status === 200, 'pin: saved');
ok((await call('POST', '/api/pin', { playerId:B, nick:'josh', pin:'1111' }, later)).status === 409, 'pin: name already taken by someone else');
ok((await call('GET', `/api/me?playerId=${A}`, null, later)).body.saved === true, 'pin: me says saved');
ok((await call('POST', '/api/login', { nick:'JOSH', pin:'0000' }, later)).status === 401, 'login: wrong pin');
const li = (await call('POST', '/api/login', { nick:' josh ', pin:'4821' }, later)).body;
ok(li.playerId === A && li.nick === 'Josh' && li.streak.days === 1 && li.streak.best === 3450 && li.today === null, 'login: right pin gives back the player and streak');
for (let k = 0; k < 5; k++) await call('POST', '/api/login', { nick:'Josh', pin:'9999' }, later);
ok((await call('POST', '/api/login', { nick:'Josh', pin:'4821' }, later)).status === 429, 'login: locked after 5 wrong tries');
ok(!JSON.stringify(li).includes('pinHash') && !JSON.stringify(li).includes('salt'), 'login: never sends the pin back');
// ---------- club games ----------
process.env.OC_ADMIN_KEY = 'josh-admin-test-key';
const cards = [ { kind:'yn', q:'Have you ever skipped a run for brunch?' }, { kind:'yn', q:'Have you ever run a marathon?' }, { kind:'yn', q:'Have you ever lied about your pace?' },
  { kind:'pop', q:'First move after a run?', opts:['Water', 'Food', 'Stretch', 'Couch'] }, { kind:'trivia', q:'Where do we meet?', opts:['The ARC', 'Stauffer', 'City Hall'], right:0 },
  { kind:'tot', q:'old kind', opts:['a', 'b'] } ];
ok((await call('POST', '/api/clubs', { playerId:A, nick:'Josh', name:'Run', cards:cards.slice(0, 2) })).status === 400, 'club: needs 3+ questions');
ok((await call('POST', '/api/clubs', { playerId:A, name:'Run', cards:[cards[0], cards[1], { kind:'pop', q:'Same twice?', opts:['A', 'a'] }] })).status === 400, 'club: options must be different');
const mk = (await call('POST', '/api/clubs', { playerId:A, nick:'Josh', name:"Queen's Run Club!", type:'sports', cards })).body;
ok(mk.slug === 'queen-s-run-club' && mk.key && /^[A-Z0-9]{6}$/.test(mk.crew), 'club: made with a slug, exec key and crew');
ok((await call('POST', '/api/clubs', { playerId:B, name:"Queen's Run Club", cards })).body.slug === 'queen-s-run-club-2', 'club: second club with the same name gets its own link');
const g = (await call('GET', `/api/clubs/${mk.slug}?playerId=${A}`)).body;
ok(g.cards.length === 5 && g.name === "Queen's Run Club!" && g.me === null && g.released === false && g.played === 0, 'club: game loads (old card kind dropped)');
ok(!('right' in g.cards[4]) && !JSON.stringify(g).includes(mk.key) && g.exec === false, 'club: the trivia answer and exec key are not sent to players');
ok((await call('GET', `/api/clubs/${mk.slug}?k=${mk.key}`)).body.exec === true, 'club: exec key is recognised');
const P = ['p','q','r','s','t','u'].map(x => x.repeat(16));
const pop = [0, 1, 1, 1, 2, 0], popGuess = [0, 1, 2, 2, 0, 0], triv = [0, 0, 0, 0, 1, 0];
const play = async (k, id, upto = 5) => { for (let i = 0; i < upto; i++) {
  const body = [ { answer:k < 4, guess:67 }, { answer:false, guess:k === 0 ? 0 : 50 }, { answer:k < 3, guess:50 }, { answer:pop[k], guess:popGuess[k] }, { answer:triv[k] } ][i];
  const r = await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:id, nick:'N' + k, card:i, ...body }); if (r.status !== 200) return r; } };
ok((await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:P[0], card:0, answer:true })).status === 400, 'club answer: yes/no needs a guess');
ok((await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:P[0], card:3, answer:1 })).status === 400, 'club answer: most popular needs a guess');
const t1 = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:P[0], nick:'N0', card:4, answer:0 })).body;
ok(t1.right === 0 && !('result' in t1) && t1.done === false, 'club answer: trivia says right/wrong straight away, no numbers before release');
const y1 = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:P[0], card:0, answer:true, guess:67 })).body;
ok(y1.ok && !('result' in y1) && !('points' in y1), 'club answer: no numbers or points before release');
for (let k = 0; k < 4; k++) await play(k, P[k]);
await play(4, P[4], 3);   // P4 stops after 3 cards
const again = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:P[0], card:0, answer:false, guess:5 })).body;
ok(again.already === true && again.done === true, 'club answer: first answer counts, a retry changes nothing');
const pre = (await call('GET', `/api/clubs/${mk.slug}/results?playerId=${P[0]}`)).body;
ok(pre.released === false && pre.played === 4 && !('cards' in pre) && !('board' in pre), 'club results: before release only the number who played');
ok((await call('POST', `/api/clubs/${mk.slug}/release`, { k:'wrong' })).status === 403, 'club release: exec only');
const early = await call('POST', `/api/clubs/${mk.slug}/release`, { k:mk.key });
ok(early.status === 409 && early.body.players === 4 && early.body.need === 5, 'club release: needs 5 to have finished');
await play(5, P[5]);
const rel = (await call('POST', `/api/clubs/${mk.slug}/release`, { k:mk.key })).body;
ok(rel.released === true && rel.players === 5, 'club release: works once 5 finished');
ok((await call('POST', `/api/clubs/${mk.slug}/release`, { k:mk.key })).body.already === true, 'club release: releasing twice changes nothing');
const res = (await call('GET', `/api/clubs/${mk.slug}/results?playerId=${P[0]}`)).body;
// counted: P0-P3, P5 finished, P4 answered cards 0-2 before release (counts for those cards)
ok(res.released && res.players === 5 && res.cards[0].n === 6 && res.cards[0].yes === 4, 'club results: real counts (16 of 25 style)');
ok(res.cards[3].n === 5 && res.cards[3].counts.join() === '2,3,0,0' && res.cards[4].right === 5, 'club results: most popular counts and trivia');
// P0: card0 guess 67 vs 66.67 -> 993, card1 guess 0 vs 0 -> 1000, card2 guess 50 vs 50 -> 1000, pop guess 0 (not top) -> 0, trivia right -> 1000
ok(res.me.score === 3993 && res.me.cards[0].points === 993 && res.me.cards[3].points === 0, 'club scoring: everyone scored against the same frozen numbers');
const sc = res.board.map(r => r.nick + ':' + r.rank + ':' + r.score).join(' ');
ok(res.board.find(r => r.nick === 'N2').rank === res.board.find(r => r.nick === 'N3').rank, 'club leaderboard: ties share a rank (' + sc + ')');
ok(res.board.length === 5 && !res.board.some(r => r.nick === 'N4'), 'club leaderboard: only people who finished');
ok(!JSON.stringify(res).includes(P[0]), 'club results: no player ids');
const late = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:'z'.repeat(16), nick:'Late', card:0, answer:false, guess:70 })).body;
ok(late.released && late.result.yes === 4 && late.points === 1000 - Math.round(20 * (70 - 400 / 6)) , 'club late player: scored straight away against the frozen numbers');
const fin4 = await play(4, P[4]);   // P4 finishes after the release
const res2 = (await call('GET', `/api/clubs/${mk.slug}/results?playerId=${P[4]}`)).body;
ok(res2.cards[0].yes === 4 && res2.cards[0].n === 6 && res2.players === 5 && res2.me && res2.ranked === 6, 'club results: late answers never change the frozen results, but late players get a score');
const other = (await call('POST', '/api/clubs', { playerId:B, name:'Climbing', cards:cards.slice(0, 5) })).body;
ok((await call('GET', `/api/clubs/${other.slug}?k=josh-admin-test-key`)).body.exec === true, 'club: Josh\'s admin key works on any club');
await store.setJSON('club/old-club', { name:'Old', cards:[{ kind:'tot', q:'a or b', opts:['a', 'b'] }, { kind:'yn', q:'yes?' }, { kind:'yn', q:'no?' }], crew:null, key:'x' });
ok((await call('GET', '/api/clubs/old-club')).body.legacy === true && (await call('POST', '/api/clubs/old-club/answer', { playerId:A, card:1, answer:true, guess:5 })).status === 410, 'club: old-format games say so');
ok((await call('GET', '/api/clubs/nope-club')).status === 404, 'club: unknown club');
const crewOfClub = (await call('GET', `/api/crews/${mk.crew}`)).body; ok(crewOfClub.name === "Queen's Run Club!" && crewOfClub.size === 1, 'club: its crew exists, nobody added without asking');
await call('POST', `/api/crews/${mk.crew}/join`, { playerId:P[1], nick:'N1' });
await call('POST', '/api/score', { playerId:P[1], day, total:2000, pts:[400, 400, 400, 400, 400] });
const cst = (await call("GET", "/api/stats")).body.clubs.find(c => c.slug === mk.slug);
ok(cst.started === 7 && cst.finished === 6 && cst.released && cst.joinedCrew === 1 && cst.playedDaily === 1, "stats: club players into the daily and crew (" + JSON.stringify(cst) + ')');

// ---------- weeks, stakes, sources, suggestions, admin, home ----------
const at = d => Date.parse('2026-11-03T17:00:00Z') + (d - 1) * 864e5;   // noon Toronto on day d
ok(dowOf(1) === 2 && dowOf(7) === 1 && mondayOf(7) === 7 && mondayOf(13) === 7 && mondayOf(6) === 0, 'weeks run Monday to Sunday (day 7 = Mon Nov 9)');
const W = ['w1', 'w2', 'w3', 'w4'].map(x => x.repeat(8));
const wc = (await call('POST', '/api/crews', { playerId:W[0], nick:'Maya', name:'517' }, at(7))).body.code;
for (const [i, n] of [[1, 'Sam'], [2, 'Jo']]) await call('POST', `/api/crews/${wc}/join`, { playerId:W[i], nick:n }, at(7));
const scW = async (id, d, t, src) => call('POST', '/api/score', { playerId:id, day:d, total:t, pts:[t / 5, t / 5, t / 5, t / 5, t / 5], src }, at(d));
await scW(W[0], 7, 3000, 'insta'); await scW(W[1], 7, 2000, 'crew'); await scW(W[2], 7, 1000, 'insta');
await scW(W[0], 8, 3000); await scW(W[1], 8, 4500);
await scW(W[0], 9, 3000);
const wk = (await call('GET', `/api/crews/${wc}/week?playerId=${W[1]}`, null, at(9))).body;
ok(wk.from === 7 && wk.to === 13 && wk.members[0].nick === 'Maya' && wk.members[0].total === 9000 && wk.members[1].total === 6500 && wk.members[1].you, 'week view: totals Monday to today');
ok(wk.stake === null && wk.lastWeek === null && wk.daysLeft === 4, 'week view: no stake yet, no last week');
ok((await call('POST', `/api/crews/${wc}/stake`, { playerId:W[3], win:'x', lose:'y' }, at(9))).status === 403, 'stake: members only');
ok((await call('POST', `/api/crews/${wc}/stake`, { playerId:W[2], win:'', lose:'' }, at(9))).status === 400, 'stake: needs something');
const st1 = (await call('POST', `/api/crews/${wc}/stake`, { playerId:W[2], win:'Picks the movie', lose:'Cleans the kitchen' }, at(9))).body;
ok(st1.stake.win === 'Picks the movie' && st1.stake.lose === 'Cleans the kitchen' && !JSON.stringify(st1).includes(W[2]), 'stake: set for the week, no player ids sent');
const meMon = (await call('GET', `/api/me?recap=1&playerId=${W[2]}`, null, at(14))).body.crews.find(c => c.code === wc);
ok(meMon.lastWeek && meMon.lastWeek.winners[0].nick === 'Maya' && meMon.lastWeek.losers[0].nick === 'Jo' && meMon.lastWeek.losers[0].you && meMon.lastWeek.stake.lose === 'Cleans the kitchen', 'Monday recap: last week\'s winner, loser and stake');
const meTue = (await call('GET', `/api/me?recap=1&playerId=${W[2]}`, null, at(15))).body.crews.find(c => c.code === wc);
ok(!meTue.lastWeek, 'recap: last week only shows on Monday');
ok((await call('GET', `/api/crews/${wc}/week`, null, at(14))).body.stake.lose === 'Cleans the kitchen', 'stake carries over to the next week until changed');
// sources and coming back
const stS = (await call('GET', '/api/stats', null, at(9))).body;
const insta = stS.sources.find(x => x.src === 'insta');
ok(insta && insta.players === 2 && insta.d1.of === 2 && insta.d1.back === 1 && insta.d7.of === 0, 'stats: players by source and next-day return (' + JSON.stringify(insta) + ')');
ok(stS.sources.some(x => x.src === 'crew'), 'stats: crew source counted');
const today9 = stS.playersToday;
await call('POST', '/api/hideme', { playerId:W[0] }, at(9));
const stH = (await call('GET', '/api/stats', null, at(9))).body;
ok(stH.playersToday === today9 - 1 && stH.sources.find(x => x.src === 'insta').players === 1 && stH.hiddenBrowsers === 1, 'stats: hidden browser left out');
// admin + suggestions
ok((await call('POST', '/api/suggest', { playerId:W[1], kind:'receipts', q:'short' }, at(9))).status === 400, 'suggest: needs a real question');
ok((await call('POST', '/api/suggest', { playerId:W[1], kind:'survey', q:'Name a place you cry on campus', credit:'@maya.k<script>' }, at(9))).status === 200, 'suggest: saved');
for (let i = 0; i < 4; i++) await call('POST', '/api/suggest', { playerId:W[1], kind:'receipts', q:'Have you ever slept in Stauffer #' + i }, at(9));
ok((await call('POST', '/api/suggest', { playerId:W[1], kind:'receipts', q:'Have you ever slept in Douglas' }, at(9))).status === 429, 'suggest: 5 a day per player');
ok((await call('GET', '/api/suggestions?k=nope', null, at(9))).status === 403, 'suggestions: admin only');
const cl = (await call('POST', '/api/admin/claim', { playerId:W[3] }, at(9))).body;
ok(cl.key && cl.key.length === 24, 'admin: first claim gets the key');
ok((await call('POST', '/api/admin/claim', { playerId:W[2] }, at(9))).status === 409, 'admin: can only be claimed once');
const sl = (await call('GET', '/api/suggestions?k=' + cl.key, null, at(9))).body.list;
ok(sl.length === 5 && sl.filter(x => x.kind === 'survey').length === 1 && sl.find(x => x.kind === 'survey').credit === 'maya.kscript', 'suggestions: Josh sees them, credit cleaned');
ok((await call('GET', `/api/clubs/${mk.slug}?k=${cl.key}`, null, at(9))).body.exec === true, 'admin key works on club games');
// home: yesterday's real result + crew of the week
for (let i = 0; i < 12; i++) await call('POST', '/api/answer', { playerId:('h' + i).padEnd(14, 'x'), day:8, round:2, yes:i < 8, q:'Have you ever cried in Stauffer?' }, at(8));
await call('POST', '/api/crews/' + wc + '/join', { playerId:W[3], nick:'Lee' }, at(9));
const hm = (await call('GET', '/api/home', null, at(9))).body;
ok(hm.yesterday && hm.yesterday.n === 12 && hm.yesterday.yes === 8 && /cried in Stauffer/.test(hm.yesterday.q), 'home: yesterday\'s real result');
ok(hm.crewOfWeek && hm.crewOfWeek.name === '517' && hm.crewOfWeek.players === 3, 'home: crew of the week');
console.log('all tests passed');

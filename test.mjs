// Tests the Crews API with an in-memory store standing in for Netlify Blobs. Run: npm test
import { handle, torontoDay } from './lib/crews.mjs';

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
const cards = [ { kind:'yn', q:'Have you ever skipped a run for brunch?' }, { kind:'tot', q:'Pick one', opts:['Sunrise run', 'Sunset run'] },
  { kind:'name', q:'Name something every runner says' }, { kind:'trivia', q:'Where do we meet?', opts:['The ARC', 'Stauffer', 'City Hall'], right:0 }, { kind:'bad', q:'x' } ];
ok((await call('POST', '/api/clubs', { playerId:A, nick:'Josh', name:'Run', cards:cards.slice(0, 2) })).status === 400, 'club: needs 3+ questions');
const mk = (await call('POST', '/api/clubs', { playerId:A, nick:'Josh', name:"Queen's Run Club!", type:'sports', cards })).body;
ok(mk.slug === 'queen-s-run-club' && mk.key && /^[A-Z0-9]{6}$/.test(mk.crew), 'club: made with a slug, admin key and crew');
ok((await call('POST', '/api/clubs', { playerId:B, name:"Queen's Run Club", cards })).body.slug === 'queen-s-run-club-2', 'club: second club with the same name gets its own link');
const g = (await call('GET', `/api/clubs/${mk.slug}?playerId=${A}`)).body; ok(g.cards.length === 4 && g.name === "Queen's Run Club!" && g.me === null, 'club: game loads (bad card dropped)');
const players = ['p','q','r','s'].map(x => x.repeat(16));
let first = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:players[0], nick:'P', card:0, answer:true })).body;
ok(first.before.n === 0, 'club answer: first player sees nobody before them');
for (const [k, id] of players.entries()) {
  await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:id, nick:'N' + k, card:0, answer:k < 3 });
  await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:id, card:1, answer:k % 2 });
  await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:id, card:2, answer:k < 3 ? ['  "Just 3K" ', 'easy pace'] : ['wait for my garmin'] });
  await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:id, card:3, answer:k === 3 ? 2 : 0 });
  await call('POST', `/api/clubs/${mk.slug}/score`, { playerId:id, nick:'N' + k, score:1000 + k * 500 });
}
const late = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:'z'.repeat(16), card:2, answer:['just 3k', 'pizza'] })).body;
ok(late.before.hits === 1 && !('keys' in late.before), 'club answer: typed answers score against clubmates without leaking them');
const again = (await call('POST', `/api/clubs/${mk.slug}/answer`, { playerId:players[0], card:0, answer:false })).body;
ok(again.already === true && again.before.n === 4 && again.before.yes === 3, 'club answer: first answer counts, results come back');
const res = (await call('GET', `/api/clubs/${mk.slug}/results?playerId=${players[3]}&k=${mk.key}`)).body;
ok(res.players === 5 && res.cards[0].yes === 3 && res.cards[1].split[0] === 2 && res.cards[3].right === 3, 'club results: yes/no, this or that, trivia');
ok(res.cards[2].top.length === 2 && res.cards[2].top[0].n === 4 && !res.cards[2].top.some(x => /garmin/i.test(x.t)), 'club results: typed answers only show when 2+ gave them');
ok(res.board[0].nick === 'N3' && res.board[0].you === true && res.myRank === 1 && res.admin === true, 'club results: leaderboard and admin key');
ok(!JSON.stringify(res).includes(players[0]), 'club results: no player ids');
ok((await call('GET', '/api/clubs/nope-club')).status === 404, 'club: unknown club');
const crewOfClub = (await call('GET', `/api/crews/${mk.crew}`)).body; ok(crewOfClub.name === "Queen's Run Club!" && crewOfClub.size === 1, 'club: its crew exists for the daily league');
console.log('all tests passed');

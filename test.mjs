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
console.log('all tests passed');

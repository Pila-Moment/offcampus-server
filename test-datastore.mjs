// Tests which data store each kind of deploy uses, and that test deploys never touch production data. Run: npm test
import { chooseStore, makeApi, PRODUCTION_STORE } from './lib/datastore.mjs';
import { handle, torontoDay } from './lib/crews.mjs';

const ok = (c, m) => { if (!c) { console.error('FAIL:', m); process.exit(1); } console.log('ok -', m); };

// In-memory stand-ins for Netlify Blobs, one per store name, and a record of every store opened.
const stores = new Map(), opened = [];
const memStore = () => { const mem = new Map(); return {
  mem,
  async get(k){ return mem.has(k) ? JSON.parse(mem.get(k)) : null; },
  async setJSON(k, v){ mem.set(k, JSON.stringify(v)); },
  async list({ prefix } = {}){ return { blobs:[...mem.keys()].filter(k => !prefix || k.startsWith(prefix)).map(key => ({ key })) }; },
}; };
const getStoreFn = ({ name }) => { opened.push(name); if (!stores.has(name)) stores.set(name, memStore()); return stores.get(name); };
const api = env => makeApi({ getStoreFn, handle, env });
const ctx = c => (c === undefined ? undefined : { deploy:{ context:c } });
const call = async (fn, c, method, path, body) => { const r = await fn(new Request('https://x.netlify.app' + path, { method, body:body ? JSON.stringify(body) : undefined }), ctx(c)); return { status:r.status, body:await r.json() }; };

// ---------- choosing the store ----------
ok(chooseStore('production', {}).name === PRODUCTION_STORE, 'production uses the existing store with no setting');
ok(chooseStore('production', { OC_TEST_STORE:'offcampus-test' }).name === 'offcampus', 'production ignores the test setting');
for (const c of ['deploy-preview', 'branch-deploy', 'dev', undefined, '', 'Production', 'something-new'])
  ok(!chooseStore(c, {}).ok, `"${c}" deploy with no setting is refused`);
for (const bad of ['offcampus', 'offcampus-live', 'Offcampus-test', 'offcampus-test-', 'offcampus-testing', 'test', 'offcampus-test-a/b', ' offcampus '])
  ok(!chooseStore('deploy-preview', { OC_TEST_STORE:bad }).ok, `test setting "${bad}" is refused`);
for (const good of ['offcampus-test', 'offcampus-test-2', 'offcampus-test-nov6', ' offcampus-test '])
  ok(chooseStore('deploy-preview', { OC_TEST_STORE:good }).name === good.trim(), `test setting "${good.trim()}" is used`);

// ---------- fail closed: no store is opened, every route answers 503 ----------
opened.length = 0;
for (const [c, env] of [['deploy-preview', {}], ['branch-deploy', { OC_TEST_STORE:'offcampus' }], [undefined, {}], ['dev', { OC_TEST_STORE:'' }]]) {
  const h = await call(api(env), c, 'GET', '/api/health');
  ok(h.status === 503 && h.body.data === 'none', `${c || 'no context'}: health says not configured (503)`);
  const s = await call(api(env), c, 'POST', '/api/score', { playerId:'a'.repeat(16), day:torontoDay(), total:5000, pts:[1000, 1000, 1000, 1000, 1000] });
  ok(s.status === 503, `${c || 'no context'}: a score is refused (503)`);
}
ok(opened.length === 0, 'an unconfigured deploy never opens any store, so it cannot read or write production');

// ---------- isolation: the same requests on production and on a preview land in different stores ----------
const prod = api({}), prev = api({ OC_TEST_STORE:'offcampus-test' }), day = torontoDay();
const P = 'p'.repeat(16), T = 't'.repeat(16);
ok((await call(prod, 'production', 'POST', '/api/score', { playerId:P, nick:'Real', day, total:3000, pts:[600, 600, 600, 600, 600] })).status === 200, 'production saves a score');
const prodBefore = JSON.stringify([...stores.get('offcampus').mem]);
ok((await call(prev, 'deploy-preview', 'POST', '/api/score', { playerId:T, nick:'Tester', day, total:4000, pts:[800, 800, 800, 800, 800] })).status === 200, 'preview saves a score');
await call(prev, 'deploy-preview', 'POST', '/api/answer', { playerId:T, day, round:0, yes:true });
await call(prev, 'deploy-preview', 'POST', '/api/crews', { playerId:T, nick:'Tester', name:'Test House' });
await call(prev, 'deploy-preview', 'POST', '/api/suggest', { playerId:T, kind:'receipts', q:'Ever tested in production?' });
ok(JSON.stringify([...stores.get('offcampus').mem]) === prodBefore, 'preview score, answer, crew and suggestion leave production data unchanged');
ok(![...stores.get('offcampus').mem.keys()].some(k => k.includes(T)), 'the preview player is not in production');
ok(![...stores.get('offcampus-test').mem.keys()].some(k => k.includes(P)), 'the production player is not in the test store');
const pst = await call(prev, 'deploy-preview', 'GET', '/api/stats');
ok(!JSON.stringify(pst.body).includes('Real'), 'preview stats cannot see production players');
const ph = await call(prev, 'deploy-preview', 'GET', '/api/health'), lh = await call(prod, 'production', 'GET', '/api/health');
ok(ph.body.data === 'test' && ph.body.store === 'offcampus-test' && ph.body.context === 'deploy-preview' && ph.body.ok, 'preview health says test data');
ok(lh.body.data === 'production' && lh.body.store === 'offcampus' && lh.body.day === day, 'production health says production data and still reports the day');
ok(new Set(opened).size === 2 && opened.every(n => n === 'offcampus' || n === 'offcampus-test'), 'only the two expected stores were ever opened');
console.log('datastore tests passed');

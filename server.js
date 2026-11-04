// Off Campus server: Crews (friend groups that compare daily scores).
// Plain Node, no packages. Data is kept in memory and saved to DATA_DIR/offcampus-data.json every few seconds.
'use strict';
const http = require('http');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ---------- settings you can change ----------
const PORT = Number(process.env.PORT) || 8080;
const DATA_DIR = process.env.DATA_DIR || path.join(__dirname, 'data');
const SAVE_EVERY_MS = 5000;
const FIRST_DAY = '2026-11-03';            // must match FIRST_DAY in the game (daily.html)
const MAX_SCORE = 5000;
const MAX_CREW_MEMBERS = 60;
const MAX_CREWS_PER_PLAYER = 10;
const NICK_MAX = 16, CREW_NAME_MAX = 28;
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'https://offcampusontario.ca,https://www.offcampusontario.ca,https://rad-pothos-d03a2a.netlify.app')
  .split(',').map(s => s.trim()).filter(Boolean);
const RATE = { windowMs: 60000, max: 300 };   // requests per address per minute
const BACKUP_DAYS = 14;

// ---------- data ----------
const FILE = path.join(DATA_DIR, 'offcampus-data.json');
let db = { crews: {}, players: {}, scores: {} };   // scores: { day: { playerId: { total, pts, at } } }
let dirty = false;
try { fs.mkdirSync(DATA_DIR, { recursive: true }); } catch (e) {}
try { db = Object.assign(db, JSON.parse(fs.readFileSync(FILE, 'utf8'))); console.log('loaded', Object.keys(db.crews).length, 'crews'); } catch (e) { console.log('starting with empty data'); }
function save(){
  if (!dirty) return; dirty = false;
  const tmp = FILE + '.tmp';
  try { fs.writeFileSync(tmp, JSON.stringify(db)); fs.renameSync(tmp, FILE); } catch (e) { dirty = true; console.error('save failed', e.message); }
}
function backup(){
  try {
    const dir = path.join(DATA_DIR, 'backups'); fs.mkdirSync(dir, { recursive: true });
    const name = 'offcampus-data-' + new Date().toISOString().slice(0, 10) + '.json';
    if (!fs.existsSync(path.join(dir, name)) && fs.existsSync(FILE)) fs.copyFileSync(FILE, path.join(dir, name));
    fs.readdirSync(dir).sort().slice(0, -BACKUP_DAYS).forEach(f => fs.unlinkSync(path.join(dir, f)));
  } catch (e) { console.error('backup failed', e.message); }
}
setInterval(save, SAVE_EVERY_MS).unref();
setInterval(backup, 3600e3).unref(); backup();
process.on('SIGTERM', () => { dirty = true; save(); process.exit(0); });

// ---------- helpers ----------
function torontoDay(){   // Daily number: No. 1 on FIRST_DAY, a new one at 4am Toronto time
  const s = new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date(Date.now() - 4 * 3600e3));
  return Math.max(1, Math.round((Date.parse(s) - Date.parse(FIRST_DAY)) / 864e5) + 1);
}
const CODE_CHARS = 'ABCDEFGHJKMNPQRSTUVWXYZ23456789';
function newCode(){ let c; do { c = ''; const b = crypto.randomBytes(6); for (let i = 0; i < 6; i++) c += CODE_CHARS[b[i] % CODE_CHARS.length]; } while (db.crews[c]); return c; }
const cleanText = (s, max) => String(s || '').replace(/[\u0000-\u001f<>]/g, '').replace(/\s+/g, ' ').trim().slice(0, max);
const validId = id => typeof id === 'string' && /^[a-z0-9]{12,40}$/i.test(id);
const hits = new Map();
function limited(ip){ const now = Date.now(); let h = hits.get(ip); if (!h || now - h.t > RATE.windowMs) { h = { t: now, n: 0 }; hits.set(ip, h); } return ++h.n > RATE.max; }
setInterval(() => { const now = Date.now(); for (const [k, v] of hits) if (now - v.t > RATE.windowMs) hits.delete(k); }, 60000).unref();

function crewView(code, day){
  const c = db.crews[code]; if (!c) return null;
  const today = db.scores[day] || {};
  const members = c.members.map(id => {
    const p = db.players[id] || {}; const s = today[id];
    return { nick: p.nick || 'Player', you: false, id, total: s ? s.total : null, pts: s ? s.pts : null, streak: streakOf(id, day) };
  }).sort((a, b) => (b.total ?? -1) - (a.total ?? -1));
  return { code, name: c.name, day, played: members.filter(m => m.total !== null).length, size: members.length, members };
}
function streakOf(id, day){ let n = 0; for (let d = day; d > 0 && db.scores[d] && db.scores[d][id]; d--) n++; if (!n) for (let d = day - 1; d > 0 && db.scores[d] && db.scores[d][id]; d--) n++; return n; }
function publicView(v, me){ if (!v) return v; return Object.assign({}, v, { members: v.members.map(m => ({ nick: m.nick, you: m.id === me, total: m.total, pts: m.pts, streak: m.streak })) }); }
function touchPlayer(id, nick){ const p = db.players[id] || (db.players[id] = { nick: 'Player', crews: [], at: Date.now() }); if (nick) p.nick = cleanText(nick, NICK_MAX) || p.nick; return p; }

// ---------- http ----------
function send(res, status, body, origin){
  const h = { 'Content-Type': 'application/json', 'Cache-Control': 'no-store' };
  if (origin) { h['Access-Control-Allow-Origin'] = origin; h['Vary'] = 'Origin'; }
  res.writeHead(status, h); res.end(JSON.stringify(body));
}
function readBody(req){ return new Promise((resolve, reject) => { let d = ''; req.on('data', c => { d += c; if (d.length > 16384) { reject(new Error('too big')); req.destroy(); } }); req.on('end', () => { try { resolve(d ? JSON.parse(d) : {}); } catch (e) { reject(e); } }); }); }

const server = http.createServer(async (req, res) => {
  const reqOrigin = req.headers.origin || '';
  const origin = ALLOWED_ORIGINS.includes(reqOrigin) || /^http:\/\/localhost(:\d+)?$/.test(reqOrigin) ? reqOrigin : '';
  if (req.method === 'OPTIONS') { res.writeHead(204, { 'Access-Control-Allow-Origin': origin || 'null', 'Access-Control-Allow-Methods': 'GET,POST', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Max-Age': '86400', 'Vary': 'Origin' }); return res.end(); }
  const url = new URL(req.url, 'http://x');
  if (url.pathname === '/health') return send(res, 200, { ok: true, day: torontoDay() }, origin);
  const ip = (req.headers['x-forwarded-for'] || req.socket.remoteAddress || '').split(',')[0].trim();
  if (limited(ip)) return send(res, 429, { error: 'slow down' }, origin);
  try {
    const day = torontoDay();
    // POST /api/score  { playerId, nick, day, total, pts[5] }  -> saves today's score (first one counts)
    if (req.method === 'POST' && url.pathname === '/api/score') {
      const b = await readBody(req);
      if (!validId(b.playerId)) return send(res, 400, { error: 'bad player' }, origin);
      if (Number(b.day) !== day) return send(res, 409, { error: 'wrong day', day }, origin);
      const pts = Array.isArray(b.pts) ? b.pts.map(Number) : [];
      if (pts.length !== 5 || pts.some(p => !Number.isFinite(p) || p < 0 || p > 1000)) return send(res, 400, { error: 'bad score' }, origin);
      const total = pts.reduce((a, c) => a + Math.round(c), 0);
      if (total > MAX_SCORE || Math.abs(total - Number(b.total)) > 5) return send(res, 400, { error: 'bad score' }, origin);
      touchPlayer(b.playerId, b.nick);
      const today = db.scores[day] || (db.scores[day] = {});
      if (!today[b.playerId]) { today[b.playerId] = { total, pts: pts.map(Math.round), at: Date.now() }; dirty = true; }
      return send(res, 200, { ok: true, day, total: today[b.playerId].total }, origin);
    }
    // POST /api/crews  { playerId, nick, name }  -> makes a crew and joins it
    if (req.method === 'POST' && url.pathname === '/api/crews') {
      const b = await readBody(req);
      if (!validId(b.playerId)) return send(res, 400, { error: 'bad player' }, origin);
      const name = cleanText(b.name, CREW_NAME_MAX); if (!name) return send(res, 400, { error: 'name your crew' }, origin);
      const p = touchPlayer(b.playerId, b.nick);
      if (p.crews.length >= MAX_CREWS_PER_PLAYER) return send(res, 400, { error: 'too many crews' }, origin);
      const code = newCode(); db.crews[code] = { name, members: [b.playerId], by: b.playerId, at: Date.now() }; p.crews.push(code); dirty = true;
      return send(res, 200, publicView(crewView(code, day), b.playerId), origin);
    }
    // POST /api/crews/CODE/join  { playerId, nick }
    let m = url.pathname.match(/^\/api\/crews\/([A-Z0-9]{6})\/join$/);
    if (req.method === 'POST' && m) {
      const b = await readBody(req); const c = db.crews[m[1]];
      if (!c) return send(res, 404, { error: 'crew not found' }, origin);
      if (!validId(b.playerId)) return send(res, 400, { error: 'bad player' }, origin);
      const p = touchPlayer(b.playerId, b.nick);
      if (!c.members.includes(b.playerId)) {
        if (c.members.length >= MAX_CREW_MEMBERS) return send(res, 400, { error: 'crew is full' }, origin);
        if (p.crews.length >= MAX_CREWS_PER_PLAYER) return send(res, 400, { error: 'too many crews' }, origin);
        c.members.push(b.playerId); p.crews.push(m[1]); dirty = true;
      }
      return send(res, 200, publicView(crewView(m[1], day), b.playerId), origin);
    }
    // GET /api/crews/CODE?playerId=  -> the crew's board for today
    m = url.pathname.match(/^\/api\/crews\/([A-Z0-9]{6})$/);
    if (req.method === 'GET' && m) {
      const v = crewView(m[1], day); if (!v) return send(res, 404, { error: 'crew not found' }, origin);
      return send(res, 200, publicView(v, url.searchParams.get('playerId')), origin);
    }
    // GET /api/me?playerId=  -> all my crews with today's boards
    if (req.method === 'GET' && url.pathname === '/api/me') {
      const id = url.searchParams.get('playerId'); if (!validId(id)) return send(res, 400, { error: 'bad player' }, origin);
      const p = db.players[id]; if (!p) return send(res, 200, { day, nick: null, crews: [] }, origin);
      return send(res, 200, { day, nick: p.nick, crews: p.crews.map(c => publicView(crewView(c, day), id)).filter(Boolean) }, origin);
    }
    // GET /api/stats  -> simple counts for Josh
    if (req.method === 'GET' && url.pathname === '/api/stats') {
      return send(res, 200, { day, playersToday: Object.keys(db.scores[day] || {}).length, playersAllTime: Object.keys(db.players).length, crews: Object.keys(db.crews).length }, origin);
    }
    send(res, 404, { error: 'not found' }, origin);
  } catch (e) { send(res, 400, { error: 'bad request' }, origin); }
});
server.listen(PORT, () => console.log('Off Campus server on', PORT, 'day', torontoDay()));

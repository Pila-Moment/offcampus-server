// Club games: a club exec picks 5 cards, members play them, and everyone sees the club's real answers.
// Keys:  club/SLUG -> { name, type, cards[], crew, key, by, at }
//        clubp/SLUG/ID -> { nick, ans:{ cardIndex: answer }, score, at }
// Results are worked out from the members' records when asked for (no shared counters to race on).

// ---------- settings you can change ----------
const MAX_CARDS = 6;
const SHOW_MIN = 3;            // answers needed before a card's results show (so nobody's answer stands out)
const NAME_SHOW_MIN = 2;       // a typed answer only shows if at least this many people gave it
const NAMES_PER_CARD = 3;
const CLUB_NAME_MAX = 32, Q_MAX = 140, OPT_MAX = 40;
const KINDS = ['yn', 'tot', 'name', 'trivia'];

const slugOf = s => String(s || '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 30) || 'club';
export const normAnswer = s => String(s || '').toLowerCase().replace(/[^a-z0-9 ]+/g, ' ').replace(/\b(the|a|an|my|your|our)\b/g, ' ').replace(/\s+/g, ' ').trim().replace(/(\w{3,})s\b/g, '$1');

function cleanCard(c, cleanText){
  if (!c || !KINDS.includes(c.kind)) return null;
  const q = cleanText(c.q, Q_MAX); if (q.length < 4) return null;
  if (c.kind === 'tot') {
    const opts = (c.opts || []).slice(0, 2).map(o => cleanText(o, OPT_MAX)); if (opts.length !== 2 || opts.some(o => !o)) return null;
    return { kind:'tot', q, opts };
  }
  if (c.kind === 'trivia') {
    const opts = (c.opts || []).slice(0, 4).map(o => cleanText(o, OPT_MAX)).filter(Boolean); const right = Number(c.right);
    if (opts.length < 2 || !Number.isInteger(right) || right < 0 || right >= opts.length) return null;
    return { kind:'trivia', q, opts, right };
  }
  return { kind:c.kind, q };
}

// Everything about how the club answered, from each member's record
async function tally(store, slug, club){
  const keys = (await store.list({ prefix:`clubp/${slug}/` })).blobs.map(b => b.key);
  const players = (await Promise.all(keys.map(k => store.get(k, { type:'json' })))).filter(Boolean);
  const cards = club.cards.map((c, i) => {
    const ans = players.map(p => p.ans ? p.ans[i] : undefined).filter(a => a !== undefined && a !== null);
    const n = ans.length, base = { kind:c.kind, n, shown:n >= SHOW_MIN };
    if (c.kind === 'yn') { const yes = ans.filter(a => a === true).length; return { ...base, yes }; }
    if (c.kind === 'tot') { const a = ans.filter(x => x === 0).length; return { ...base, split:[a, n - a] }; }
    if (c.kind === 'trivia') { const right = ans.filter(x => x === c.right).length; return { ...base, right }; }
    const counts = {}; const label = {};
    ans.forEach(list => (Array.isArray(list) ? list : []).forEach(t => { const k = normAnswer(t); if (!k) return; counts[k] = (counts[k] || 0) + 1; label[k] = label[k] || t; }));
    const top = Object.entries(counts).filter(([, v]) => v >= NAME_SHOW_MIN).sort((a, b) => b[1] - a[1]).slice(0, 6).map(([k, v]) => ({ t:label[k], k, n:v }));
    return { ...base, top, keys:Object.keys(counts) };   // keys stay on the server (used to score typed answers)
  });
  const board = players.filter(p => typeof p.score === 'number').map(p => ({ nick:p.nick || 'Player', score:p.score, id:p.id }))
    .sort((a, b) => b.score - a.score);
  return { players:players.length, cards, board };
}

export async function clubRoutes({ req, store, now, url, p, body, json, cleanText, validId, newCode, getPlayer }){
  // POST /api/clubs  { playerId, nick, name, type, cards[] }  makes a club game (and its crew for the daily league)
  if (req.method === 'POST' && p === '/api/clubs') {
    const b = await body();
    if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const name = cleanText(b.name, CLUB_NAME_MAX); if (name.length < 2) return json(400, { error:'name your club' });
    const cards = (Array.isArray(b.cards) ? b.cards : []).slice(0, MAX_CARDS).map(c => cleanCard(c, cleanText)).filter(Boolean);
    if (cards.length < 3) return json(400, { error:'pick at least 3 questions' });
    let slug = slugOf(name), k = 1; while (await store.get('club/' + slug, { type:'json' })) slug = slugOf(name) + '-' + (++k);
    const code = await newCode(store);
    const pl = await getPlayer(store, b.playerId); const nick = cleanText(b.nick, 16); if (nick) pl.nick = nick;
    await store.setJSON('crew/' + code, { name, members:[b.playerId], by:b.playerId, at:now, club:slug });
    pl.crews = pl.crews || []; if (!pl.crews.includes(code)) pl.crews.push(code); await store.setJSON('player/' + b.playerId, pl);
    const key = Array.from(crypto.getRandomValues(new Uint8Array(9)), x => x.toString(16).padStart(2, '0')).join('');
    await store.setJSON('club/' + slug, { name, type:cleanText(b.type, 20), cards, crew:code, key, by:b.playerId, at:now });
    return json(200, { ok:true, slug, key, crew:code });
  }

  let m = p.match(/^\/api\/clubs\/([a-z0-9-]{1,40})(\/(answer|score|results))?$/); if (!m) return null;
  const slug = m[1], what = m[3] || '';
  const club = await store.get('club/' + slug, { type:'json' }); if (!club) return json(404, { error:'club not found' });

  // GET /api/clubs/SLUG?playerId=   the game, plus this player's answers so far
  if (req.method === 'GET' && !what) {
    const id = url.searchParams.get('playerId'); const me = validId(id) ? await store.get(`clubp/${slug}/${id}`, { type:'json' }) : null;
    return json(200, { slug, name:club.name, type:club.type, cards:club.cards, crew:club.crew, me:me ? { nick:me.nick, ans:me.ans || {}, score:me.score ?? null } : null });
  }
  // GET /api/clubs/SLUG/results?playerId=   how the club answered + the leaderboard
  if (req.method === 'GET' && what === 'results') {
    const t = await tally(store, slug, club), id = url.searchParams.get('playerId');
    t.cards.forEach(c => delete c.keys);
    return json(200, { name:club.name, players:t.players, cards:t.cards, board:t.board.slice(0, 20).map(r => ({ nick:r.nick, score:r.score, you:r.id === id })),
      myRank:Math.max(0, t.board.findIndex(r => r.id === id)) + (t.board.some(r => r.id === id) ? 1 : 0), ranked:t.board.length, admin:url.searchParams.get('k') === club.key });
  }
  // POST /api/clubs/SLUG/answer  { playerId, nick, card, answer }  first answer per card counts. Sends back the club's answers from BEFORE yours.
  if (req.method === 'POST' && what === 'answer') {
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const i = Number(b.card), c = club.cards[i]; if (!c) return json(400, { error:'bad card' });
    let a = b.answer;
    if (c.kind === 'yn') { if (typeof a !== 'boolean') return json(400, { error:'yes or no' }); }
    else if (c.kind === 'tot') { a = Number(a); if (a !== 0 && a !== 1) return json(400, { error:'pick one' }); }
    else if (c.kind === 'trivia') { a = Number(a); if (!Number.isInteger(a) || a < 0 || a >= c.opts.length) return json(400, { error:'pick one' }); }
    else { a = (Array.isArray(a) ? a : []).slice(0, NAMES_PER_CARD).map(t => cleanText(t, OPT_MAX)).filter(Boolean); }
    const before = (await tally(store, slug, club)).cards[i];
    if (c.kind === 'name') { before.hits = a.filter(t => before.keys.includes(normAnswer(t))).length; } delete before.keys;
    const key = `clubp/${slug}/${b.playerId}`, rec = (await store.get(key, { type:'json' })) || { id:b.playerId, ans:{}, at:now };
    const nick = cleanText(b.nick, 16); if (nick) rec.nick = nick;
    const had = rec.ans[i] !== undefined; if (!had) { rec.ans[i] = a; await store.setJSON(key, rec); }
    return json(200, { ok:true, before, already:had, kind:c.kind, right:c.kind === 'trivia' ? c.right : undefined });
  }
  // POST /api/clubs/SLUG/score  { playerId, nick, score }  first finished score counts
  if (req.method === 'POST' && what === 'score') {
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const score = Math.round(Number(b.score)); if (!Number.isFinite(score) || score < 0 || score > 1000 * MAX_CARDS) return json(400, { error:'bad score' });
    const key = `clubp/${slug}/${b.playerId}`, rec = (await store.get(key, { type:'json' })) || { id:b.playerId, ans:{}, at:now };
    const nick = cleanText(b.nick, 16); if (nick) rec.nick = nick;
    if (typeof rec.score !== 'number') { rec.score = score; rec.id = b.playerId; await store.setJSON(key, rec); }
    return json(200, { ok:true, score:rec.score });
  }
  return json(404, { error:'not found' });
}

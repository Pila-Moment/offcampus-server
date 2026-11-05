// Club games: a club exec picks 5 cards, members play them in one visit, and the exec releases the results when they're ready.
// Keys:  club/SLUG -> { name, type, cards[], crew, key, by, at, released, releasedAt, results }
//        clubp/SLUG/ID -> { id, nick, ans:{ cardIndex: answer }, guess:{ cardIndex: guess }, done, late, at }
//
// How a game runs:
//   OPEN      members answer + guess. Nobody sees any numbers yet.
//   RELEASED  the exec taps RELEASE. The answers so far are counted once and frozen (club.results).
//             Everyone is scored against those frozen numbers. People who play after that are scored straight
//             away against the same numbers, but their answers don't change the results.

// ---------- settings you can change ----------
const MAX_CARDS = 6;
const RELEASE_MIN = 5;          // members who must finish before the exec can release the results
const PTS_PER_PCT_OFF = 20;     // yes/no: every 1 point off the real % costs this many points (out of 1,000)
const BOARD_SHOW = 20;          // leaderboard rows sent to the page
const CLUB_NAME_MAX = 32, Q_MAX = 140, OPT_MAX = 40;
const KINDS = ['yn', 'pop', 'trivia'];   // yes/no + guess the %, most popular of 2-4 options, trivia

const slugOf = s => String(s || '').toLowerCase().replace(/&/g, ' and ').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 30) || 'club';
const adminKey = () => { try { return (globalThis.process && process.env && process.env.OC_ADMIN_KEY) || ''; } catch (e) { return ''; } };

function cleanCard(c, cleanText){
  if (!c || !KINDS.includes(c.kind)) return null;
  const q = cleanText(c.q, Q_MAX); if (q.length < 4) return null;
  if (c.kind === 'yn') return { kind:'yn', q };
  const opts = (Array.isArray(c.opts) ? c.opts : []).slice(0, 4).map(o => cleanText(o, OPT_MAX)).filter(Boolean);
  if (opts.length < 2 || new Set(opts.map(o => o.toLowerCase())).size !== opts.length) return null;
  if (c.kind === 'pop') return { kind:'pop', q, opts };
  const right = Number(c.right); if (!Number.isInteger(right) || right < 0 || right >= opts.length) return null;
  return { kind:'trivia', q, opts, right };
}
// What the page is allowed to see of a card (the trivia answer stays on the server)
const publicCard = c => c.kind === 'trivia' ? { kind:c.kind, q:c.q, opts:c.opts } : c;
const isLegacy = club => club.cards.some(c => !KINDS.includes(c.kind));

async function members(store, slug){
  const keys = (await store.list({ prefix:`clubp/${slug}/` })).blobs.map(b => b.key);
  return (await Promise.all(keys.map(k => store.get(k, { type:'json' })))).filter(Boolean);
}

// Count the answers once, at release. Only people who played before the release count.
function countResults(club, players){
  const counted = players.filter(p => !p.late);
  const cards = club.cards.map((c, i) => {
    const ans = counted.map(p => p.ans ? p.ans[i] : undefined).filter(a => a !== undefined && a !== null);
    const n = ans.length;
    if (c.kind === 'yn') return { n, yes:ans.filter(a => a === true).length };
    if (c.kind === 'trivia') return { n, right:ans.filter(a => a === c.right).length };
    return { n, counts:c.opts.map((_, j) => ans.filter(a => a === j).length) };
  });
  return { players:counted.filter(p => p.done).length, cards };
}
// Points for one card against the frozen results
function cardPoints(c, r, ans, guess){
  if (ans === undefined || ans === null) return 0;
  if (c.kind === 'trivia') return ans === c.right ? 1000 : 0;
  if (!r || !r.n) return 0;
  if (c.kind === 'yn') { if (typeof guess !== 'number') return 0; const pct = 100 * r.yes / r.n; return Math.max(0, Math.round(1000 - PTS_PER_PCT_OFF * Math.abs(guess - pct))); }
  const best = Math.max(...r.counts); return best > 0 && r.counts[guess] === best ? 1000 : 0;   // ties: any top option counts
}
const scoreOf = (club, p) => club.cards.reduce((a, c, i) => a + cardPoints(c, club.results.cards[i], p.ans ? p.ans[i] : undefined, p.guess ? p.guess[i] : undefined), 0);

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
    await store.setJSON('club/' + slug, { name, type:cleanText(b.type, 20), cards, crew:code, key, by:b.playerId, at:now, released:false });
    return json(200, { ok:true, slug, key, crew:code });
  }

  const m = p.match(/^\/api\/clubs\/([a-z0-9-]{1,40})(\/(answer|results|release))?$/); if (!m) return null;
  const slug = m[1], what = m[3] || '';
  const club = await store.get('club/' + slug, { type:'json' }); if (!club) return json(404, { error:'club not found' });
  const isExec = k => !!k && (k === club.key || (adminKey() && k === adminKey()));
  const meKey = id => `clubp/${slug}/${id}`;

  // GET /api/clubs/SLUG?playerId=&k=   the game, this player's answers so far, and whether results are out
  if (req.method === 'GET' && !what) {
    const id = url.searchParams.get('playerId'); const me = validId(id) ? await store.get(meKey(id), { type:'json' }) : null;
    const done = club.released ? null : (await members(store, slug)).filter(x => x.done && !x.late).length;
    return json(200, { slug, name:club.name, type:club.type, cards:club.cards.map(publicCard), crew:club.crew, legacy:isLegacy(club),
      released:!!club.released, played:club.released ? club.results.players : done, releaseMin:RELEASE_MIN, exec:isExec(url.searchParams.get('k')),
      me:me ? { nick:me.nick, ans:me.ans || {}, guess:me.guess || {}, done:!!me.done } : null });
  }

  // POST /api/clubs/SLUG/answer  { playerId, nick, card, answer, guess }  saves one card. The first answer per card counts.
  if (req.method === 'POST' && what === 'answer') {
    if (isLegacy(club)) return json(410, { error:'old club game' });
    const b = await body(); if (!validId(b.playerId)) return json(400, { error:'bad player' });
    const i = Number(b.card), c = club.cards[i]; if (!Number.isInteger(i) || !c) return json(400, { error:'bad card' });
    let a = b.answer, g = b.guess;
    if (c.kind === 'yn') { if (typeof a !== 'boolean') return json(400, { error:'yes or no' }); g = Math.round(Number(g)); if (!Number.isFinite(g) || g < 0 || g > 100) return json(400, { error:'guess 0-100' }); }
    else { a = Number(a); if (!Number.isInteger(a) || a < 0 || a >= c.opts.length) return json(400, { error:'pick one' });
      if (c.kind === 'pop') { g = Number(g); if (!Number.isInteger(g) || g < 0 || g >= c.opts.length) return json(400, { error:'guess one' }); } else g = null; }
    const rec = (await store.get(meKey(b.playerId), { type:'json' })) || { id:b.playerId, ans:{}, guess:{}, at:now, late:!!club.released };
    const nick = cleanText(b.nick, 16); if (nick) rec.nick = nick;
    const had = rec.ans[i] !== undefined;
    if (!had) { rec.ans[i] = a; if (g !== null) rec.guess[i] = g; }
    rec.done = club.cards.every((_, j) => rec.ans[j] !== undefined);
    if (!had) await store.setJSON(meKey(b.playerId), rec);
    const out = { ok:true, already:had, done:rec.done, released:!!club.released };
    if (c.kind === 'trivia') out.right = c.right;
    if (club.released) { out.result = club.results.cards[i]; out.points = cardPoints(c, club.results.cards[i], rec.ans[i], rec.guess[i]); }
    return json(200, out);
  }

  // POST /api/clubs/SLUG/release  { k }  the exec (or Josh) releases the results. Doing it twice changes nothing.
  if (req.method === 'POST' && what === 'release') {
    const b = await body(); if (!isExec(b.k)) return json(403, { error:'exec only' });
    if (club.released) return json(200, { ok:true, released:true, already:true, players:club.results.players });
    const players = await members(store, slug), results = countResults(club, players);
    if (results.players < RELEASE_MIN) return json(409, { error:'not enough players', players:results.players, need:RELEASE_MIN });
    club.released = true; club.releasedAt = now; club.results = results;
    await store.setJSON('club/' + slug, club);
    return json(200, { ok:true, released:true, players:results.players });
  }

  // GET /api/clubs/SLUG/results?playerId=&k=   before release: just how many played. After: real counts, scores, leaderboard.
  if (req.method === 'GET' && what === 'results') {
    const id = url.searchParams.get('playerId'), exec = isExec(url.searchParams.get('k'));
    const players = await members(store, slug);
    if (!club.released) return json(200, { name:club.name, released:false, played:players.filter(x => x.done && !x.late).length, releaseMin:RELEASE_MIN, exec });
    const scored = players.filter(x => x.done).map(x => ({ id:x.id, nick:x.nick || 'Player', score:scoreOf(club, x), late:!!x.late }));
    scored.sort((a, b) => b.score - a.score);
    scored.forEach(r => { r.rank = 1 + scored.filter(o => o.score > r.score).length; });   // ties share a rank
    const mine = scored.find(r => r.id === id), meRec = players.find(x => x.id === id);
    const myCards = meRec ? club.cards.map((c, i) => ({ ans:meRec.ans[i] ?? null, guess:meRec.guess ? meRec.guess[i] ?? null : null, points:cardPoints(c, club.results.cards[i], meRec.ans[i], meRec.guess ? meRec.guess[i] : undefined) })) : null;
    return json(200, { name:club.name, released:true, players:club.results.players, cards:club.results.cards, exec,
      trivia:club.cards.map(c => c.kind === 'trivia' ? c.right : null),
      board:scored.slice(0, BOARD_SHOW).map(r => ({ nick:r.nick, score:r.score, rank:r.rank, you:r.id === id })),
      me:mine ? { score:mine.score, rank:mine.rank, cards:myCards } : null, ranked:scored.length });
  }
  return json(404, { error:'not found' });
}

// For /api/stats: how club players move into the daily
export async function clubStats(store, crewOf){
  const clubs = (await store.list({ prefix:'club/' })).blobs.map(b => b.key.slice(5));
  return Promise.all(clubs.map(async slug => {
    const club = await store.get('club/' + slug, { type:'json' }); if (!club) return null;
    const ps = await members(store, slug); const ids = ps.map(x => x.id);
    const crew = club.crew ? await crewOf(club.crew) : null;
    const daily = await Promise.all(ids.map(async id => { const pl = await store.get('player/' + id, { type:'json' }); return !!(pl && pl.hist && Object.keys(pl.hist).length); }));
    return { name:club.name, slug, released:!!club.released, started:ps.length, finished:ps.filter(x => x.done).length,
      playedDaily:daily.filter(Boolean).length, joinedCrew:crew ? ids.filter(id => crew.members.includes(id)).length : 0 };
  })).then(r => r.filter(Boolean));
}

# Frozen Receipts on the phone (Nov 7). Only does anything when the server's switch is on (GET /api/rq/today answers);
# when it's off (404), the Daily is exactly as before.
# - Round 1: the answer is saved to the 14-day question ("N of 30 answers in").
# - Round 3: if today has a frozen target, it's a guess. The server scores it and only then sends the real result.
# - After the Daily: up to 3 optional OPEN QUESTIONS (unscored).
s = open('src.html').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, ('COUNT %d: ' % s.count(a)) + a[:100]
    s = s.replace(a, b)

rep('.linkbtn{', '''.fz{display:inline-block;margin-bottom:8px;padding:4px 9px;border-radius:999px;background:var(--ink);color:var(--gold);font:700 10px var(--mono);letter-spacing:.14em}
.reveal{display:flex;flex-direction:column;gap:12px;margin-top:6px}
.reveal .big{font-family:var(--display);font-size:clamp(54px,17vw,76px);line-height:.9;color:var(--gold);text-align:center;font-variant-numeric:tabular-nums}
.reveal .big small{display:block;margin-top:4px;font-family:var(--mono);font-size:12px;font-weight:700;letter-spacing:.16em;color:var(--text)}
.reveal .src{margin:0;font-size:12.5px;font-weight:600;color:var(--muted);text-align:center}
.reveal .src b{color:var(--text)}
.openq{display:flex;flex-direction:column;gap:8px;padding:12px;border-radius:16px;background:var(--night-2)}
.openq .oh{display:flex;justify-content:space-between;gap:8px;font-size:10.5px;font-weight:700;letter-spacing:.16em;color:var(--muted)}
.openq .oq{display:grid;grid-template-columns:1fr auto auto;gap:6px;align-items:center;min-height:48px}
.openq .oq p{margin:0;font-size:12.5px;font-weight:700;line-height:1.3}
.openq .oq button{min-width:52px;min-height:44px;border-radius:10px;background:var(--night);box-shadow:inset 0 0 0 2px var(--night-3);font-family:var(--display);font-size:14px}
.openq .oq.done{opacity:.55}
.openq .oq em{grid-column:2 / 4;font-style:normal;font-size:10.5px;font-weight:700;letter-spacing:.12em;color:var(--good);text-align:right}
#openbox:empty{display:none}
.linkbtn{''')

# ---------- the switch: is frozen Receipts on, and is there a target today? ----------
rep("const DAY_MAX = DAY.rounds.filter(r => SCORED(r.type)).length * 1000;   // 3,000", "let DAY_MAX = DAY.rounds.filter(r => SCORED(r.type)).length * 1000;   // 3,000 (4,000 on a day with a frozen guess round)")
rep("/* ================= HOUSE LEAGUE ================= */", r'''/* ================= FROZEN RECEIPTS (only when the server's switch is on) ================= */
let RQ = null;   // null = off. Otherwise { target:{ qid, text } | null, guessed, max }
let RQ_P = null;   // asked once, when PLAY is tapped (CREWS_API and friends are set up further down this script)
const rqReady = () => RQ_P || (RQ_P = (async () => { if (!CREWS_API || GUEST) return null;
  try { const r = await api('GET', '/api/rq/today?playerId=' + PLAYER_ID); RQ = r && r.enabled ? r : null; if (RQ && RQ.target) DAY_MAX = RQ.max; } catch (e) { RQ = null; } return RQ; })());
async function rqAnswer(qid, yes){ try { return await api('POST', '/api/rq/answer', { playerId:PLAYER_ID, qid, yes }); } catch (e) { return null; } }
function guessRound(){
  const t = RQ.target; let guess = 50;
  app.innerHTML = `<section class="screen">${hud()}
    <div class="slip"><div class="head"><span>FROZEN RECEIPT</span><span>REAL ANSWERS</span></div>
      <span class="fz">LOCKED AT 30+ OFF CAMPUS ANSWERS</span><p class="q">${esc(t.text)}</p></div>
    <div id="stage"><div class="pctwrap"><div class="lbl">GUESS: WHAT % SAID YES?</div>
      <div class="pctrow"><button class="step" id="pm" aria-label="Lower">&minus;</button><div class="pctbig" id="pv">${guess}%</div><button class="step" id="pp" aria-label="Higher">+</button></div>
      <input type="range" id="pr" min="0" max="100" step="1" value="${guess}" aria-label="Your guess, percent"></div>
      <button class="btn dock" id="lock">LOCK IT IN</button></div></section>`;
  wireSound(); SFX.slip(); vibe(12);
  let lastT = guess; const set = (v, snd) => { guess = Math.max(0, Math.min(100, v)); $('#pv').textContent = guess + '%'; $('#pr').value = guess; if (snd) SFX.tick(); };
  $('#pr').oninput = e => { const v = +e.target.value; if (Math.abs(v - lastT) >= 2) { SFX.tick(); lastT = v; } set(v, false); };
  $('#pm').onclick = () => set(guess - 1, true); $('#pp').onclick = () => set(guess + 1, true);
  const send = async () => {
    const b = $('#lock'); b.disabled = true; b.textContent = 'CHECKING THE RECEIPTS…'; vibe([20, 30, 40]);
    let res = null; try { res = await api('POST', '/api/rq/guess', { playerId:PLAYER_ID, day:DAY.no, guess }); } catch (e) {}
    if (!res) {   // never a made-up reveal: say so, and let them retry or move on
      $('#stage').innerHTML = `<div class="saved"><span class="svstate bad">COULDN'T SEND YOUR GUESS</span><p>Check your connection. The real result only shows once the server has your guess.</p><button class="retry" id="rg" type="button">TRY AGAIN</button></div>
        <button class="btn dock" id="skipg">SKIP THIS ROUND</button>`;
      $('#rg').onclick = () => { SFX.tap(); guessRound(); }; $('#skipg').onclick = () => { SFX.tap(); addScore(0, { type:'guess', skipped:true }); next(); }; return;
    }
    reveal(res);
  };
  const reveal = async res => {
    const pct = res.pct, off = Math.round(Math.abs(res.guess - pct)), v = off <= 2 ? ['DEAD ON', true] : off <= 7 ? ['SO CLOSE', true] : off <= 15 ? ['NOT BAD', false] : off <= 25 ? ['MEH', false] : ['WAY OFF', false];
    $('.slip').classList.add('rev');
    $('#stage').innerHTML = `<div class="reveal">
        <div class="meter"><div class="fill" id="fill"></div><span class="fillv" id="fv">0%</span><div class="you" id="you" style="left:${res.guess}%"><span>YOU: ${res.guess}%</span></div></div>
        <div class="big"><span id="bp">0</span>%<small>SAID YES</small></div>
        <p class="src"><b>${fmt(res.yes)} of ${fmt(res.n)}</b> Off Campus responses said YES.</p>
        <div id="after" hidden style="display:flex;flex-direction:column;gap:12px">
          <span class="verdict ${v[1] ? 'good' : ''}">${v[0]}</span>
          <div class="facts"><div><small>YOU GUESSED</small><b>${res.guess}%</b></div><div><small>OFF BY</small><b>${off}%</b></div></div>
          <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
          <div class="how">Every 1% off costs 25 points</div></div></div>
      <button class="btn dock" id="nx" style="visibility:hidden">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button>`;
    SFX.whoosh(); await wait(60); $('#fill').style.width = pct + '%';
    const fv = $('#fv'), bp = $('#bp'), t0 = performance.now();
    await new Promise(r => { (function f(now){ const p = Math.min(1, (now - t0) / 1400), e = 1 - Math.pow(1 - p, 3), x = Math.round(pct * e); fv.textContent = x + '%'; bp.textContent = x; if (Math.random() < .3 && p < 1) SFX.tick(); if (p < 1) requestAnimationFrame(f); else r(); })(t0); });
    SFX.stamp(); vibe(v[1] ? [40, 30, 80] : 30);
    $('#after').hidden = false; addScore(res.points, { type:'guess', guess:res.guess, real:pct });
    await countUp($('#rp'), res.points, 700); $('#nx').style.visibility = 'visible';
    $('#nx').onclick = () => { SFX.tap(); next(); };
  };
  $('#lock').onclick = send;
  if (RQ.guessed) reveal(RQ.guessed);   // already guessed today (reload): show your result, never a second guess
}
async function openQuestions(el){
  if (!RQ || !el) return;
  let o; try { o = await api('GET', '/api/rq/open?playerId=' + PLAYER_ID); } catch (e) { return; }
  if (!o.open.length) return;
  el.innerHTML = `<div class="openq"><div class="oh"><span>OPEN QUESTIONS · OPTIONAL, NO POINTS</span><span>${o.open.length}</span></div>
    ${o.open.map(q => `<div class="oq" data-q="${q.qid}"><p>${esc(q.text)}</p><button type="button" data-a="1">YES</button><button type="button" data-a="0">NO</button></div>`).join('')}</div>`;
  el.querySelectorAll('.oq').forEach(row => row.onclick = async e => { const b = e.target.closest('button'); if (!b || row.classList.contains('done')) return; SFX.tap();
    row.querySelectorAll('button').forEach(x => x.disabled = true); const r = await rqAnswer(row.dataset.q, b.dataset.a === '1');
    if (r && r.ok) { row.classList.add('done'); row.insertAdjacentHTML('beforeend', '<em>SAVED · NEVER SHOWN TO OTHER PLAYERS</em>'); } else { row.querySelectorAll('button').forEach(x => x.disabled = false); toast('COULDN\'T SAVE, TRY AGAIN'); } });
}

/* ================= HOUSE LEAGUE ================= */''')

# ---------- round 1: with the switch on, the answer goes to the 14-day question ----------
rep("      sendAnswer(round, yes).then(res => res && res.ok ? show('ok', res.queens && Number.isFinite(res.queens.n) ? res.queens.n : null) : show('fail'));",
    "      (RQ && r.qid ? rqAnswer(r.qid, yes).then(x => x && x.ok ? { ok:true, queens:{ n:x.frozen ? null : x.n }, rq:x } : null) : sendAnswer(round, yes))\n        .then(res => res && res.ok ? show('ok', res.queens && Number.isFinite(res.queens.n) ? res.queens.n : null, res.rq) : show('fail'));")
rep("      else if (st === 'ok') { sv.innerHTML = `<span class=\"stampin\">ANSWER LOCKED</span><p>Your answer isn't shown to other players.${count(n)}</p><p class=\"rule\">${RESULTS_RULE}</p>`; SFX.ding(); vibe(15); }",
    "      else if (st === 'ok') { sv.innerHTML = `<span class=\"stampin\">ANSWER LOCKED</span><p>Your answer isn't shown to other players.${RQ ? (n ? ` <b>${fmt(n)} of 30</b> answers in.` : '') : count(n)}</p><p class=\"rule\">${RQ ? 'At 30 answers (within 14 days) the real result is locked in and becomes a future guessing round. With fewer, no % is ever shown.' : RESULTS_RULE}</p>`; SFX.ding(); vibe(15); }")
rep("    const show = (st, n) => {", "    const show = (st, n, rq) => {")
# ---------- round 3 becomes the guess when there's a target ----------
rep("  if (r.type === 'receipts') receipts(); else if (r.type === 'survey') survey(); else pinRound();",
    "  if (r.type === 'receipts' && S.i === 2 && RQ && RQ.target) return guessRound();\n  if (r.type === 'receipts') receipts(); else if (r.type === 'survey') survey(); else pinRound();")
rep("  $('#go').onclick = () => { SFX.ok(); vibe(20); track('start'); next(); };", "  $('#go').onclick = async () => { SFX.ok(); vibe(20); track('start'); const b = $('#go'); b.disabled = true; await Promise.race([rqReady(), wait(2500)]); next(); };")
rep("const SQLAB = { receipts:'RCPT', survey:'SHOW', pin:'PIN' };", "const SQLAB = { receipts:'RCPT', survey:'SHOW', pin:'PIN', guess:'GUESS' };")
# ---------- results: the day's own max, saved with it; open questions after ----------
rep("  const rec = { total:S.total, pts:S.results.map(r => r.pts), types:S.results.map(r => r.type) };", "  const rec = { total:S.total, pts:S.results.map(r => r.pts), types:S.results.map(r => r.type), max:DAY_MAX };")
rep("  rec = honestRec(rec);   // a result saved before honest scores (out of 5,000) shows the honest way\n", "  if (rec.max) DAY_MAX = rec.max;   // that day's own max (4,000 on a frozen-guess day)\n  rec = honestRec(rec);   // a result saved before honest scores (out of 5,000) shows the honest way\n")
rep("sc >= 0 && sc <= DAY_MAX && d === DAY.no", "sc >= 0 && sc <= 5000 && d === DAY.no")
rep("${GUEST ? '' : '<div id=\"housebox\"></div><div id=\"crewsbox\"></div>'}", "${GUEST ? '' : '<div id=\"housebox\"></div><div id=\"openbox\"></div><div id=\"crewsbox\"></div>'}")
rep("houseStrip($('#housebox'), { posted:ok, rec:{ total:S.total, pts } })));", "houseStrip($('#housebox'), { posted:ok, rec:{ total:S.total, pts } })).then(() => openQuestions($('#openbox'))));")
# ---------- crews: WEEK, LEAGUE and the Monday recap show average % (each day against its own max), with days played ----------
rep("<span class=\"lw\">${m.played}D</span><b>${m.played ? fmt(m.total) : '–'}</b></li>", "<span class=\"lw\">${m.played}D</span><b>${m.played && m.pct !== null ? m.pct.toFixed(1) + '%' : '–'}</b></li>")
rep("<span class=\"lw\">PLAYED</span><b>TOTAL</b></li>${rows}</ol>`;", "<span class=\"lw\">PLAYED</span><b>AVG</b></li>${rows}</ol>`;")
rep("const list = W.members.filter(m => m.played).slice(0, 6).map((m, i) => `${i + 1}. ${m.nick} ${fmt(m.total)}`).join('\\n');", "const list = W.members.filter(m => m.played).slice(0, 6).map((m, i) => `${i + 1}. ${m.nick} ${m.pct.toFixed(1)}% (${m.played} ${m.played === 1 ? 'day' : 'days'})`).join('\\n');")
rep("<b>${m.avg === null ? '–' : fmt(m.avg)}</b></li>", "<b>${m.avg === null ? '–' : m.avg.toFixed(1) + '%'}</b></li>")
rep("THE WEEK <em>${fmt(L.winners[0].total)}</em>`;", "THE WEEK <em>${L.winners[0].pct.toFixed(1)}%</em>`;")
rep("won with ${fmt(L.winners[0].total)}${s.win", "won with a ${L.winners[0].pct.toFixed(1)}% average${s.win")
open('src.html', 'w').write(s)
print('splice16 ok')

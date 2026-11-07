# PR 1 (Nov 6): honest Receipts.
# - Receipts rounds are answer-only: YES / NO, lock it in, saved anonymously. No % guess against a made-up number, no points.
# - A day is out of 3,000 (Showdown, Showdown, Drop the Pin). Old 5,000-point results on this phone are shown the same honest way.
# - No YES/NO split (campus or crew) is ever shown while a question is open. Only how many have answered.
# - Showdown boards are labelled as our board, not a survey. No prize links for players.
s = open('src.html').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, ('COUNT %d: ' % s.count(a)) + a[:100]
    s = s.replace(a, b)

# ---------- CSS ----------
rep('.linkbtn{', '''.rnote{margin:2px 0 12px;font-size:13px;font-weight:600;line-height:1.4;color:var(--muted);text-align:center}
.saved{display:flex;flex-direction:column;align-items:center;gap:12px;margin:4px 0 14px;text-align:center}
.saved .stampin{display:inline-block;padding:7px 16px;background:var(--stamp);color:var(--paper);font-family:var(--display);font-size:clamp(20px,6.4vw,28px);letter-spacing:.03em;transform:rotate(-3deg);box-shadow:0 0 0 3px var(--night-2), 0 0 0 5px var(--stamp);animation:stampin .5s var(--ease-pop) both}
.saved p{margin:0;max-width:34ch;font-size:13.5px;font-weight:600;line-height:1.45;color:var(--text)}
.saved p b{color:var(--gold)}
.bnote{margin:0;font-size:11px;font-weight:600;letter-spacing:.04em;color:var(--muted);text-align:center}
.linkbtn{''')

# ---------- honest scoring constants ----------
rep("const UNLOCK = 2500;", """// Honest scores: Receipts rounds are answer-only until real results exist (no made-up % to score a guess against).
const SCORED = t => t !== 'receipts';
const DAY_MAX = DAY.rounds.filter(r => SCORED(r.type)).length * 1000;   // 3,000
const RESULTS_AT = 30;   // answers a question needs before its real result can go up (home page, the next day)
const honestRec = rec => { const types = rec.types || ['receipts', 'survey', 'receipts', 'survey', 'pin']; const pts = (rec.pts || []).map((p, k) => SCORED(types[k]) && p !== null && p !== undefined ? p : null);
  return { ...rec, types, pts, total:pts.reduce((a, p) => a + (p || 0), 0) }; };
try { if (!store.get('oc-honest')) { const st0 = store.get('oc-streak'); if (st0) { st0.best = 0; store.set('oc-streak', st0); } store.set('oc-honest', 1); } } catch (e) {}   // old best was out of 5,000; the server sends the honest one
const UNLOCK = 2500;""")

# ---------- receipts: answer-only ----------
a = s.index('function receipts(){'); b = s.index('/* ================= SURVEY SHOWDOWN')
s = s[:a] + r'''function receipts(){
  const r = R(); let said = null;
  app.innerHTML = `<section class="screen">${hud()}
    <div class="slip"><div class="head"><span>OFF CAMPUS RECEIPTS</span><span>${esc(DAY.school.toUpperCase())}</span></div>
      <p class="q">${esc(r.q)}</p>${r.by ? `<div class="by">SUGGESTED BY @${esc(r.by)}</div>` : ''}<div class="said" id="said" hidden></div></div>
    <div id="stage"></div></section>`;
  wireSound(); SFX.slip(); vibe(12);
  const stage = $('#stage');
  const askYN = () => {
    stage.innerHTML = `<div class="lbl" style="margin-bottom:10px">YOUR ANSWER · NOBODY SEES WHO SAID WHAT</div><div class="yn"><button class="yes" id="y">YES</button><button class="no" id="n">NO</button></div>`;
    $('#y').onclick = () => pick('YES'); $('#n').onclick = () => pick('NO');
  };
  const pick = v => {
    said = v; SFX.stamp(); vibe(25);
    const sd = $('#said'); sd.hidden = false; sd.innerHTML = `YOU SAID <b>${v}</b> <button class="lbl" id="chg" style="color:var(--blue)">CHANGE</button>`;
    $('#chg').onclick = () => { SFX.tap(); askYN(); sd.hidden = true; };
    stage.innerHTML = `<p class="rnote">No points on this one. Just be honest.</p><button class="btn dock" id="lock">LOCK IT IN</button>`;
    $('#lock').onclick = lock;
  };
  const lock = async () => {
    vibe([20, 30, 40]); const chg = $('#chg'); if (chg) chg.remove(); const slp = $('.slip'); if (slp) slp.classList.add('rev');
    const lb = $('#lock'); lb.disabled = true; lb.textContent = 'SAVING…';
    const res = await Promise.race([sendAnswer(S.i, said === 'YES'), wait(2500).then(() => null)]);
    const n = res && res.queens && Number.isFinite(res.queens.n) ? res.queens.n : null;
    addScore(null, { said });
    stage.innerHTML = `<div class="saved"><span class="stampin">ANSWER LOCKED</span>
        <p>Saved anonymously.${n === 1 ? ' You\'re the <b>first</b> to answer today.' : n !== null ? ` <b>${fmt(n)}</b> people have answered so far today.` : ''} Once ${RESULTS_AT}+ answer, the real result goes up on the home page tomorrow.</p></div>
      <button class="sendq" id="sendq" type="button">ASK ${esc((r.send || 'a friend').toUpperCase())} THE SAME QUESTION &rarr;</button>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button>`;
    SFX.ding(); vibe(15);
    $('#nx').onclick = () => { SFX.tap(); next(); };
    $('#sendq').onclick = () => sendQuestion(r);
  };
  askYN();
}

''' + s[b:]

# the old live split display: never shows a split now, only the count
a = s.index('function showReal(res){'); b = s.index('/* ================= SEND A QUESTION TO A FRIEND')
s = s[:a] + '''function showReal(res){   // only ever shows how many answered, never a YES/NO split (a moving split gives away the newest vote)
  const el = $('#real'); if (!el || !res || !res.queens) return;
  el.innerHTML = `<span>ANSWERS SO FAR TODAY: <b>${fmt(res.queens.n)}</b></span>`; el.hidden = false;
}

''' + s[b:]
rep("const text = `${r.pct}% of ${DAY.school} said YES to this:\\n\"${r.q}\"\\nWhat would you say? Play today's five:`;",
    "const text = `\"${r.q}\"\\nYes or no? It's in today's five at ${DAY.school}:`;")

# ---------- points: answer-only rounds add nothing and never count as a miss ----------
rep("function addScore(n, detail){ S.results.push({ type:R().type, pts:n, ...detail }); const from = S.total;",
    "function addScore(n, detail){ S.results.push({ type:R().type, pts:n, ...detail }); if (n === null) return; const from = S.total;")
rep("const sqColor = p => p >= 800", "const sqColor = p => p === null || p === undefined ? 'var(--muted)' : p >= 800")
rep("const sqEmoji = p => p >= 800", "const sqEmoji = p => p === null || p === undefined ? '\\u{1F9FE}' : p >= 800")
rep("<span>${SQLAB[r.type]}</span><b>${fmt(r.pts)}</b>", "<span>${SQLAB[r.type]}</span><b>${r.pts === null ? 'SAVED' : fmt(r.pts)}</b>")
rep("<span>${SQLAB[rec.types[k]]}</span><b>${fmt(p)}</b>", "<span>${SQLAB[rec.types[k]]}</span><b>${p === null ? 'SAVED' : fmt(p)}</b>")
rep("x.fillText('OUT OF 5,000', 540, 630);", "x.fillText('OUT OF ' + fmt(DAY_MAX), 540, 630);")
rep("pts.forEach((p, k) => { const cx = x0 + k * (sz + gap); x.fillStyle = p >= 800",
    "pts.forEach((p, k) => { const cx = x0 + k * (sz + gap); x.fillStyle = p === null || p === undefined ? css('--muted') : p >= 800")
rep("x.fillStyle = css('--ink'); x.font = '44px \"Bowlby One\", Impact, sans-serif'; x.fillText(SQLAB[types[k]], cx + sz / 2, 792); });",
    "x.fillStyle = css('--ink'); x.font = '44px \"Bowlby One\", Impact, sans-serif'; x.fillText(SQLAB[types[k]], cx + sz / 2, 792); });")
rep("${fmt(total)}/5,000 ${pts.map(sqEmoji).join('')}", "${fmt(total)}/${fmt(DAY_MAX)} ${pts.map(sqEmoji).join('')}")
rep('<div class="of">OUT OF 5,000</div>', '<div class="of">OUT OF ${fmt(DAY_MAX)}</div>', 2)
rep("sc >= 0 && sc <= 5000 && d === DAY.no", "sc >= 0 && sc <= DAY_MAX && d === DAY.no")
rep("if (S.total >= UNLOCK) { SFX.fanfare();", "if (S.total >= DAY_MAX * .7) { SFX.fanfare();")
rep(" if (S.total >= UNLOCK) track('unlocked'); }", " }")
rep("function doneScreen(rec){\n", "function doneScreen(rec){\n  rec = honestRec(rec);   // a result saved before honest scores (out of 5,000) shows the honest way\n")
rep("<span>BEST <b>${fmt(st.best || 0)}</b></span>", "<span>BEST <b>${st.best ? fmt(st.best) : '–'}</b></span>")

# ---------- copy ----------
rep("<b>Receipts:</b> yes or no, then guess what % said yes.", "<b>Receipts:</b> yes or no, anonymous, no points.")
rep("${k('RECEIPTS', L.best.receipts)}", "")
rep("const ak = $('#asked'); if (ak) ak.textContent = 'SURVEY SAYS…';", "const ak = $('#asked'); if (ak) ak.textContent = 'OUR BOARD SAYS… (NOT A SURVEY)';")
rep("""      <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.stamp();""", """      <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
      <p class="bnote">Board and points written by Off Campus, not a real survey.</p>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.stamp();""")
rep('<a class="btn ghost" href="prizes.html" style="text-decoration:none">SEE EVERY PRIZE</a>', '')

open('src.html', 'w').write(s)
print('splice14 ok')

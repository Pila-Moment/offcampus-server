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
.svstate{font-family:var(--display);font-size:clamp(17px,5vw,22px);letter-spacing:.03em;color:var(--muted)}
.svstate.bad{color:var(--red)}
.saved p.rule{font-size:12px;color:var(--muted)}
.retry{min-height:44px;padding:0 18px;border:0;border-radius:12px;background:var(--gold);color:var(--ink);font:700 13px var(--mono);letter-spacing:.1em}
.gband{position:fixed;top:0;left:0;right:0;z-index:60;padding:5px 8px;background:var(--stamp);color:var(--paper);font:700 10.5px var(--mono);letter-spacing:.12em;text-align:center;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none}
body.gdemo{padding-top:24px}
.bnote{margin:0;font-size:11px;font-weight:600;letter-spacing:.04em;color:var(--muted);text-align:center}
.linkbtn{''')

# ---------- honest scoring constants ----------
rep("const UNLOCK = 2500;", """// Honest scores: Receipts rounds are answer-only until real results exist (no made-up % to score a guess against).
const SCORED = t => t !== 'receipts';
const DAY_MAX = DAY.rounds.filter(r => SCORED(r.type)).length * 1000;   // 3,000
const RESULTS_AT = 30;   // answers a question needs IN ITS OWN DAY before its real result shows (home page, the next day)
const RESULTS_RULE = `A real result only shows if a question gets ${RESULTS_AT}+ answers in one day. With fewer, no % is shown.`;
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
    stage.innerHTML = `<div class="lbl" style="margin-bottom:10px">YOUR ANSWER · NEVER SHOWN TO OTHER PLAYERS</div><div class="yn"><button class="yes" id="y">YES</button><button class="no" id="n">NO</button></div>`;
    $('#y').onclick = () => pick('YES'); $('#n').onclick = () => pick('NO');
  };
  const pick = v => {
    said = v; SFX.stamp(); vibe(25);
    const sd = $('#said'); sd.hidden = false; sd.innerHTML = `YOU SAID <b>${v}</b> <button class="lbl" id="chg" style="color:var(--blue)">CHANGE</button>`;
    $('#chg').onclick = () => { SFX.tap(); askYN(); sd.hidden = true; };
    stage.innerHTML = `<p class="rnote">No points on this one. Just be honest.</p><button class="btn dock" id="lock">LOCK IT IN</button>`;
    $('#lock').onclick = lock;
  };
  const lock = () => {
    vibe([20, 30, 40]); const chg = $('#chg'); if (chg) chg.remove(); const slp = $('.slip'); if (slp) slp.classList.add('rev');
    addScore(null, { said });
    const round = S.i, yes = said === 'YES';
    stage.innerHTML = `<div class="saved" id="sv" aria-live="polite"></div>
      <button class="sendq" id="sendq" type="button">ASK ${esc((r.send || 'a friend').toUpperCase())} THE SAME QUESTION &rarr;</button>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button>`;
    $('#nx').onclick = () => { SFX.tap(); next(); };
    $('#sendq').onclick = () => sendQuestion(r);
    const count = n => n === 1 ? ' You\'re the <b>first</b> to answer today.' : n > 1 ? ` <b>${fmt(n)}</b> people have answered so far today.` : '';
    // Only after the server says it's saved do we say so. Offline or too slow: say so, keep playing, offer a retry.
    const show = (st, n) => {
      const sv = $('#sv'); if (!sv) { if (st === 'fail') toast('YOUR RECEIPTS ANSWER DIDN\'T SAVE'); return; }
      if (st === 'saving') sv.innerHTML = `<span class="svstate">SAVING YOUR ANSWER…</span><p>You can keep playing.</p>`;
      else if (st === 'ok') { sv.innerHTML = `<span class="stampin">ANSWER LOCKED</span><p>Your answer isn't shown to other players.${count(n)}</p><p class="rule">${RESULTS_RULE}</p>`; SFX.ding(); vibe(15); }
      else if (st === 'fail') { sv.innerHTML = `<span class="svstate bad">COULDN'T SAVE YOUR ANSWER</span><p>Check your connection. You can keep playing either way.</p><button class="retry" id="retry" type="button">TRY AGAIN</button>`; $('#retry').onclick = () => { SFX.tap(); save(); }; }
      else sv.innerHTML = `<span class="svstate">${GUEST ? 'BRAND DEMO · ANSWERS AREN\'T SAVED' : 'ANSWERS CAN\'T BE SAVED ON THIS PAGE'}</span>`;
    };
    const save = () => {
      if (GUEST || !CREWS_API) return show('off');
      show('saving');
      sendAnswer(round, yes).then(res => res && res.ok ? show('ok', res.queens && Number.isFinite(res.queens.n) ? res.queens.n : null) : show('fail'));
    };
    save();
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
rep("<b>Receipts:</b> yes or no, then guess what % said yes.", "<b>Receipts:</b> yes or no, private, no points.")
rep("FIRST, YOUR ANSWER · NOBODY SEES WHO SAID WHAT", "FIRST, YOUR ANSWER · NEVER SHOWN TO OTHER PLAYERS")
rep("id=\"sf\">0 OF ${ans.length} FOUND<", "id=\"sf\">0 OF ${ans.length} FOUND · OUR BOARD, NOT A SURVEY<")
rep("#sf').textContent = `${found.size} OF ${ans.length} FOUND`;", "#sf').textContent = `${found.size} OF ${ans.length} FOUND · OUR BOARD, NOT A SURVEY`;")
rep("${k('RECEIPTS', L.best.receipts)}", "")
rep("const ak = $('#asked'); if (ak) ak.textContent = 'SURVEY SAYS…';", "const ak = $('#asked'); if (ak) ak.textContent = 'OUR BOARD SAYS… (NOT A SURVEY)';")
rep("""      <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.stamp();""", """      <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
      <p class="bnote">Board and points written by Off Campus, not a real survey.</p>
      <button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.stamp();""")
rep('<a class="btn ghost" href="prizes.html" style="text-decoration:none">SEE EVERY PRIZE</a>', '')

# ---------- brand demo (?spot=): unmistakably a sample, on the 3,000 scale ----------
rep("const UNLOCK = 2500;            // score needed (out of 5,000) to unlock the prize spin", "const UNLOCK = Math.round(DAY_MAX / 2);   // score needed (out of 3,000) to unlock the prize spin (only the brand demo shows it for now)")
rep("if (GUEST) BRANDS.unshift(GUEST);", "if (GUEST) { BRANDS.unshift(GUEST); document.body.classList.add('gdemo'); document.body.insertAdjacentHTML('afterbegin', '<div class=\"gband\">BRAND DEMO · SAMPLE ONLY · NOTHING IS REAL</div>'); }")
rep('<div class="guest"><b>PREVIEW FOR ${esc(GUEST.name.toUpperCase())}</b><span>Play it like a student, or jump straight to where your spot shows up.</span><button id="skip">SKIP TO THE PRIZE SPIN &rarr;</button></div>',
    '<div class="guest"><b>BRAND DEMO FOR ${esc(GUEST.name.toUpperCase())}</b><span>A sample of how your spot could show up. Nothing here is live: no real prizes, codes or players.</span><button id="skip">SKIP TO THE SAMPLE PRIZE SPIN &rarr;</button></div>')
rep("Score ${fmt(UNLOCK)} out of 5,000 to unlock today's <em>free prize spin</em>.", "${GUEST ? `Demo: score ${fmt(UNLOCK)} out of ${fmt(DAY_MAX)} to see the <em>sample prize spin</em>.` : `Score ${fmt(UNLOCK)} out of ${fmt(DAY_MAX)} to unlock today's <em>free prize spin</em>.`}")
rep("Score ${fmt(UNLOCK)} out of 5,000 to unlock the prize spin. <em>Prizes from Kingston spots drop soon.</em>", "Score ${fmt(UNLOCK)} out of ${fmt(DAY_MAX)} to unlock the prize spin.")
rep("if (GUEST) stamp = `BEAT ${beatPct(S.total)}% OF ${DAY.school.toUpperCase()} TODAY`;", "if (GUEST) stamp = 'DEMO RUN · SAMPLE SCORE';")
rep("<b>YOU UNLOCKED A PRIZE!</b><span>You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.</span></div><button class=\"btn pulse dock go\" id=\"prize\">SPIN FOR YOUR PRIZE!</button>",
    "<b>${GUEST ? 'DEMO: PRIZE SPIN UNLOCKED' : 'YOU UNLOCKED A PRIZE!'}</b><span>${GUEST ? 'This is where a student would spin. The prizes are samples.' : `You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.`}</span></div><button class=\"btn pulse dock go\" id=\"prize\">${GUEST ? 'SEE THE SAMPLE SPIN' : 'SPIN FOR YOUR PRIZE!'}</button>")
rep('Brand preview: player numbers and "beat %" are samples.', 'Brand demo. The score, prizes and codes here are samples. Nothing is live.')
rep('<div class="kick">SPIN 1 OF 2</div>', '<div class="kick">${GUEST ? \'BRAND DEMO · \' : \'\'}SPIN 1 OF 2</div>')
rep('<div class="kick">SPIN 2 OF 2 · YOU LANDED ON</div>', '<div class="kick">${GUEST ? \'BRAND DEMO · \' : \'\'}SPIN 2 OF 2 · YOU LANDED ON</div>')
rep('Sample prizes from made-up Kingston spots. Real partners are added as they sign on.', 'Sample prizes from made-up Kingston spots. Nothing here is a real prize.')
rep("${jackpot ? 'YOU HIT THE WEEKLY JACKPOT!' : p.big ? 'BIG WIN!' : 'YOU WON!'}", "${GUEST ? 'SAMPLE: ' : ''}${jackpot ? 'YOU HIT THE WEEKLY JACKPOT!' : p.big ? 'BIG WIN!' : 'YOU WON!'}")
rep('<small>SHOW THIS AT THE COUNTER</small>', '<small>${GUEST ? \'SAMPLE CODE · NOT REDEEMABLE\' : \'SHOW THIS AT THE COUNTER\'}</small>')
rep('<div class="post"><b>DOUBLE IT:</b> post your prize on your story', '<div class="post"><b>${GUEST ? \'IDEA:\' : \'DOUBLE IT:\'}</b> post your prize on your story')
rep('<button class="btn" id="red">TAP TO REDEEM IN FRONT OF STAFF</button>', '<button class="btn" id="red">${GUEST ? \'DEMO: HOW STAFF WOULD REDEEM IT\' : \'TAP TO REDEEM IN FRONT OF STAFF\'}</button>')

rep("tag Off Campus and ${esc(jackpot ? 'Night Shift' : brand.name)}, and we double it.", "tag Off Campus and ${esc(jackpot ? 'Night Shift' : brand.name)}, and ${GUEST ? 'it could be doubled' : 'we double it'}.")
# brand demo: no suggestions (they'd POST to /api/suggest), from any button or link
rep('<button class="btn ghost" id="sugg" type="button">SUGGEST</button>', '${GUEST ? \'\' : \'<button class="btn ghost" id="sugg" type="button">SUGGEST</button>\'}')
rep("function suggestSheet(){\n", "function suggestSheet(){\n  if (GUEST) { toast('BRAND DEMO: SUGGESTIONS ARE OFF'); return; }   // the demo never writes anything to the server\n")
rep("  if (QS.has('suggest')) setTimeout(suggestSheet, 400);", "  if (QS.has('suggest') && !GUEST) setTimeout(suggestSheet, 400);")
open('src.html', 'w').write(s)
print('splice14 ok')

# Nov 5 batch: survey answer-first, crews for houses (week tab + stakes + Monday recap), suggest a question,
# tomorrow teaser, add-to-home-screen tip, where players came from (src) and question text for the home page.
s = open('src.html').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) >= 1, 'MISSING: ' + a[:100]
    s = s.replace(a, b, n)

# ---------- CSS ----------
rep('.linkbtn{', '''.sgk{display:grid;grid-template-columns:1fr 1fr;gap:8px}
.sgk button{display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-height:56px;padding:9px 12px;border-radius:12px;background:var(--night);color:var(--muted);font:400 17px var(--display);box-shadow:inset 0 0 0 2px var(--line, #2a3048)}
.sgk button small{font:700 10.5px var(--mono);letter-spacing:.08em}
.sgk button.on{background:var(--mint);color:var(--ink);box-shadow:none}
.sheet textarea{box-sizing:border-box;width:100%;min-height:84px;border:0;border-radius:12px;padding:12px 14px;background:var(--cream);color:var(--ink);font:700 16px/1.35 var(--mono);resize:none}
.sh-steps{margin:0;padding-left:20px;display:flex;flex-direction:column;gap:6px;font-size:14px;font-weight:700;color:var(--text)}
.sh-steps b{color:var(--gold)}
.stakeline{all:unset;box-sizing:border-box;width:100%;display:flex;align-items:center;gap:8px;min-height:38px;padding:6px 10px;border-radius:10px;background:var(--night);cursor:pointer}
.stakeline .sl{flex:1;min-width:0;font-size:11.5px;font-weight:700;line-height:1.3;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.stakeline .sl b{color:var(--text)}
.stakeline .sl em{font-style:normal;color:var(--gold);letter-spacing:.08em}
.stakeline i{flex:0 0 auto;font-style:normal;font:700 10.5px var(--mono);letter-spacing:.08em;color:var(--mint)}
.stakeline.empty{justify-content:center;box-shadow:inset 0 0 0 2px var(--gold)}
.stakeline.empty .sl{flex:0 1 auto;color:var(--gold);font:400 14px var(--display);letter-spacing:.02em}
.wk-send{width:100%}
.cd .tmrw{display:block;margin:0 auto 4px;max-width:34ch;font-size:11.5px;font-weight:700;letter-spacing:.02em;line-height:1.35;color:var(--text);text-transform:none;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.cd .tmrw em{font-style:normal;color:var(--gold);letter-spacing:.12em}
.linkbtn{''')

# ---------- where a player came from (?ref=), kept from their first visit ----------
rep("const CREW_INVITE_BASE = 'https://offcampusontario.ca/daily.html';",
"""const CREW_INVITE_BASE = 'https://offcampusontario.ca/daily.html';
const SRC = (() => { const r = (new URLSearchParams(location.search).get('ref') || '').toLowerCase().replace(/[^a-z0-9-]/g, '').slice(0, 24);
  if (r && !store.get('oc-src')) store.set('oc-src', r); return store.get('oc-src') || 'direct'; })();""")
rep("api('POST', '/api/score', { playerId:PLAYER_ID, nick:getNick(), day:DAY.no, total:rec.total, pts:rec.pts })",
    "api('POST', '/api/score', { playerId:PLAYER_ID, nick:getNick(), day:DAY.no, total:rec.total, pts:rec.pts, src:SRC })")
# question text goes with the answer, so the home page can show yesterday's real result
rep("return await api('POST', '/api/answer', { playerId:PLAYER_ID, day:DAY.no, round, yes });",
    "return await api('POST', '/api/answer', { playerId:PLAYER_ID, day:DAY.no, round, yes, q:(DAY.rounds[round] || {}).q });")

# ---------- intro copy ----------
rep("<b>Showdown:</b> name the top answers before 3 X's.", "<b>Showdown:</b> give your answer, then name the top answers before 3 X's.")

# ---------- receipts: credit for suggested questions ----------
rep('<p class="q">${esc(r.q)}</p><div class="said" id="said" hidden></div></div>',
    '<p class="q">${esc(r.q)}</p>${r.by ? `<div class="by">SUGGESTED BY @${esc(r.by)}</div>` : \'\'}<div class="said" id="said" hidden></div></div>')
rep('.qcard .asked{', '.slip .by{margin-top:4px;font:700 10px var(--mono);letter-spacing:.1em;color:var(--red)}\n.qcard .asked{')

# ---------- survey: your answer first, then the board ----------
rep("function survey(){\n  const r = R(); const ans = r.a.slice().sort((a, b) => b.p - a.p);",
"""function survey(){
  const r = R();
  app.innerHTML = `<section class="screen">${hud()}
    <div class="qcard"><div class="asked">SURVEY SHOWDOWN · ${esc(DAY.school.toUpperCase())}${r.by ? ` · SUGGESTED BY @${esc(r.by)}` : ''}</div><p>${esc(r.q)}</p></div>
    <div class="lbl">FIRST, YOUR ANSWER · NOBODY SEES WHO SAID WHAT</div>
    <form class="guess" id="mf" autocomplete="off"><input id="mi" maxlength="60" placeholder="Your answer" autocapitalize="characters" enterkeyhint="go"><button class="btn" type="submit">LOCK IT</button></form>
    <p class="howto">Then the board opens: name the top answers before 3 X's.</p>
    <button class="linkbtn" id="mskip" type="button" style="align-self:center">SKIP TO THE BOARD</button></section>`;
  wireSound(); SFX.slip(); vibe(12);
  const mi = $('#mi');
  mi.addEventListener('focus', () => { if (matchMedia('(pointer:coarse)').matches) document.body.classList.add('typing'); });
  mi.addEventListener('blur', () => document.body.classList.remove('typing'));
  setTimeout(() => { try { mi.focus({ preventScroll:true }); } catch (e) {} }, 350);
  const go = mine => { if (mine) { sendTexts(S.i + 5, [mine]); track('survey-own'); } mi.blur(); document.body.classList.remove('typing'); SFX.ok(); vibe(15); surveyBoard(); };
  $('#mf').onsubmit = e => { e.preventDefault(); const v = mi.value.trim(); if (!v) { toast('TYPE YOUR ANSWER, OR SKIP'); return; } go(v); };
  $('#mskip').onclick = () => go('');
}
function surveyBoard(){
  const r = R(); const ans = r.a.slice().sort((a, b) => b.p - a.p);""")
rep('<div class="qcard"><div class="asked">WE ASKED 100 ${esc(DAY.school.toUpperCase())} STUDENTS</div><p>${esc(r.q)}</p></div>',
    '<div class="qcard"><div class="asked" id="asked">SURVEY SHOWDOWN · ${esc(DAY.school.toUpperCase())}</div><p>${esc(r.q)}</p></div>')
rep("    await wait(500);\n    for (let k = 0; k < ans.length; k++) if (!found.has(k)) { flip(k, true);",
    "    const ak = $('#asked'); if (ak) ak.textContent = 'SURVEY SAYS…';\n    await wait(500);\n    for (let k = 0; k < ans.length; k++) if (!found.has(k)) { flip(k, true);")

# ---------- finish: suggest button, tomorrow teaser ----------
rep("""const tailHTML = () => `<div class="row3"><button class="btn ghost" id="see">SEE IMAGE</button><a class="btn ghost" href="party.html">PARTY</a><a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener">INSTAGRAM</a></div>
    <div class="cd">NEXT FIVE IN <b id="cd">${nextDropText()}</b></div>`;""",
"""const TOMORROW_Q = (() => { const d = DAYS[(DAY_INDEX + 1) % DAYS.length]; const r = d && d.rounds.find(x => x.type === 'receipts'); return r && DAY_INDEX + 1 < DAYS.length ? r.q : ''; })();
const tailHTML = () => `<div class="row3"><button class="btn ghost" id="see">SEE IMAGE</button><button class="btn ghost" id="sugg" type="button">SUGGEST</button><a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener">INSTAGRAM</a></div>
    <div class="cd">${TOMORROW_Q && !GUEST ? `<span class="tmrw"><em>TOMORROW</em> ${esc(TOMORROW_Q)}</span>` : ''}NEXT FIVE IN <b id="cd">${nextDropText()}</b></div>`;""")
rep("  const f = $('#follow'); if (f) f.onclick = () => { track('follow'); };",
    "  const f = $('#follow'); if (f) f.onclick = () => { track('follow'); };\n  const sg = $('#sugg'); if (sg) sg.onclick = () => { SFX.tap(); suggestSheet(); };")

# ---------- suggest a question + add-to-home-screen tip (sheets) ----------
rep("function newCrewFormHTML(first){",
"""function suggestSheet(){
  if (!CREWS_API) { toast('OPEN THIS ON OFFCAMPUSONTARIO.CA'); return; }
  let kind = 'receipts';
  const ph = { receipts:'Have you ever…?', survey:'Name something…' };
  const d = sheet(`<b class="sh-h">SUGGEST A QUESTION</b><p>The best ones go in the daily for all of ${esc(DAY.school)}, with your @ on them.</p>
    <div class="sgk"><button type="button" class="on" data-k="receipts">RECEIPTS<small>YES OR NO</small></button><button type="button" data-k="survey">SURVEY<small>NAME A…</small></button></div>
    <form id="sgf" autocomplete="off"><textarea id="sgq" maxlength="160" placeholder="${ph.receipts}" required></textarea><input id="sgc" maxlength="30" placeholder="Your @ for credit (optional)"><button class="btn" type="submit">SEND IT</button></form>
    <button class="sh-later" id="sgx" type="button">CLOSE</button>`);
  track('suggest-open');
  d.querySelectorAll('.sgk button').forEach(b => b.onclick = () => { kind = b.dataset.k; d.querySelectorAll('.sgk button').forEach(x => x.classList.toggle('on', x === b)); d.querySelector('#sgq').placeholder = ph[kind]; SFX.tap(); });
  d.querySelector('#sgx').onclick = () => d.remove();
  d.querySelector('#sgf').onsubmit = async e => {
    e.preventDefault(); const q = d.querySelector('#sgq').value.trim(); if (q.length < 8) { toast('WRITE A LITTLE MORE'); return; }
    const btn = d.querySelector('#sgf button'); btn.disabled = true; btn.textContent = 'SENDING…';
    try { await api('POST', '/api/suggest', { playerId:PLAYER_ID, kind, q, credit:d.querySelector('#sgc').value.trim() }); track('suggest'); SFX.ding(); d.remove(); toast('SENT. IF IT MAKES THE DAILY, YOU GET CREDIT'); }
    catch (err) { btn.disabled = false; btn.textContent = 'SEND IT'; toast(/plenty/.test(err.message) ? 'THAT\\'S 5 TODAY, SEND MORE TOMORROW' : 'COULDN\\'T SEND, TRY AGAIN'); }
  };
}
// Put it on the home screen: shown once, on the second day someone plays, on phones in a normal browser
function homeTipSheet(st){
  const standalone = (window.matchMedia && matchMedia('(display-mode: standalone)').matches) || navigator.standalone;
  if (GUEST || standalone || IN_INSTAGRAM || store.get('oc-hometip') || (st.days || 0) < 2 || !(window.matchMedia && matchMedia('(pointer:coarse)').matches)) return false;
  const ios = /iPhone|iPad|iPod/i.test(navigator.userAgent);
  store.set('oc-hometip', DAY.no); track('hometip');
  const d = sheet(`<b class="sh-h">PUT IT ON YOUR HOME SCREEN</b><p>One tap to play every morning, like an app. No download.</p>
    <ol class="sh-steps">${ios ? '<li>Tap <b>Share</b> at the bottom of Safari (the square with the arrow)</li><li>Scroll down, tap <b>Add to Home Screen</b></li>' : '<li>Tap <b>⋮</b> at the top of your browser</li><li>Tap <b>Add to Home screen</b></li>'}</ol>
    <button class="btn" id="htok" type="button">GOT IT</button>`);
  d.querySelector('#htok').onclick = () => d.remove();
  return true;
}
function newCrewFormHTML(first){""")
rep("  if (!GUEST && store.get('oc-savelater') !== DAY.no) setTimeout(saveSheet, 2600);",
    "  if (!GUEST) setTimeout(() => { if (!homeTipSheet(st) && store.get('oc-savelater') !== DAY.no) saveSheet(); }, 2600);")

# ---------- crews: built for houses ----------
rep("""${first ? `<b class="cf-h">START A CREW</b><p>Your own daily league. Everyone plays on their own phone: see who won today, who has the streak, and who's best at each game.</p>` : `<b class="cf-h">START ANOTHER CREW</b>`}""",
    """${first ? `<b class="cf-h">START A CREW FOR YOUR HOUSE</b><p>Name it after your house or floor. Everyone plays on their own phone. Set a weekly stake: winner gets, loser has to.</p>` : `<b class="cf-h">START ANOTHER CREW</b>`}""")
rep('placeholder="Crew name, e.g. The Princess St House"', 'placeholder="Crew name, e.g. 517 or Vic Hall 3rd"')
rep("""return `<button class="crewcta" id="crewcta" type="button"><b>PLAY WITH FRIENDS</b><span>Your house vs your floor. Daily wins, streaks, who's best at what.</span><i>START A CREW</i></button>`;""",
    """return `<button class="crewcta" id="crewcta" type="button"><b>START A CREW FOR YOUR HOUSE</b><span>Who wins the week? Loser cleans the kitchen.</span><i>START</i></button>`;""")
# TODAY / WEEK / LEAGUE tabs
rep("""const tab = store.get('oc-crewtab') === 'league' ? 'league' : 'today';""",
    """const tab = ['week', 'league'].includes(store.get('oc-crewtab')) ? store.get('oc-crewtab') : 'today';""")
rep("""<button type="button" class="ct ${tab === 'today' ? 'on' : ''}" data-v="today">TODAY</button><button type="button" class="ct ${tab === 'league' ? 'on' : ''}" data-v="league">LEAGUE</button>""",
    """<button type="button" class="ct ${tab === 'today' ? 'on' : ''}" data-v="today">TODAY</button><button type="button" class="ct ${tab === 'week' ? 'on' : ''}" data-v="week">WEEK</button><button type="button" class="ct ${tab === 'league' ? 'on' : ''}" data-v="league">LEAGUE</button>""")
rep("const leagueCache = {};",
"""function weekHTML(W){
  const rows = W.members.slice(0, CREW_ROWS).map((m, i) => `<li class="${m.you ? 'me' : ''} ${m.played ? '' : 'wait'}"><span class="rk">${m.played ? i + 1 : '–'}</span><span class="nk">${esc(m.nick)}${m.you ? ' <em>YOU</em>' : ''}</span><span class="lw">${m.played}D</span><b>${m.played ? fmt(m.total) : '–'}</b></li>`).join('');
  const stake = W.stake ? `<button class="stakeline" type="button" data-act="edit"><span class="sl"><em>STAKE</em> Winner: <b>${esc(W.stake.win || '–')}</b> · Loser: <b>${esc(W.stake.lose || '–')}</b></span><i>EDIT</i></button>`
    : `<button class="stakeline empty" type="button" data-act="edit"><span class="sl">+ SET THIS WEEK'S STAKE</span></button>`;
  const left = W.daysLeft === 0 ? 'LAST DAY' : `${W.daysLeft} ${W.daysLeft === 1 ? 'DAY' : 'DAYS'} LEFT`;
  return `${stake}<ol class="lg"><li class="lh"><span class="rk"></span><span class="nk">THIS WEEK · ${left}</span><span class="lw">PLAYED</span><b>TOTAL</b></li>${rows}</ol>`;
}
function weekMsg(W){
  const list = W.members.filter(m => m.played).slice(0, 6).map((m, i) => `${i + 1}. ${m.nick} ${fmt(m.total)}`).join('\\n');
  const st = W.stake ? `${W.stake.win ? '\\nWinner: ' + W.stake.win : ''}${W.stake.lose ? '\\nLoser: ' + W.stake.lose : ''}` : '';
  return `${W.name} this week so far:\\n${list || 'Nobody yet.'}${st}\\nPlay today's five:`;
}
function stakeSheet(code, W, done){
  const d = sheet(`<b class="sh-h">THIS WEEK'S STAKE</b><p>Highest total by Sunday wins. Lowest total pays up. It shows on the board all week.</p>
    <form id="skf" autocomplete="off"><input name="win" maxlength="40" placeholder="Winner gets… (picks the movie)" value="${esc(W.stake ? W.stake.win : '')}"><input name="lose" maxlength="40" placeholder="Loser has to… (clean the kitchen)" value="${esc(W.stake ? W.stake.lose : '')}"><button class="btn" type="submit">SAVE THE STAKE</button></form>
    <button class="sh-later" id="skx" type="button">CANCEL</button>`);
  d.querySelector('#skx').onclick = () => d.remove();
  const f = d.querySelector('#skf');
  f.onsubmit = async e => { e.preventDefault(); const win = f.win.value.trim(), lose = f.lose.value.trim(); if (!win && !lose) { toast('ADD A STAKE'); return; }
    const b = f.querySelector('.btn'); b.disabled = true; b.textContent = 'SAVING…';
    try { const nw = await api('POST', `/api/crews/${code}/stake`, { playerId:PLAYER_ID, win, lose }); track('crew-stake'); SFX.ding(); done(nw);
      d.querySelector('.sheet').innerHTML = `<b class="sh-h">STAKE IS SET</b><p>${win ? `Winner: <b style="color:var(--text)">${esc(win)}</b>. ` : ''}${lose ? `Loser: <b style="color:var(--text)">${esc(lose)}</b>. ` : ''}Now tell the crew.</p>
        <button class="btn" id="sktell" type="button">TELL ${esc(W.name.toUpperCase())}</button><button class="sh-later" id="skok" type="button">DONE</button>`;
      d.querySelector('#skok').onclick = () => d.remove();
      d.querySelector('#sktell').onclick = () => { track('crew-stake-send'); shareText(`${W.name} this week. ${win ? `Winner: ${win}. ` : ''}${lose ? `Loser: ${lose}. ` : ''}Game on:`, `${CREW_INVITE_BASE}?crew=${code}&ref=crew`); };
    } catch (err) { b.disabled = false; b.textContent = 'SAVE THE STAKE'; toast('COULDN\\'T SAVE, TRY AGAIN'); } };
}
const weekCache = {};
const leagueCache = {};""")
rep("""      if (v === 'today') { body.innerHTML = todayHTML; return; }""",
"""      const inv = box.querySelector('.inv'), old = box.querySelector('.wk-send'); if (old) old.remove(); if (inv) inv.style.display = v === 'week' ? 'none' : '';
      if (v === 'today') { body.innerHTML = todayHTML; return; }
      if (v === 'week') {
        if (!weekCache[code]) { body.innerHTML = '<p class="cmeta">LOADING THE WEEK…</p>'; try { weekCache[code] = await api('GET', `/api/crews/${code}/week?playerId=${PLAYER_ID}`); } catch (e) { body.innerHTML = todayHTML; if (inv) inv.style.display = ''; toast('COULDN\\'T LOAD THE WEEK'); return; } }
        const W = weekCache[code]; body.innerHTML = weekHTML(W); track('crew-week');
        const ws = document.createElement('button'); ws.className = 'btn ghost wk-send'; ws.type = 'button'; ws.textContent = `SEND THE WEEK TO ${W.name.toUpperCase()}`;
        ws.onclick = () => { SFX.tap(); track('crew-week-send'); shareText(weekMsg(weekCache[code]), `${CREW_INVITE_BASE}?crew=${code}&ref=crew`); };
        box.appendChild(ws);
        body.querySelector('[data-act=edit]').onclick = () => { SFX.tap(); stakeSheet(code, W, nw => { weekCache[code] = nw; show('week'); }); };
        return;
      }""")
rep("""    if (store.get('oc-crewtab') === 'league') show('league');""",
    """    if (['week', 'league'].includes(store.get('oc-crewtab'))) show(store.get('oc-crewtab'));""")

# ---------- Monday recap: last week's winner and loser ----------
rep("""function recapHTML(c){
  const y = c.yesterday, top = c.members.find(m => m.total !== null);""",
"""function lastWeekHTML(c){
  const L = c.lastWeek, names = list => list.map(m => m.you ? 'YOU' : esc(m.nick.toUpperCase())).join(' + ');
  const won = L.winners.some(m => m.you), lost = L.losers.some(m => m.you), s = L.stake || {};
  const head = `${names(L.winners)} ${won && L.winners.length === 1 ? 'WON' : 'TOOK'} THE WEEK <em>${fmt(L.winners[0].total)}</em>`;
  const line = `${lost ? 'You came last' : `${L.losers.map(m => esc(m.nick)).join(' + ')} came last`}${s.lose ? ` · Loser: ${esc(s.lose)}` : ''}${s.win ? ` · Winner: ${esc(s.win)}` : ''}`;
  const msg = `${c.name} last week: ${L.winners.map(m => m.you ? 'I' : m.nick).join(' + ')} won with ${fmt(L.winners[0].total)}${s.win ? ` (winner: ${s.win})` : ''}. ${L.losers.map(m => m.you ? 'I' : m.nick).join(' + ')} came last${s.lose ? ` (loser: ${s.lose})` : ''}. New week starts now:`;
  return `<div class="recap"><div class="rh"><b>${esc(c.name.toUpperCase())}</b><span>LAST WEEK</span><button class="rsend" type="button" data-code="${c.code}" data-msg="${esc(msg)}">SEND TO CHAT</button></div>
    <p class="rw">${head}</p><p class="rl">${line}</p></div>`;
}
function recapHTML(c){
  if (c.lastWeek) return lastWeekHTML(c);
  const y = c.yesterday, top = c.members.find(m => m.total !== null);""")

# ---------- ?suggest opens the sheet (from the home page) ----------
rep("  const sk = $('#skip'); if (sk) sk.onclick = () => { SFX.ok(); vibe(20); prize(); };\n}",
    "  const sk = $('#skip'); if (sk) sk.onclick = () => { SFX.ok(); vibe(20); prize(); };\n  if (QS.has('suggest') && !GUEST) setTimeout(suggestSheet, 400);\n}")
rep("  joinCard($('#joinbox'));\n  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total));\n}",
    "  joinCard($('#joinbox'));\n  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total));\n  if (QS.has('suggest')) setTimeout(suggestSheet, 400);\n}")


# ---------- no prize bar during rounds while prizes aren't live ----------
rep("""    <div class="unlock ${S.total >= UNLOCK ? 'done' : ''}" id="ul">""", """    ${PRIZES_LIVE || GUEST ? '' : '<!--'}<div class="unlock ${S.total >= UNLOCK ? 'done' : ''}" id="ul">""")
rep("""<span>${unlockText(S.total)}</span></div>`;
}""", """<span>${unlockText(S.total)}</span></div>${PRIZES_LIVE || GUEST ? '' : '-->'}`;
}""")
# the finish screen has room now that the prize box is gone: keep the buttons and the teaser on small phones
rep("@media (max-height:700px){.cd{display:none}}", "@media (max-height:600px){.cd{display:none}}\n@media (max-height:760px){#crewsbox:has(.crew) ~ .row3,#crewsbox:has(.crew) ~ .cd{display:none}}\n@media (max-height:900px){#crewsbox:has(.crew) ~ .cd .tmrw{display:none}}\n@media (max-height:700px){.crew .lg .lh{display:none}.stakeline{min-height:30px;padding:3px 10px}.crew .lg{gap:3px}.crew .btn.inv,.crew .wk-send{min-height:44px}}")
rep("@media (max-height:700px){.row3{display:none}}", "@media (max-height:600px){.row3{display:none}}")

# ---------- intro: suggest a question link (every player sees the intro) ----------
rep("""${CREWS_API && !GUEST && !store.get('oc-saved') ? ' <button class="linkbtn" id="login" type="button">PLAYED BEFORE? LOG IN</button>' : ''}</p>""",
    """${CREWS_API && !GUEST && !store.get('oc-saved') ? ' <button class="linkbtn" id="login" type="button">PLAYED BEFORE? LOG IN</button>' : ''}${CREWS_API && !GUEST ? ' <button class="linkbtn" id="isugg" type="button">SUGGEST A QUESTION</button>' : ''}</p>""")
rep("""  const lg = $('#login'); if (lg) lg.onclick = () => { SFX.tap(); loginSheet(); };""",
    """  const lg = $('#login'); if (lg) lg.onclick = () => { SFX.tap(); loginSheet(); };
  const isg = $('#isugg'); if (isg) isg.onclick = () => { SFX.tap(); suggestSheet(); };""")
rep('function newCrewFormHTML(first){', 'window.OC = { suggestSheet:() => suggestSheet(), homeTipSheet:st => homeTipSheet(st) };   // handles for the test scripts\nfunction newCrewFormHTML(first){')

open('src.html', 'w').write(s)
print('splice13 ok')

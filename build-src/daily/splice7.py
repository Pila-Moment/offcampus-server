# Growth pass (Nov 4): challenge-your-friends as the main button, send-this-to-a-friend on every Receipts reveal,
# crew LEAGUE tab (wins, average, who's best at each game), and your crews on the start screen.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)

# ---- 1. Receipts reveal: send it to the friend it's about
rep('''        <div class="how">Every 1% off costs 25 points</div>
        <button class="btn dock" id="nx">''','''        <div class="how">Every 1% off costs 25 points</div>
        <button class="sendq" id="sendq" type="button"><span>${r.pct}% SAID YES.</span> SEND THIS TO ${esc((r.send || 'a friend').toUpperCase())} &rarr;</button>
        <button class="btn dock" id="nx">''')
rep("    vibe([20, 30, 40]); const chg = $('#chg'); if (chg) chg.remove();", "    vibe([20, 30, 40]); const chg = $('#chg'); if (chg) chg.remove(); const slp = $('.slip'); if (slp) slp.classList.add('rev');")
rep("    $('#nx').onclick = () => { SFX.tap(); next(); };\n  };\n", """    $('#nx').onclick = () => { SFX.tap(); next(); };
    $('#sendq').onclick = () => sendQuestion(r);
  };
""")
rep("/* ================= RECEIPTS ================= */", """/* ================= SEND A QUESTION TO A FRIEND ================= */
async function sendQuestion(r){
  SFX.tap(); vibe(15); track('send-q');
  const text = `${r.pct}% of ${DAY.school} said YES to this:\\n"${r.q}"\\nWhat would you say? Play today's five:`;
  const url = `https://${SHARE_URL}/?ref=q`;
  try { if (navigator.share) { await navigator.share({ text, url }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
  try { await navigator.clipboard.writeText(text + ' ' + url); toast('COPIED, SEND IT'); } catch (e) { toast('COULDN\\'T COPY'); }
}

/* ================= RECEIPTS ================= */""")

# ---- 2. Results + done screen: CHALLENGE YOUR FRIENDS is the big button
rep('''const tailHTML = () => `<div class="row3"><button class="btn ghost" id="share">SHARE</button><button class="btn ghost" id="see">IMAGE</button><a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener">INSTAGRAM</a></div>''',
    '''const tailHTML = () => `<div class="row3"><button class="btn ghost" id="see">SEE IMAGE</button><a class="btn ghost" href="party.html">PARTY</a><a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener">INSTAGRAM</a></div>''')
rep("  $('#share').onclick = async () => { SFX.tap(); track('share');", "  const shb = $('#share'); if (shb) shb.onclick = async () => { SFX.tap(); track('share');")
rep('''              : `<div class="gate ok"><b>YOU'D HAVE UNLOCKED A PRIZE!</b><span>You beat ${fmt(UNLOCK)}. The prize wheel drops soon.</span></div><button class="btn pulse dock go" id="prize">SEE WHAT'S COMING</button>`)
      : `<div class="gate"><b>${fmt(UNLOCK - S.total)} POINTS SHORT</b><span>${live ? `You needed ${fmt(UNLOCK)} to unlock the prize spin.` : `When prizes drop, ${fmt(UNLOCK)} unlocks the spin.`} New five at 4am.</span></div><a class="btn mint dock" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a>`}''',
'''              : `<button class="gate ok" id="prize" type="button"><b>YOU'D HAVE UNLOCKED A PRIZE!</b><span>You beat ${fmt(UNLOCK)}. The prize wheel drops soon.</span><i class="gate-go">SEE WHAT'S COMING &rarr;</i></button>`)
      : `<div class="gate"><b>${fmt(UNLOCK - S.total)} POINTS SHORT</b><span>${live ? `You needed ${fmt(UNLOCK)} to unlock the prize spin.` : `When prizes drop, ${fmt(UNLOCK)} unlocks the spin.`} New five at 4am.</span></div>`}
    ${GUEST || live ? '' : '<button class="btn pulse dock go" id="share">CHALLENGE YOUR FRIENDS</button>'}''')
rep('''    ${tailHTML()}
    <a class="btn mint dock" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a>''','''    ${tailHTML()}
    <button class="btn pulse dock go" id="share">CHALLENGE YOUR FRIENDS</button>''')
rep("const text = `Off Campus · ${DAY.school} Daily #${pad3(DAY.no)}\\n${fmt(total)}/5,000 ${pts.map(sqEmoji).join('')}\\nCan you beat me? https://${SHARE_URL}/?ref=share`;",
    "const text = `Off Campus · ${DAY.school} Daily #${pad3(DAY.no)}\\n${fmt(total)}/5,000 ${pts.map(sqEmoji).join('')}\\nBet you can't beat me. Same five for everyone at ${DAY.school} today: https://${SHARE_URL}/?ref=share`;")

# ---- 3. Crew board: TODAY / LEAGUE tabs
rep('''  return `<div class="crew" data-code="${c.code}"><div class="ch"><b>${esc(c.name)}</b><span>${c.played} / ${c.size} PLAYED TODAY</span></div>
    <ol>${rows}</ol>${hidden > 0 ? `<p class="cnote">+ ${hidden} more in the crew</p>` : ''}
    ${c.size < 2 ? `<p class="cnote">Just you so far. Send the invite to your house, floor or friends.</p>` : waiting ? `<p class="cnote">${waiting} ${waiting === 1 ? "hasn't" : "haven't"} played yet. Give them a nudge.</p>` : ''}''',
'''  const tab = store.get('oc-crewtab') === 'league' ? 'league' : 'today';
  return `<div class="crew" data-code="${c.code}"><div class="ch"><b>${esc(c.name)}</b><div class="ctabs"><button type="button" class="ct ${tab === 'today' ? 'on' : ''}" data-v="today">TODAY</button><button type="button" class="ct ${tab === 'league' ? 'on' : ''}" data-v="league">LEAGUE</button></div></div>
    <div class="cbody" data-today="1"><ol>${rows}</ol>
    <p class="cmeta">${c.size < 2 ? 'JUST YOU SO FAR · INVITE YOUR HOUSE OR FLOOR' : `${c.played} OF ${c.size} PLAYED TODAY${waiting ? ` · ${waiting} TO GO` : ' · EVERYONE IN'}`}${hidden > 0 ? ` · +${hidden} MORE` : ''}</p></div>''')
rep("function newCrewFormHTML(first){", r'''function leagueHTML(L){
  const rows = L.members.slice(0, CREW_ROWS).map((m, i) => `<li class="${m.you ? 'me' : ''} ${m.played ? '' : 'wait'}"><span class="rk">${i + 1}</span><span class="nk">${esc(m.nick)}${m.you ? ' <em>YOU</em>' : ''}${m.streak >= 2 ? ` <i>${m.streak}-day streak</i>` : ''}</span><span class="lw">${m.wins}W</span><b>${m.avg === null ? '–' : fmt(m.avg)}</b></li>`).join('');
  const k = (lab, x) => `<span><small>BEST AT ${lab}</small><b>${x ? (x.you ? 'YOU' : esc(x.nick)) : '–'}</b></span>`;
  return `<ol class="lg"><li class="lh"><span class="rk"></span><span class="nk">LAST ${L.days} DAYS</span><span class="lw">WINS</span><b>AVG</b></li>${rows}</ol>
    <div class="kings">${k('RECEIPTS', L.best.receipts)}${k('SHOWDOWN', L.best.showdown)}${k('PIN', L.best.pin)}</div>`;
}
const leagueCache = {};
function wireCrewTabs(el, crews){
  el.querySelectorAll('.crew').forEach(box => {
    const code = box.dataset.code, body = box.querySelector('.cbody'), todayHTML = body.innerHTML;
    const show = async v => {
      box.querySelectorAll('.ct').forEach(t => t.classList.toggle('on', t.dataset.v === v)); store.set('oc-crewtab', v);
      if (v === 'today') { body.innerHTML = todayHTML; return; }
      if (!leagueCache[code]) { body.innerHTML = '<p class="cmeta">LOADING THE LEAGUE…</p>'; try { leagueCache[code] = await api('GET', `/api/crews/${code}/league?playerId=${PLAYER_ID}`); } catch (e) { body.innerHTML = todayHTML; toast('COULDN\'T LOAD THE LEAGUE'); return; } }
      body.innerHTML = leagueHTML(leagueCache[code]); track('crew-league');
    };
    box.querySelectorAll('.ct').forEach(t => t.onclick = () => { SFX.tap(); vibe(10); show(t.dataset.v); });
    if (store.get('oc-crewtab') === 'league') show('league');
  });
}
async function crewStrip(el){
  if (!CREWS_API || !el || INVITE_CODE) return;
  let me; try { me = await api('GET', '/api/me?playerId=' + PLAYER_ID); } catch (e) { return; }
  const crews = (me.crews || []).slice(0, 2); if (!crews.length) return;
  el.innerHTML = crews.map(c => { const top = c.members.find(m => m.total !== null);
    return `<div class="cstrip"><b>${esc(c.name.toUpperCase())}</b><span>${c.played} of ${c.size} played${top ? ` · ${top.you ? 'You lead' : esc(top.nick) + ' leads'} with ${fmt(top.total)}` : ' · nobody yet, go first'}</span></div>`; }).join('');
}
function newCrewFormHTML(first){''')
rep("  el.querySelectorAll('.inv').forEach(b => b.onclick = () => invite(b.dataset.code, b.dataset.name, myScore));",
    "  el.querySelectorAll('.inv').forEach(b => b.onclick = () => invite(b.dataset.code, b.dataset.name, myScore));\n  wireCrewTabs(el, crews);")
rep('''<b>PLAY WITH FRIENDS</b><span>Start a crew for your house or floor. See who wins today.</span><i>START A CREW</i>''',
    '''<b>PLAY WITH FRIENDS</b><span>Your house vs your floor. Daily wins, streaks, who's best at what.</span><i>START A CREW</i>''')
rep('''`<b class="cf-h">PLAY WITH YOUR FRIENDS</b><p>Start a crew for your house, floor or friends. Everyone plays on their own phone, and you see who won today.</p>`''',
    '''`<b class="cf-h">START A CREW</b><p>Your own daily league. Everyone plays on their own phone: see who won today, who has the streak, and who's best at each game.</p>`''')

# ---- 4. Start screen: your crews at a glance
rep('''    <div id="joinbox"></div>
    <div class="five" aria-label="Today's rounds">''', '''    <div id="joinbox"></div><div id="crewstrip"></div>
    <div class="five" aria-label="Today's rounds">''')
rep("  if (!GUEST) joinCard($('#joinbox'));\n  const sk = $('#skip');", "  if (!GUEST) { joinCard($('#joinbox')); crewStrip($('#crewstrip')); }\n  const sk = $('#skip');")

rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* growth pass */
.sendq{all:unset;box-sizing:border-box;width:100%;min-height:50px;padding:10px 14px;border-radius:14px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--gold);color:var(--gold);font:700 12.5px var(--mono);letter-spacing:.06em;line-height:1.3;text-align:center;cursor:pointer;-webkit-tap-highlight-color:transparent}
.sendq span{color:var(--text)}
.sendq:active{transform:scale(.98)}
button.gate{width:100%;border:0;font:inherit;color:inherit;cursor:pointer;-webkit-tap-highlight-color:transparent}
.gate-go{font-style:normal;font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--good);margin-top:2px}
.crew .ch{align-items:center}
.ctabs{flex:0 0 auto;display:flex;gap:4px;padding:3px;border-radius:10px;background:var(--night)}
.ct{min-height:34px;padding:0 10px;border-radius:8px;font:700 10.5px var(--mono);letter-spacing:.1em;color:var(--muted);background:transparent}
.ct.on{background:var(--mint);color:var(--ink)}
.cbody{display:flex;flex-direction:column;gap:7px}
.cmeta{margin:0;font-size:10.5px;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.crew .lw{flex:0 0 38px;text-align:right;font-family:var(--display);font-size:14px;color:var(--mint)}
.crew .lg .lh{background:transparent;padding-top:0;padding-bottom:0}
.crew .lg .lh .nk,.crew .lg .lh .lw,.crew .lg .lh b{font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.kings{display:grid;grid-template-columns:repeat(3,1fr);gap:6px}
.kings span{display:flex;flex-direction:column;gap:2px;padding:6px 8px;border-radius:9px;background:var(--night);min-width:0}
.kings small{font-size:8.5px;font-weight:700;letter-spacing:.1em;color:var(--gold);white-space:nowrap}
.kings b{font-family:var(--display);font-weight:400;font-size:14px;color:var(--text);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.cstrip{display:flex;flex-direction:column;gap:2px;padding:9px 12px;border-radius:12px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--mint)}
.cstrip b{font-family:var(--display);font-weight:400;font-size:15px;color:var(--mint)}
.cstrip span{font-size:11.5px;font-weight:700;color:var(--text)}
#crewstrip{display:flex;flex-direction:column;gap:6px}
#crewstrip:empty{display:none}
.slip.rev{padding:12px 14px 14px}.slip.rev .head{margin-bottom:6px;padding-bottom:5px}.slip.rev .q{font-size:clamp(21px,6vw,28px)}
@media (max-height:700px){.row3{display:none}}
@media (max-height:760px){#crewsbox:has(.ct[data-v=league].on) ~ .gate{display:none}}
@media (max-height:900px){.how{display:none}#after{gap:9px!important;margin-top:16px!important}#after .pts{font-size:34px}#after .facts div{padding:7px 12px}#after .facts b{font-size:19px}.crewcta span{display:block;font-size:10.5px}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice7 ok')

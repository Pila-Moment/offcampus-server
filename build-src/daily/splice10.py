# Group-chat pushes (Nov 4): crew board button changes to NUDGE THE 2 WHO HAVEN'T PLAYED / SEND THE RESULTS,
# and the morning recap has a SEND button that drops yesterday's result into the house chat.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)
rep('''    <button class="btn ghost inv" data-code="${c.code}" data-name="${esc(c.name)}">INVITE TO ${esc(c.name.toUpperCase())}</button></div>`;''',
'''    ${crewButtonHTML(c, waiting)}</div>`;''')
rep("function leagueHTML(L){", r'''// The one button under each crew board does whatever moves the crew forward right now.
function crewButtonHTML(c, waiting){
  const top = c.members.find(m => m.total !== null), N = c.name;
  if (c.size >= 2 && waiting > 0 && c.played > 0) {
    const msg = `${N}: ${c.played} of ${c.size} played today. ${top.you ? `I'm leading with ${fmt(top.total)}` : `${top.nick} leads with ${fmt(top.total)}`}. Your turn:`;
    return `<button class="btn ghost inv nudge" data-code="${c.code}" data-name="${esc(N)}" data-msg="${esc(msg)}">NUDGE THE ${waiting} WHO HAVEN'T PLAYED</button>`;
  }
  if (c.size >= 2 && waiting === 0) {
    const list = c.members.filter(m => m.total !== null).slice(0, 6).map((m, i) => `${i + 1}. ${m.nick} ${fmt(m.total)}`).join('\n');
    const msg = `${N} today:\n${list}\nSame time tomorrow:`;
    return `<button class="btn ghost inv" data-code="${c.code}" data-name="${esc(N)}" data-msg="${esc(msg)}">SEND THE RESULTS TO ${esc(N.toUpperCase())}</button>`;
  }
  return `<button class="btn ghost inv" data-code="${c.code}" data-name="${esc(N)}">INVITE TO ${esc(N.toUpperCase())}</button>`;
}
async function shareText(text, url, copied){
  try { if (navigator.share) { await navigator.share({ text, url }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
  try { await navigator.clipboard.writeText(text + ' ' + url); toast(copied || 'COPIED, PASTE IT IN THE CHAT'); } catch (e) { toast(url); }
}
function leagueHTML(L){''')
rep("  el.querySelectorAll('.inv').forEach(b => b.onclick = () => invite(b.dataset.code, b.dataset.name, myScore));",
    "  el.querySelectorAll('.inv').forEach(b => b.onclick = () => b.dataset.msg ? (SFX.tap(), track(b.classList.contains('nudge') ? 'crew-nudge' : 'crew-results'), shareText(b.dataset.msg, `${CREW_INVITE_BASE}?crew=${b.dataset.code}&ref=crew`)) : invite(b.dataset.code, b.dataset.name, myScore));")
# recap SEND button
rep('''  return `<div class="recap"><div class="rh"><b>${esc(c.name.toUpperCase())}</b><span>${head ? 'YESTERDAY' : 'YOUR CREW'}</span></div>''',
'''  const msg = y && y.played ? `${c.name} yesterday: ${y.top.you ? `I took it with ${fmt(y.top.total)}` : `${y.top.nick} took it with ${fmt(y.top.total)}`} (${y.played} of ${y.size} played). New five is up:` : `${c.name}: new five is up. Who's going first?`;
  return `<div class="recap"><div class="rh"><b>${esc(c.name.toUpperCase())}</b><span>${head ? 'YESTERDAY' : 'YOUR CREW'}</span><button class="rsend" type="button" data-code="${c.code}" data-msg="${esc(msg)}">SEND TO CHAT</button></div>''')
rep("  el.innerHTML = crews.map(recapHTML).join('');\n}",
    "  el.innerHTML = crews.map(recapHTML).join('');\n  el.querySelectorAll('.rsend').forEach(b => b.onclick = () => { SFX.tap(); vibe(10); track('recap-send'); shareText(b.dataset.msg, `${CREW_INVITE_BASE}?crew=${b.dataset.code}&ref=recap`); });\n}")
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* group-chat pushes */
.recap .rh span{margin-left:auto}
.rsend{flex:0 0 auto;min-height:32px;padding:0 10px;border-radius:9px;background:var(--mint);color:var(--ink);font:700 10px var(--mono);letter-spacing:.1em}
.rsend:active{transform:scale(.96)}
.crew .inv.nudge{box-shadow:inset 0 0 0 2px var(--gold);color:var(--gold)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice10 ok')

# Real answers + morning crew recap (Nov 4, from Grace's Crew Mode review).
# Every YES/NO and every typed Showdown answer is saved. Reveals show "REAL ANSWERS SO FAR" and your crew's split (5+ only).
# Scoring does not change: everyone is scored against the same fixed number all day.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)

# ---- Receipts: send the answer, show real counts under the reveal
rep('''        <div class="how">Every 1% off costs 25 points</div>''', '''        <div class="real" id="real" hidden></div>
        <div class="how">Every 1% off costs 25 points</div>''')
rep("    addScore(pts, { off });", "    addScore(pts, { off });\n    sendAnswer(S.i, said === 'YES').then(res => showReal(res));")
rep("/* ================= SEND A QUESTION TO A FRIEND ================= */", r'''/* ================= REAL ANSWERS ================= */
async function sendAnswer(round, yes){ if (!CREWS_API || GUEST) return null; try { return await api('POST', '/api/answer', { playerId:PLAYER_ID, day:DAY.no, round, yes }); } catch (e) { return null; } }
function sendTexts(round, texts){ if (!CREWS_API || GUEST || !texts.length) return; api('POST', '/api/answer', { playerId:PLAYER_ID, day:DAY.no, round, texts }).catch(() => {}); }
function showReal(res){
  const el = $('#real'); if (!el || !res || !res.queens) return;
  const q = res.queens, c = (res.crews || []).find(x => !x.hidden);
  el.innerHTML = (q.hidden ? `<span>REAL ANSWERS COMING IN · <b>${q.n}</b> SO FAR</span>` : `<span>REAL ANSWERS SO FAR: <b>${q.yes} OF ${q.n}</b> SAID YES</span>`)
    + (c ? `<span class="rcrew">${esc(c.name.toUpperCase())}: <b>${c.yes} OF ${c.n}</b> SAID YES</span>` : '');
  el.hidden = false;
}

/* ================= SEND A QUESTION TO A FRIEND ================= */''')
# ---- Showdown: save the typed answers for this board
rep("    addScore(p, { found:found.size, of:ans.length });", "    addScore(p, { found:found.size, of:ans.length });\n    sendTexts(S.i, (S.guesses || []).filter(x => x.q === r.q).map(x => x.g));")

# ---- Start screen: morning crew recap (replaces the one-line crew strip)
i = s.index('async function crewStrip(el){'); j = s.index('function newCrewFormHTML(first){')
s = s[:i] + r'''async function crewStrip(el){
  if (!CREWS_API || !el || INVITE_CODE) return;
  let me; try { me = await api('GET', '/api/me?recap=1&playerId=' + PLAYER_ID); } catch (e) { return; }
  const crews = (me.crews || []).slice(0, innerHeight < 760 ? 1 : 2); if (!crews.length) return;
  el.innerHTML = crews.map(recapHTML).join('');
}
function recapHTML(c){
  const y = c.yesterday, top = c.members.find(m => m.total !== null);
  const today = `TODAY: ${c.played} of ${c.size} played${top ? ` · ${top.you ? 'you lead' : esc(top.nick) + ' leads'} with ${fmt(top.total)}` : ' · nobody yet, go first'}`;
  let head = '', line = '';
  if (y && y.played) {
    const won = y.top.you, gap = y.second ? y.top.total - y.second.total : 0;
    head = won ? `YOU TOOK IT <em>${fmt(y.top.total)}</em>` : `${esc(y.top.nick.toUpperCase())} TOOK IT <em>${fmt(y.top.total)}</em>`;
    line = y.played === 1 ? (won ? 'Only you played. Easy win.' : `Only ${esc(y.top.nick)} played.`)
      : won ? `${y.played} of ${y.size} played · you beat ${esc(y.second.nick)} by ${fmt(gap)}`
      : y.myRank ? `${y.played} of ${y.size} played · you came ${ordinal(y.myRank)}, ${fmt(y.top.total - y.myTotal)} behind`
      : `${y.played} of ${y.size} played · you sat it out`;
  }
  return `<div class="recap"><div class="rh"><b>${esc(c.name.toUpperCase())}</b><span>${head ? 'YESTERDAY' : 'YOUR CREW'}</span></div>
    ${head ? `<p class="rw">${head}</p><p class="rl">${line}</p>` : ''}<p class="rt">${today}</p></div>`;
}
const ordinal = n => n + (n % 100 >= 11 && n % 100 <= 13 ? 'th' : ['th','st','nd','rd'][n % 10] || 'th');
''' + s[j:]

rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* real answers + recap */
.real{display:flex;flex-direction:column;gap:3px;padding:8px 12px;border-radius:12px;background:var(--night-2);font-size:10.5px;font-weight:700;letter-spacing:.1em;color:var(--muted);text-align:center}
.real b{color:var(--text)}
.real .rcrew{color:var(--mint);font-size:10.5px;font-family:var(--mono);display:block} .real .rcrew b{color:var(--mint)}
@media (max-height:780px){#after:has(.real:not([hidden])) .facts{display:none}}
.real[hidden]{display:none}
.recap{display:flex;flex-direction:column;gap:3px;padding:11px 14px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--mint)}
.recap .rh{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.recap .rh b{font-family:var(--display);font-weight:400;font-size:16px;color:var(--mint)}
.recap .rh span{font-size:10px;font-weight:700;letter-spacing:.16em;color:var(--muted)}
.recap p{margin:0}
.recap .rw{font-family:var(--display);font-size:22px;line-height:1.05;color:var(--text)}
.recap .rw em{font-style:normal;color:var(--gold)}
.recap .rl{font-size:12px;font-weight:700;color:var(--muted)}
.recap .rt{margin-top:3px;font-size:10.5px;font-weight:700;letter-spacing:.08em;color:var(--mint)}
#crewstrip:not(:empty) ~ .howto{display:none}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice9 ok')

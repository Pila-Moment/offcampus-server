# Challenge links (Nov 4): a shared score link opens the daily with "YOUR FRIEND GOT 3,212. BEAT IT.",
# and the result stamp says whether you beat them, so the share back is "I beat you".
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)

rep("const SHARE_URL = 'offcampusontario.ca';", """const SHARE_URL = 'offcampusontario.ca';
// A friend's challenge: daily.html?ref=share&s=3212&d=2 (only counts on the same day's five)
const CHAL = (() => { const q = new URLSearchParams(location.search), sc = parseInt(q.get('s'), 10), d = parseInt(q.get('d'), 10);
  const key = 'oc-chal-' + d;
  if (Number.isFinite(sc) && sc >= 0 && sc <= 5000 && d === DAY.no) { store.set(key, sc); return sc; }
  const saved = store.get('oc-chal-' + DAY.no); return Number.isFinite(saved) ? saved : null; })();""")
# share links go straight to the daily, carrying the score
rep("Bet you can't beat me. Same five for everyone at ${DAY.school} today: https://${SHARE_URL}/?ref=share`;",
    "Bet you can't beat me. Same five for everyone at ${DAY.school} today: https://${SHARE_URL}/daily.html?ref=share&s=${total}&d=${DAY.no}`;")
rep("const url = `https://${SHARE_URL}/?ref=q`;", "const url = `https://${SHARE_URL}/daily.html?ref=q`;")
# start screen banner
rep('''    <div id="joinbox"></div><div id="crewstrip"></div>''',
    '''    ${CHAL !== null && !GUEST ? `<div class="chal"><small>YOUR FRIEND GOT</small><b>${fmt(CHAL)}</b><span>Same five, today only.<br>Can you beat it?</span></div>` : ''}
    <div id="joinbox"></div><div id="crewstrip"></div>''')
# result stamp
rep("else { const r = saveDay(); st = r.st; stamp = stampFor(st, r.newBest); track('finish');",
    "else { const r = saveDay(); st = r.st; stamp = CHAL !== null ? (S.total > CHAL ? `BEAT YOUR FRIEND BY ${fmt(S.total - CHAL)}` : S.total === CHAL ? 'TIED YOUR FRIEND' : `${fmt(CHAL - S.total)} SHORT OF YOUR FRIEND`) : stampFor(st, r.newBest); if (CHAL !== null) track(S.total > CHAL ? 'chal-won' : 'chal-lost'); track('finish');")
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* challenge link */
.chal{display:grid;grid-template-columns:auto 1fr;grid-template-rows:auto auto;column-gap:14px;align-items:center;padding:12px 16px;border-radius:16px;background:color-mix(in srgb, var(--red) 16%, var(--night-2));box-shadow:inset 0 0 0 2px var(--red)}
.chal small{grid-column:1;font-size:10.5px;font-weight:700;letter-spacing:.14em;color:var(--muted)}
.chal b{grid-column:1;font-family:var(--display);font-weight:400;font-size:40px;line-height:1;color:var(--text);font-variant-numeric:tabular-nums}
.chal span{grid-column:2;grid-row:1 / span 2;font-family:var(--display);font-size:17px;line-height:1.15;color:var(--red)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice8 ok')

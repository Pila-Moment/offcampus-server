s=open('src.html').read()
def rep(a,b,count=1):
    global s
    assert s.count(a)>=1, a[:70]
    s=s.replace(a,b) if count==0 else s.replace(a,b,count)
def span(a,b,new):
    global s
    i=s.index(a); j=s.index(b,i); s=s[:i]+new+s[j:]
# content: first-year floor goes to 24%
rep('q:"Have you ever hooked up with someone from your first-year floor?", pct:27','q:"Have you ever hooked up with someone from your first-year floor?", pct:24')
# buttons that move into a dock at the bottom of the screen (no scrolling to find them)
rep('<button class="btn pulse" id="go">PLAY TODAY\'S 5</button>','<button class="btn pulse dock" id="go">PLAY TODAY\'S 5</button>')
rep('<button class="btn" id="lock" style="margin-top:12px">LOCK IT IN</button>','<button class="btn dock" id="lock">LOCK IT IN</button>')
rep('<button class="btn" id="nx">${S.i + 1 < DAY.rounds.length ? \'NEXT ROUND\' : \'SEE MY SCORE\'}</button>','<button class="btn dock" id="nx">${S.i + 1 < DAY.rounds.length ? \'NEXT ROUND\' : \'SEE MY SCORE\'}</button>',0)
rep('<button class="btn" id="lock" disabled style="margin-top:12px">DROP A PIN FIRST</button>','<button class="btn dock" id="lock" disabled>DROP A PIN FIRST</button>')
rep('<button class="btn" id="nx2">SEE MY SCORE</button>','<button class="btn dock" id="nx2">SEE MY SCORE</button>')
# results: hype the unlock
rep("""? `<div class="gate ok"><b>PRIZE SPIN UNLOCKED</b><span>You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.</span></div><button class="btn pulse" id="prize">SPIN FOR YOUR PRIZE</button>`""",
    """? `<div class="gate ok"><b>YOU UNLOCKED A PRIZE!</b><span>You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.</span></div><button class="btn pulse dock go" id="prize">SPIN FOR YOUR PRIZE!</button>`""")
rep("""<a class="btn mint" href="party.html">PLAY THE PARTY GAMES</a>`}""","""<a class="btn mint dock" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a>`}""")
# intro: the five rounds as one compact row so the whole screen fits
i=s.index('<ol class="lineup">'); j=s.index('</ol>',i)+len('</ol>')
s=s[:i]+"""<div class="five" aria-label="Today's rounds">
      <div class="r"><b>1</b><span>RECEIPTS</span></div><div class="s"><b>2</b><span>SHOW­DOWN</span></div><div class="r"><b>3</b><span>RECEIPTS</span></div><div class="s"><b>4</b><span>SHOW­DOWN</span></div><div class="p"><b>5</b><span>DROP PIN</span></div></div>
    <p class="howto"><b>Receipts:</b> yes or no, then guess what % said yes. <b>Showdown:</b> name the top answers before 3 X's. <b>Drop the Pin:</b> where and when was this photo taken?</p>"""+s[j:]
# first spin becomes a sliding reel
span("async function prize(){","async function wheel2(brand){",open('parts/reel.js').read())
rep('<button class="btn pulse" id="sp2">REVEAL MY PRIZE</button>','<button class="btn pulse dock go" id="sp2">REVEAL MY PRIZE!</button>')
# no skill-testing question: straight to the code
rep("""    <div class="stq" id="stq"><label for="sa">One quick skill-testing question to claim it: ${a} × ${b2} − ${c} = ?</label><div><input id="sa" inputmode="numeric" autocomplete="off"><button class="btn" id="sok">CLAIM</button></div></div>
    <div id="claimed"></div>""","""    <div id="claimed"></div>""")
rep("""  $('#sok').onclick = () => {
    if (+$('#sa').value !== ans) { SFX.buzz(); toast('NOT QUITE, TRY AGAIN'); return; }
    SFX.ok(); $('#stq').remove();
    const cl = $('#claimed');""","""  {
    const cl = $('#claimed');""")
rep("  const a = 2 + Math.floor(Math.random() * 8), b2 = 3 + Math.floor(Math.random() * 7), c = 1 + Math.floor(Math.random() * 9), ans = a * b2 - c;\n","")
rep("""    <div class="lbl" style="color:var(--red)">${jackpot ? 'YOU HIT THE WEEKLY JACKPOT' : p.big ? 'BIG WIN' : 'YOU WON'}</div>""","""    <div class="lbl" style="color:var(--red)">${jackpot ? 'YOU HIT THE WEEKLY JACKPOT!' : p.big ? 'BIG WIN!' : 'YOU WON!'}</div>""")
s=s.replace("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", open('parts/extra2.css').read()+"@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>")
open('src.html','w').write(s)
print('splice2 ok')

s=open('src.v1.html').read()
P=lambda f: open('parts/'+f).read()
def span(a,b,new):
    global s
    i=s.index(a); j=s.index(b,i); s=s[:i]+new+s[j:]
def rep(a,b):
    global s
    assert a in s, a[:60]; s=s.replace(a,b)
span("/* ================= TODAY'S DAILY","/* ================= scoring",P('A_content.js'))
rep("const SURVEY_SECS = 40;         // Survey: time to find answers before it closes","const SURVEY_SECS = 60;         // Survey: time to find answers before it closes\nconst UNLOCK = 2500;            // score needed (out of 5,000) to unlock the prize spin")
rep("// demo school board\nconst BOARD = { q:{ avg:2914, n:1284 }, w:{ avg:2871, n:1530 } };","// demo numbers for today at the school\nconst TODAY = { n:1284, avg:2914 };")
span("function hud(){","/* ================= RECEIPTS",P('C_hud_intro.js'))
span("const PIN_HTML =","async function buildMap",P('F_pin.js'))
span("async function pinRound(){","/* ================= RESULTS",P('F_pinround.js'))
span("async function results(){","/* ================= THE PRIZE",'')
span("/* ================= THE PRIZE","intro();\n})();",P('G_results.js')+P('H_prize.js'))
rep("""        <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
        <button class="btn" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.whoosh();""","""        <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div>
        <div class="how">Every 1% off costs 25 points</div>
        <button class="btn" id="nx">${S.i + 1 < DAY.rounds.length ? 'NEXT ROUND' : 'SEE MY SCORE'}</button></div>`;
    SFX.whoosh();""")
rep("""  const gi = $('#gi');
  setTimeout(() => { try { gi.focus({ preventScroll:true }); } catch (e) {} }, 350);""","""  const gi = $('#gi');
  // phone keyboard open: shrink the question and board so question, board, timer and box all fit above it
  const fit = () => { const vv = window.visualViewport; if (!vv || !document.body.classList.contains('typing')) return; const f = $('#gf'); if (!f) return; const r = f.getBoundingClientRect(), d = r.bottom + 10 - (vv.offsetTop + vv.height); if (Math.abs(d) > 4) window.scrollBy(0, d); };
  gi.addEventListener('focus', () => { document.body.classList.add('typing'); setTimeout(fit, 320); });
  gi.addEventListener('blur', () => document.body.classList.remove('typing'));
  if (window.visualViewport) window.visualViewport.addEventListener('resize', fit);
  setTimeout(() => { try { gi.focus({ preventScroll:true }); } catch (e) {} }, 350);""")
rep("    if (over) return; over = true; cancelAnimationFrame(timerId);\n    gi.blur();","    if (over) return; over = true; cancelAnimationFrame(timerId);\n    gi.blur(); document.body.classList.remove('typing'); if (window.visualViewport) window.visualViewport.removeEventListener('resize', fit);")
anchor="@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>"
rep(anchor, open('parts/extra.css').read()+anchor)
open('src.html','w').write(s)
print('ok', len(s))
s=open('src.html').read()
rep(".meter .you span{position:absolute;bottom:100%;left:50%;transform:translateX(-50%);font-size:10px;font-weight:700;letter-spacing:.12em;white-space:nowrap;color:var(--text);padding-bottom:2px}",
    ".meter .you span{position:absolute;top:100%;left:50%;transform:translateX(-50%);font-size:10px;font-weight:700;letter-spacing:.12em;white-space:nowrap;color:var(--text);padding-top:3px}")
rep('<div id="after" hidden style="display:flex;flex-direction:column;gap:12px;margin-top:16px">','<div id="after" hidden style="display:flex;flex-direction:column;gap:12px;margin-top:26px">')
rep("gi.addEventListener('focus', () => { document.body.classList.add('typing'); setTimeout(fit, 320); });","gi.addEventListener('focus', () => { if (!matchMedia('(pointer:coarse)').matches) return; document.body.classList.add('typing'); setTimeout(fit, 320); });")
rep("<div class=\"kick\">${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)} · ${esc(DAY.date.toUpperCase())}</div>\n    <h1>TODAY'S <span>FIVE</span></h1>","<div class=\"kick\">${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)}</div>\n    <h1>TODAY'S <span>FIVE</span></h1>")
rep("<button class=\"visit\" id=\"visit\">VISIT ${esc(brand.name.toUpperCase())} &rarr;</button>","<button class=\"visit\" id=\"visit\">VISIT THEIR SITE &rarr;</button>")
open('src.html','w').write(s)
print('fixes ok')

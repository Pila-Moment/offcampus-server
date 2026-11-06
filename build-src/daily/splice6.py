# No-scroll pass (Nov 4): pin round in two steps (map, then year), I'M DONE on survey boards, compact results and done screens.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:80]; s=s.replace(a,b,1)

# ---- 1. Survey: I'M DONE button in the timer row (visible even with the keyboard open)
rep('<span class="tleft" id="tl">${SURVEY_SECS}</span></div>',
    '<span class="tleft" id="tl">${SURVEY_SECS}</span><button class="sdone" id="sdone" type="button">I\'M DONE</button></div>')
rep("  endAt = performance.now() + SURVEY_SECS * 1000; timerId = requestAnimationFrame(tick);",
    "  endAt = performance.now() + SURVEY_SECS * 1000; timerId = requestAnimationFrame(tick);\n"
    "  const sd = $('#sdone'), quit = e => { if (e) e.preventDefault(); if (over) return; SFX.tap(); vibe(15); finish(found.size ? 'YOU CALLED IT' : 'PASSED'); };\n"
    "  sd.addEventListener('touchstart', quit, { passive:false }); sd.addEventListener('mousedown', quit); sd.onclick = quit;")
rep("$('#gf').style.display = 'none'; $('.sbar').style.opacity = .5;", "$('#gf').style.display = 'none'; $('.sbar').style.opacity = .5; const sdb = $('#sdone'); if (sdb) sdb.style.display = 'none';")

# ---- 2. Pin round: step 1 = photo + map, step 2 = photo + year. Nothing below the fold.
rep('<div id="lower"><div class="yearbox">', '<div id="lower"><div class="yearbox" id="yb" hidden><div class="yb-top"><div class="lbl">WHAT YEAR WAS THIS TAKEN?</div><button class="yb-back" id="ybb" type="button">&larr; MOVE MY PIN</button></div>')
rep('<div class="yearbox" id="yb" hidden><div class="yb-top"><div class="lbl">WHAT YEAR WAS THIS TAKEN?</div><button class="yb-back" id="ybb" type="button">&larr; MOVE MY PIN</button></div><div class="lbl">WHAT YEAR?</div>',
    '<div class="yearbox" id="yb" hidden><div class="yb-top"><div class="lbl">WHAT YEAR WAS THIS TAKEN?</div><button class="yb-back" id="ybb" type="button">&larr; MOVE MY PIN</button></div>')
rep("    const b = $('#lock'); b.disabled = false; b.textContent = 'LOCK IT IN';",
    "    const b = $('#lock'); b.disabled = false; if (step === 1) b.textContent = 'NEXT: WHAT YEAR?';")
rep("  const r = R(), P = r.photo; let guess = null, year = YEAR_START, pin = null, locked = false;",
    "  const r = R(), P = r.photo; let guess = null, year = YEAR_START, pin = null, locked = false, step = 1;")
rep("  $('#lock').onclick = async () => {\n    if (locked || !guess) return; locked = true;",
    "  const showStep = n => { step = n; const yb = $('#yb'), mw = $('#mw'), b = $('#lock');\n"
    "    yb.hidden = n !== 2; mw.style.display = n === 2 ? 'none' : ''; b.textContent = n === 2 ? 'LOCK IT IN' : 'NEXT: WHAT YEAR?';\n"
    "    if (n === 1 && map) setTimeout(() => map.invalidateSize(), 30); window.scrollTo(0, 0); };\n"
    "  $('#ybb').onclick = () => { SFX.tap(); showStep(1); };\n"
    "  $('#lock').onclick = async () => {\n    if (locked || !guess) return;\n    if (step === 1) { SFX.ok(); vibe(15); showStep(2); return; }\n    locked = true; $('#yb').hidden = true; $('#mw').style.display = ''; $('#mw').classList.add('rev'); map.invalidateSize();")

# ---- 3. Results / done screens: slimmer card, one-line stats, one row of buttons
rep("const statsRow = st => `<div class=\"today\"><h3>YOU</h3><div><small>STREAK</small><b>${st.n || 0}</b></div><div><small>BEST</small><b>${fmt(st.best || 0)}</b></div><div><small>DAYS</small><b>${st.days || 0}</b></div></div>`;",
    "const statsRow = st => `<div class=\"statline\"><span>STREAK <b>${st.n || 0}</b></span><span>BEST <b>${fmt(st.best || 0)}</b></span><span>DAYS PLAYED <b>${st.days || 0}</b></span></div>`;")
rep('''const tailHTML = () => `<div class="row2"><button class="btn ghost" id="share">SHARE MY SCORE</button><button class="btn ghost" id="see">SEE THE IMAGE</button></div>
    <a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener" style="text-decoration:none;color:var(--text)">FOLLOW US ON INSTAGRAM</a>''',
'''const tailHTML = () => `<div class="row3"><button class="btn ghost" id="share">SHARE</button><button class="btn ghost" id="see">IMAGE</button><a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener">INSTAGRAM</a></div>''')

rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* no-scroll pass */
.sbar .sdone{flex:0 0 auto;min-height:36px;padding:0 12px;border-radius:10px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--muted);color:var(--text);font:700 11px var(--mono);letter-spacing:.1em;-webkit-tap-highlight-color:transparent}
.sbar .sdone:active{transform:scale(.95)}
.bigx,.redflash{pointer-events:none}
.yearbox[hidden]{display:none!important}
.yb-top{display:flex;justify-content:space-between;align-items:center;gap:8px}
.yb-back{min-height:40px;padding:0 10px;border-radius:10px;background:var(--night);color:var(--mint);font:700 11px var(--mono);letter-spacing:.08em;white-space:nowrap}
.yearbox{gap:12px;padding:16px 14px}
.yearbox .nix i{width:52px;height:66px;font-size:54px}
.yearbox input[type=range]{height:44px}
.statline{display:flex;justify-content:space-between;gap:8px;padding:10px 14px;border-radius:12px;background:var(--night-2);font-size:10.5px;font-weight:700;letter-spacing:.12em;color:var(--muted)}
.statline b{font-family:var(--display);font-weight:400;font-size:17px;letter-spacing:0;color:var(--text);margin-left:4px;font-variant-numeric:tabular-nums}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.row3 .btn{min-height:50px;font-size:14px;padding:0 6px;text-decoration:none;color:var(--text);display:grid;place-items:center}
.card{padding:16px 16px 18px}
.card .total{font-size:clamp(56px,17vw,92px);margin-top:6px}
.squares{margin-top:12px}
.rankstamp{margin-top:12px}
.gate{padding:9px 12px}
.gate b{font-size:19px;line-height:1.1}
.gate span{font-size:11.5px}
@media (max-height:900px){.gate span,.crewcta span,.statline,.kick{display:none}.crewcta{min-height:54px;padding:8px 12px}.card{padding:12px 14px 14px}.card .total{font-size:clamp(48px,14vw,70px)}.card .of{margin-top:2px}.squares{gap:6px;margin-top:8px}.squares .sq i{aspect-ratio:auto;height:34px}.squares .sq{gap:3px}.rankstamp{margin-top:8px;font-size:14px}.screen{gap:9px}.gate{padding:8px 12px}.crew{padding:10px 12px;gap:7px}.crew .ch b{font-size:16px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;min-width:0}.crew li{padding:6px 10px}.crew .inv{min-height:44px;font-size:13px}.crew .cnote{display:none}}
@media (max-height:760px){.crews .more{display:none}}
.mapwrap{isolation:isolate;z-index:0}
.mapwrap.rev{height:min(38vh,320px);min-height:180px}
@media (max-height:900px){.yrev{padding:10px 12px}.yrev b{font-size:58px}.pinrev .pts{font-size:40px}}
@media (max-height:700px){.cd{display:none}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
rep('const CREW_ROWS = 5;', 'const CREW_ROWS = innerHeight < 760 ? 3 : 5;')
rep('<div class="yrev"><small>THE PHOTO WAS TAKEN IN</small>', '<div class="yrev"><small>${esc(P.title.toUpperCase())} · TAKEN IN</small>')
open('src.html','w').write(s)
print('splice6 ok')

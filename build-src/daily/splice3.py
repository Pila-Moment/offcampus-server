s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,1)
rep("/* ================= scoring", open('parts/guest.js').read()+"/* ================= scoring")
# intro: preview banner + skip straight to the spin
rep("""    <h1>TODAY'S <span>FIVE</span></h1>
    <p class="sub">""","""    <h1>TODAY'S <span>FIVE</span></h1>
    ${GUEST ? `<div class="guest"><b>PREVIEW FOR ${esc(GUEST.name.toUpperCase())}</b><span>Play it like a student, or jump straight to where your spot shows up.</span><button id="skip">SKIP TO THE PRIZE SPIN &rarr;</button></div>` : ''}
    <p class="sub">""")
rep("""  $('#go').onclick = () => { SFX.ok(); vibe(20); next(); };
}""","""  $('#go').onclick = () => { SFX.ok(); vibe(20); next(); };
  const sk = $('#skip'); if (sk) sk.onclick = () => { SFX.ok(); vibe(20); prize(); };
}""")
# results: a brand preview always gets to spin
rep("const beat = beatPct(S.total), ok = S.total >= UNLOCK;","const beat = beatPct(S.total), ok = S.total >= UNLOCK || !!GUEST;")
# the spinner always lands on the previewed spot
rep("const win = forced ? JACKPOT : pickSpot();","const win = forced ? JACKPOT : GUEST || pickSpot();")
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>",
""".guest{display:flex;flex-direction:column;gap:6px;padding:12px 14px;border-radius:14px;background:var(--cream);color:var(--ink)}
.guest b{font-family:var(--display);font-weight:400;font-size:16px;letter-spacing:.02em}
.guest span{font-size:12.5px;font-weight:600;line-height:1.4}
.guest button{align-self:flex-start;min-height:44px;padding:0 14px;border-radius:10px;background:var(--ink);color:var(--gold);font-family:var(--display);font-size:14px;letter-spacing:.03em}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice3 ok')

# Preseason: a new five every day, one play per phone per day, streaks, prize teaser, play counter.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,1)
def span(a,b,new):
    global s
    i=s.index(a); j=s.index(b,i); s=s[:i]+new+s[j:]
days=open('parts/days.js').read()
span("const DAY = {", "\n/* ================= SAMPLE PRIZES", days + """
const FIRST_DAY = '2026-11-03';   // the date of Daily No. 001. A new five starts every day at 4am Toronto time.
const PRIZES_LIVE = false;        // false = preseason: the prize spin is a "coming soon" teaser. true = real prizes.
function torontoDate(){ return new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', year:'numeric', month:'2-digit', day:'2-digit' }).format(new Date(Date.now() - 4 * 3600e3)); }
const DAY_INDEX = (() => { const f = new URLSearchParams(location.search).get('day'); if (f && /^\\d+$/.test(f)) return Math.max(0, +f - 1);
  return Math.max(0, Math.round((Date.parse(torontoDate()) - Date.parse(FIRST_DAY)) / 864e5)); })();
const DAY = Object.assign({ school:"Queen's", no:DAY_INDEX + 1,
  date:new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', weekday:'short', month:'short', day:'numeric' }).format(new Date(Date.now() - 4 * 3600e3)) },
  DAYS[DAY_INDEX % DAYS.length]);
const store = { get(k){ try { return JSON.parse(localStorage.getItem(k)); } catch (e) { return null; } }, set(k, v){ try { localStorage.setItem(k, JSON.stringify(v)); } catch (e) {} } };
const PLAY_KEY = 'oc-played-' + DAY.no;
const REPLAY = /[?&]again\\b/.test(location.search);   // add ?again to the link to replay today (for testing)
function track(name){ try { if (window.goatcounter && window.goatcounter.count) window.goatcounter.count({ path:'event-' + name, title:name, event:true }); } catch (e) {} }
""")
# results, score card and teaser
span("async function drawCard(beat){", "/* ================= THE PRIZE", open('parts/preseason.js').read())
# intro: already played -> done screen; streak; preseason copy; count a start
rep("function intro(){\n  fresh(); document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);",
    "function intro(){\n  fresh(); document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);\n  const done = !GUEST && !REPLAY && store.get(PLAY_KEY); if (done) return doneScreen(done);\n  const st = store.get('oc-streak'); const streak = st && st.last === DAY.no - 1 && st.n >= 1 ? st.n : 0;")
rep("<div class=\"kick\">${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)}</div>",
    "<div class=\"kick\">${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)} · ${esc(DAY.date.toUpperCase())}</div>${streak ? `<div class=\"streak\">${streak}-DAY STREAK · KEEP IT GOING</div>` : ''}")
rep("<div class=\"goal\"><b>${fmt(UNLOCK)}</b><span>Score ${fmt(UNLOCK)} out of 5,000 to unlock today's <em>free prize spin</em>.</span></div>",
    "<div class=\"goal\"><b>${fmt(UNLOCK)}</b><span>${PRIZES_LIVE || GUEST ? `Score ${fmt(UNLOCK)} out of 5,000 to unlock today's <em>free prize spin</em>.` : `Score ${fmt(UNLOCK)} out of 5,000 to unlock the prize spin. <em>Prizes from Kingston spots drop soon.</em>`}</span></div>")
rep("<p class=\"demo-note\">Demo build. Percentages, survey boards, player numbers and prizes are samples.</p>",
    "<p class=\"demo-note\">Free to play. One go per day. A new five every day at 4am.</p>")
rep("$('#go').onclick = () => { SFX.ok(); vibe(20); next(); };", "$('#go').onclick = () => { SFX.ok(); vibe(20); track('start'); next(); };")
# styles
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>",
""".streak{align-self:flex-start;padding:6px 12px;border-radius:999px;background:var(--red);color:var(--paper);font-size:11px;font-weight:700;letter-spacing:.14em}
.rc.lock{background:var(--night);box-shadow:inset 0 0 0 3px var(--gold);color:var(--gold)}
.rc.lock b{font-size:26px}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
# free play counter (GoatCounter). Make an account with the code "offcampusontario" at goatcounter.com
rep("</script>\n</body></html>", "</script>\n<script data-goatcounter=\"https://offcampusontario.goatcounter.com/count\" async src=\"https://gc.zgo.at/count.js\"></script>\n</body></html>")
open('src.html','w').write(s)
print('splice4 ok')

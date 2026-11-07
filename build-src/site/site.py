# Builds the Off Campus demo pages: home menu (index.html), party.html, prizes.html, brands.html.
# Run from the scratchpad folder: python3 site/site.py
import html, re
SP = '/tmp/claude-0/-home-claude/5bf8c0ba-cb85-583b-8189-97cffac50747/scratchpad'
OUT = SP + '/bundle/'
e = html.escape

# ---- settings you can change ----
UNLOCK = '2,500'
FOUNDING_SPOTS = 8          # how many brands get on the wheel for the launch
CONTACT = 'https://ig.me/m/offcampuskingston'   # opens an Instagram DM to @offcampuskingston

# made-up demo spots (same as the daily game). slice = size on the wheel.
BRANDS = [
  dict(name='Night Shift', kind='Club · student nights · 19+', col='#B03BD1', mono='NS', slice=1.5, small='Skip the line on Saturday', big='2 free entries'),
  dict(name='Locked In Escapes', kind='Escape rooms · downtown', col='#6C4BE0', mono='LI', slice=1.3, small='20% off any room', big='A free room for 4'),
  dict(name='Splitwood Axe Throwing', kind='Axe throwing · groups', col='#3E8E5A', mono='SA', slice=1.2, small='2-for-1 lane booking', big='A free lane for 4'),
  dict(name='Limestone Bean Co.', kind='Coffee · Princess St', col='#C8782A', mono='LB', slice=1, small='15% off any drink', big='A free latte'),
  dict(name='Crumb Club Cookies', kind='Cookies · pre-order drops', col='#E8608A', mono='CC', slice=1, small='Buy 2 cookies, get 1 free', big='A free cookie'),
  dict(name='Stuart St. Supply', kind='Student-made merch', col='#2E5BD8', mono='SS', slice=1, small='15% off any crewneck', big='A free crewneck'),
  dict(name='Pole & Flow Studio', kind='Fitness classes', col='#D04545', mono='PF', slice=.9, small='A free beginner class', big='A free 3-class pass'),
  dict(name='Fresh Start Crew', kind='Student house cleaning', col='#2BA3C7', mono='FS', slice=.8, small='$10 off a house clean', big='A free kitchen deep clean'),
]

FONTS = '''<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Bowlby+One&family=Bungee+Inline&family=Big+Shoulders+Display:wght@700;800;900&family=IBM+Plex+Mono:wght@500;600;700&display=swap">'''

BASE_CSS = '''
:root{
  --night:#07060F; --night-2:#120F24; --night-3:#1C1836; --text:#F6F1E8; --muted:#A49FC0;
  --gold:#FFC83D; --gold-deep:#B97F05; --red:#FF3B4A; --navy:#0A1036; --tile:#2246E6; --stone:#E6E0D2;
  --lake:#0C2B35; --pin:#FF5A1F; --amber:#FFB23F; --mint:#7FE0C4; --grape:#170A26; --cup:#EF2B3A; --hi:#FFE63B;
  --ink:#111111; --cream:#FFF5DE; --good:#3BD67A; --blue:#2D4BFF;
  --display:"Bowlby One","Arial Black",Impact,sans-serif;
  --marquee:"Bungee Inline","Bowlby One","Arial Black",sans-serif;
  --tall:"Big Shoulders Display","Oswald","Arial Narrow",Impact,sans-serif;
  --mono:"IBM Plex Mono",Menlo,Consolas,monospace;
  --ease-pop:cubic-bezier(.2,1.45,.4,1); --ease-out:cubic-bezier(.16,1,.3,1);
  color-scheme:dark;
}
html,body{min-height:100%}
body{margin:0;background:var(--night);color:var(--text);font-family:var(--mono);overflow-x:hidden;-webkit-tap-highlight-color:transparent}
a{color:inherit}
a:focus-visible,button:focus-visible{outline:3px solid var(--hi);outline-offset:3px}
button{font:inherit;color:inherit;border:0;background:none;cursor:pointer;touch-action:manipulation}
.bgfx{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none}
.bgfx .orb{position:absolute;width:52vmax;height:52vmax;border-radius:50%;filter:blur(100px);opacity:.22;will-change:transform}
.bgfx .a{background:var(--tile);left:-20vmax;top:-22vmax;animation:d1 14s ease-in-out infinite alternate}
.bgfx .b{background:var(--pin);right:-22vmax;bottom:-20vmax;animation:d2 16s ease-in-out infinite alternate}
@keyframes d1{to{transform:translate(10vmax,8vmax) scale(1.1)}}
@keyframes d2{to{transform:translate(-10vmax,-6vmax) scale(.9)}}
.wrap{position:relative;z-index:1;box-sizing:border-box;display:flex;flex-direction:column;gap:clamp(14px,2.4vh,26px);max-width:1180px;margin:0 auto;
  padding-left:max(16px, env(safe-area-inset-left, 0px));padding-right:max(16px, env(safe-area-inset-right, 0px));padding-block:14px 28px}
.tabs{display:flex;gap:6px;align-items:stretch;position:sticky;top:0;z-index:20;padding:10px 0;margin:-10px 0 0;background:color-mix(in srgb, var(--night) 88%, transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.tabs a{flex:1;display:grid;place-items:center;min-height:46px;padding:0 6px;border-radius:12px;background:var(--night-2);box-shadow:inset 0 0 0 1.5px var(--night-3);color:var(--muted);text-decoration:none;font-family:var(--display);font-size:clamp(12px,3.4vw,16px);letter-spacing:.03em;text-align:center;line-height:1}
.tabs a.home{flex:0 0 46px;color:var(--gold)}
.tabs a.on{background:var(--gold);color:var(--ink);box-shadow:0 4px 0 var(--gold-deep)}
.kick{font-size:12px;font-weight:700;letter-spacing:.26em;color:var(--mint)}
.h1{margin:0;font-family:var(--display);font-weight:400;font-size:clamp(40px,min(9vw,11vh),96px);line-height:.9;text-wrap:balance}
.h1 span{color:var(--gold)}
.lede{margin:0;font-size:clamp(14px,1.8vh,17px);line-height:1.5;font-weight:600;color:var(--muted);max-width:62ch}
.lede b{color:var(--text)}
.btn{box-sizing:border-box;display:flex;align-items:center;justify-content:center;gap:10px;min-height:58px;padding:0 20px;border-radius:16px;font-family:var(--display);font-size:19px;letter-spacing:.03em;text-decoration:none;
  background:var(--gold);color:var(--ink);box-shadow:0 6px 0 var(--gold-deep);transition:transform .12s, box-shadow .12s}
.btn:active{transform:translateY(4px);box-shadow:0 2px 0 var(--gold-deep)}
.demo{font-size:11px;color:var(--muted);line-height:1.5}
footer{display:flex;flex-wrap:wrap;justify-content:space-between;gap:8px;font-size:11px;color:var(--muted);font-weight:600;padding-top:8px}
footer b{color:var(--text)}
.toast{position:fixed;left:50%;bottom:12%;z-index:60;transform:translateX(-50%);padding:10px 16px;border-radius:12px;background:var(--cream);color:var(--ink);font-family:var(--display);font-size:14px;letter-spacing:.03em;box-shadow:0 6px 0 var(--gold-deep);animation:toast 1.8s var(--ease-out) forwards;white-space:nowrap}
@keyframes toast{0%{opacity:0;transform:translate(-50%,10px)}12%,80%{opacity:1;transform:translate(-50%,0)}100%{opacity:0}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
'''

def tabs(on):
    t = lambda k, href, label: f'<a href="{href}" class="{"on" if on == k else ""}">{label}</a>'
    return f'<nav class="tabs" aria-label="Off Campus"><a class="home" href="./" aria-label="Off Campus home">OC</a>{t("daily","daily.html","DAILY")}{t("party","party.html","PARTY GAMES")}{t("clubs","clubs.html","CLUBS")}</nav>'

FOOT = '<footer><span><b>Free to play.</b> No sign-up, no app. <a href="clubs.html" style="color:var(--mint)">Run a club? Get your club its own game &rarr;</a></span><span>Off Campus · Kingston · Not affiliated with Queen\'s University</span></footer>'
BG = '<div class="bgfx" aria-hidden="true"><div class="orb a"></div><div class="orb b"></div></div>'
TOAST_JS = "<script>window.ocToast=function(t){var d=document.createElement('div');d.className='toast';d.textContent=t;document.body.appendChild(d);setTimeout(function(){d.remove()},1900)};</script>"
COUNTDOWN_JS = '''<script>
(function(){
  var els = document.querySelectorAll('[data-cd]'); if (!els.length) return;
  function tick(){
    var p = {}; new Intl.DateTimeFormat('en-CA', { timeZone:'America/Toronto', hour:'numeric', minute:'numeric', second:'numeric', hour12:false }).formatToParts(new Date()).forEach(function(x){ p[x.type] = x.value; });
    var secs = (4 - (+p.hour % 24)) * 3600 - (+p.minute) * 60 - (+p.second); if (secs <= 0) secs += 86400;
    var t = Math.floor(secs / 3600) + 'h ' + String(Math.floor(secs % 3600 / 60)).padStart(2, '0') + 'm';
    els.forEach(function(el){ el.textContent = t; });
  }
  tick(); setInterval(tick, 15000);
})();
</script>'''

def page(title, css, body, sub=True):
    head = f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n{FONTS}\n<style>{BASE_CSS}{css}</style>\n'
    content = f'{head}{BG}\n<main class="wrap">\n{body}\n{FOOT}\n</main>\n{TOAST_JS}{COUNTDOWN_JS}'
    if not sub:
        return content
    return ('<!doctype html>\n<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + content.replace('<main', '</head><body>\n<main', 1).replace(BG + '\n</head><body>', '</head><body>\n' + BG, 1)
            + '\n</body></html>\n')

def subpage(title, css, body):
    head = f'<title>{title}</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n{FONTS}\n<style>{BASE_CSS}{css}</style>'
    return ('<!doctype html>\n<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            f'{head}\n</head><body>\n{BG}\n<main class="wrap">\n{body}\n{FOOT}\n</main>\n{TOAST_JS}{COUNTDOWN_JS}\n</body></html>\n')

# =============== HOME (menu) ===============
home_css = '''
.bar{display:flex;align-items:center;justify-content:space-between;gap:12px}
.logo{font-family:var(--display);font-size:clamp(20px,2.6vw,30px);line-height:1}
.logo span{color:var(--gold)}
.school{display:inline-flex;align-items:center;gap:8px;height:38px;padding:0 14px;border-radius:999px;background:var(--night-2);box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--gold) 60%, transparent);font-size:12px;font-weight:700;letter-spacing:.12em;white-space:nowrap}
.school i{width:10px;height:10px;border-radius:50%;background:var(--red);box-shadow:0 0 0 2px var(--gold), 0 0 0 4px var(--tile)}
.tag{margin:0;font-family:var(--display);font-weight:400;font-size:clamp(38px,min(8.6vw,10vh),104px);line-height:.88;text-wrap:balance}
.tag span{color:var(--gold);text-shadow:0 0 30px color-mix(in srgb, var(--gold) 50%, transparent)}
.menu{display:grid;grid-template-columns:1.7fr 1fr;grid-template-rows:1fr 1fr;gap:clamp(12px,1.6vw,22px)}
.menu .t-daily{grid-row:1 / span 2;min-height:clamp(320px,58vh,560px)}
.t-daily h2{font-size:clamp(56px,min(7.4vw,12vh),120px)}
.play{display:flex;align-items:center;justify-content:center;min-height:62px;margin-top:8px;border-radius:16px;background:var(--good);color:var(--ink);font-family:var(--display);font-size:clamp(20px,2.4vw,28px);letter-spacing:.03em;
  box-shadow:0 6px 0 #1E8A4A, 0 0 34px color-mix(in srgb, var(--good) 45%, transparent);animation:throb 1.4s ease-in-out infinite}
@keyframes throb{50%{transform:scale(1.03)}}
.hl{position:relative;display:flex;align-items:center;gap:14px;margin-top:clamp(12px,1.6vw,22px);padding:16px;border-radius:22px;background:linear-gradient(120deg, color-mix(in srgb, var(--mint) 22%, var(--night-2)), var(--night-2) 65%);box-shadow:0 0 0 3px var(--mint);color:var(--text);text-decoration:none;overflow:hidden}
.hl .hlc{flex:0 0 auto;display:flex;align-items:flex-end;gap:5px}
.hl .hlc i{display:block;width:26px;height:30px;background:var(--gold);clip-path:polygon(50% 0, 100% 38%, 100% 100%, 0 100%, 0 38%)}
.hl .hlc i:nth-child(2){width:34px;height:40px;background:var(--mint)}
.hl .hlc i:nth-child(3){background:var(--red)}
.hl small{display:block;font-size:11px;font-weight:700;letter-spacing:.18em;color:var(--mint)}
.hl b{display:block;margin-top:4px;font-family:var(--display);font-weight:400;font-size:clamp(22px,6vw,34px);line-height:.95}
.hl b span{color:var(--gold)}
.hl p{margin:6px 0 0;font-size:12.5px;line-height:1.4;color:var(--muted)}
.hl em{flex:0 0 44px;height:44px;margin-left:auto;display:grid;place-items:center;border-radius:12px;background:var(--mint);color:var(--ink);font-style:normal;font-family:var(--display);font-size:20px}
.t-daily p{padding-right:0!important}
.menu .t-party,.menu .t-prize{min-height:0}
.menu .t-party h2,.menu .t-prize h2{font-size:clamp(28px,min(3.4vw,6vh),52px)}
.tile{position:relative;display:flex;flex-direction:column;gap:8px;justify-content:flex-end;min-height:clamp(150px,34vh,380px);padding:clamp(16px,2.4vh,28px);border-radius:22px;text-decoration:none;overflow:hidden;isolation:isolate;transition:transform .35s var(--ease-pop)}
.tile:hover,.tile:focus-visible{transform:translateY(-6px)}
.tile .k{position:absolute;top:clamp(14px,2vh,22px);left:clamp(16px,2.4vh,28px);right:clamp(16px,2.4vh,28px);display:flex;justify-content:space-between;align-items:center;gap:8px;font-size:11px;font-weight:700;letter-spacing:.18em}
.tile .k em{font-style:normal;padding:4px 8px;border-radius:6px}
.tile h2{margin:0;font-family:var(--display);font-weight:400;font-size:clamp(34px,min(4.4vw,7vh),68px);line-height:.88}
.tile p{margin:0;font-size:13px;font-weight:600;line-height:1.4;max-width:34ch;padding-right:56px}
.tile .go{position:absolute;right:clamp(16px,2.4vh,28px);bottom:clamp(16px,2.4vh,28px);display:grid;place-items:center;width:48px;height:48px;border-radius:50%;font-family:var(--display);font-size:22px}
.t-daily{background:var(--night-2);box-shadow:0 0 0 3px var(--gold), 0 0 50px color-mix(in srgb, var(--gold) 30%, transparent);color:var(--text)}
.t-daily::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(80% 70% at 85% 0%, color-mix(in srgb, var(--gold) 30%, transparent), transparent 70%)}
.t-daily .k{color:var(--mint)} .t-daily .k em{background:var(--text);color:var(--red)}
.t-daily h2 span{color:var(--gold)} .t-daily p{color:var(--muted)} .t-daily p b{color:var(--text)}
.t-daily .go{background:var(--gold);color:var(--ink)}
.t-party{background:var(--grape);box-shadow:0 0 0 3px var(--cup), 0 0 40px color-mix(in srgb, var(--cup) 35%, transparent);color:var(--text)}
.t-party::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(80% 60% at 20% 0%, color-mix(in srgb, var(--cup) 45%, transparent), transparent 70%)}
.t-party .k{color:var(--hi)} .t-party .k em{background:var(--hi);color:var(--ink)}
.t-party h2{text-shadow:4px 4px 0 var(--cup)} .t-party .go{background:var(--cup);color:var(--text)}
.t-prize{background:var(--lake);box-shadow:0 0 0 3px var(--mint), 0 0 40px color-mix(in srgb, var(--mint) 25%, transparent);color:var(--text)}
.t-prize::before{content:"";position:absolute;inset:0;z-index:-1;background:radial-gradient(70% 60% at 80% 10%, color-mix(in srgb, var(--amber) 30%, transparent), transparent 70%)}
.t-prize .k{color:var(--mint)} .t-prize .k em{background:var(--mint);color:var(--ink)}
.t-prize h2 span{color:var(--amber)} .t-prize .go{background:var(--mint);color:var(--ink)}
.chipsrow{display:flex;gap:6px;margin-bottom:2px}
.chipsrow i{display:grid;place-items:center;width:28px;height:28px;border-radius:8px;font-style:normal;font-family:var(--display);font-size:10px;color:var(--text);box-shadow:0 0 0 2px var(--lake)}
.forbrands{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:14px 16px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--muted) 30%, transparent);text-decoration:none}
.forbrands b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(16px,2vw,20px)}
.forbrands span{font-size:12px;font-weight:600;color:var(--muted)}
.forbrands em{flex:0 0 auto;font-style:normal;padding:10px 14px;border-radius:12px;background:var(--text);color:var(--ink);font-family:var(--display);font-size:14px}
.live{display:flex;flex-wrap:wrap;gap:8px}
.live[hidden]{display:none}
.live div{flex:1 1 260px;min-width:0;display:flex;flex-direction:column;gap:3px;padding:10px 14px;border-radius:14px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--gold)}
.live small{font-size:10px;font-weight:700;letter-spacing:.14em;color:var(--gold)}
.live b{font-family:var(--display);font-weight:400;font-size:clamp(16px,2vw,20px);line-height:1.15}
.live span{font-size:12px;font-weight:600;color:var(--muted)}
.suggest{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:12px 16px;border-radius:14px;background:var(--night-2);text-decoration:none;color:var(--text)}
.suggest b{font-family:var(--display);font-weight:400;font-size:clamp(15px,2vw,19px)}
.suggest span{font-size:12px;font-weight:600;color:var(--muted)}
.suggest em{flex:0 0 auto;font-style:normal;padding:9px 12px;border-radius:12px;background:var(--mint);color:var(--ink);font-family:var(--display);font-size:13px}
@media (max-width:860px){
  .menu{grid-template-columns:1fr 1fr;grid-template-rows:auto auto}
  .menu .t-daily{grid-column:1 / -1;grid-row:auto;min-height:0;padding-top:48px}
  .t-daily h2{font-size:clamp(52px,15vw,80px)}
  .menu .t-party,.menu .t-prize{padding:42px 14px 14px;min-height:112px}
  .menu .t-party p,.menu .t-prize p,.menu .t-party .go,.menu .t-prize .go,.menu .t-prize .chipsrow{display:none}
  .menu .t-party h2,.menu .t-prize h2{font-size:26px}
  .tile .k{left:14px;right:14px;top:14px;font-size:9.5px;letter-spacing:.12em}
  .tag{font-size:clamp(34px,10vw,52px)}
}
'''
chips = ''.join(f'<i style="background:{b["col"]}">{b["mono"]}</i>' for b in BRANDS[:5])
home_body = f'''<div class="bar"><div class="logo">OFF <span>CAMPUS</span></div><span class="school"><i></i>QUEEN'S</span></div>
<h1 class="tag">KNOW YOUR SCHOOL? <span>PROVE IT.</span></h1>
<nav class="menu" aria-label="Pick one">
  <a class="tile t-daily" href="daily.html"><div class="k"><span>QUEEN'S DAILY</span><em>NEW EVERY DAY</em></div>
    <h2>TODAY'S <span>FIVE</span></h2><p>Five quick rounds about Queen's. <b>Beat your friends. Play for your house.</b> New five in <b data-cd>--</b>.</p><span class="play">PLAY TODAY'S 5</span></a>
  <a class="tile t-party" href="party.html"><div class="k"><span>WITH YOUR FRIENDS</span><em>3 GAMES</em></div>
    <h2>PARTY GAMES</h2><p>For the pregame. Plug the laptop into the TV and play together.</p><span class="go" aria-hidden="true">&rarr;</span></a>
  <a class="tile t-prize" href="clubs.html"><div class="k"><span>FOR CLUBS</span><em>FREE</em></div>
    <h2>CLUB <span>GAMES</span></h2><p>Your club's own game. Guess how everyone answered.</p><span class="go" aria-hidden="true">&rarr;</span></a>
</nav>
<a class="hl" href="house.html"><span class="hlc" aria-hidden="true"><i></i><i></i><i></i></span><div><small>QUEEN'S HOUSE LEAGUE</small><b>YOUR HOUSE <span>VS EVERY HOUSE.</span></b><p>Everyone plays the Daily. Your house's average counts. Three players to enter.</p></div><em aria-hidden="true">&rarr;</em></a>
<div class="live" id="live" hidden></div>
<a class="suggest" href="daily.html?suggest"><div><b>GOT A QUESTION FOR QUEEN'S?</b><br><span>Suggest it. The best ones make the daily, with your @ on them.</span></div><em>SUGGEST</em></a>
<a class="forbrands" href="brands.html"><div><b>OWN A SPOT IN KINGSTON?</b><span>Get your business in front of Queen's students.</span></div><em>FOR BRANDS</em></a>'''
HOME_JS = '''<script>
(function(){
  var t = new URLSearchParams(location.search).get('api'), API = t && /^http:\\/\\/localhost:\\d+$/.test(t) ? t : '';
  if (!API && !/(^|\\.)offcampusontario\\.ca$|\\.netlify\\.app$/.test(location.hostname)) return;
  var esc = function(x){ return String(x).replace(/[&<>"]/g, function(c){ return { '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;' }[c]; }); };
  fetch(API + '/api/home').then(function(r){ return r.ok ? r.json() : null; }).then(function(d){
    if (!d) return; var h = '';
    if (d.crewOfWeek) h += '<div><small>CREW OF THE WEEK</small><b>' + esc(d.crewOfWeek.name) + '</b><span>' + d.crewOfWeek.players + ' playing · averaging ' + d.crewOfWeek.avg.toLocaleString('en-CA') + (d.max ? ' of ' + d.max.toLocaleString('en-CA') : '') + ' a day</span></div>';
    (d.closed || (d.yesterday ? [d.yesterday] : [])).forEach(function(y){   // closed questions only, 30+ real answers
      h += '<div><small>YESTERDAY · REAL ANSWERS</small><b>' + Math.round(100 * y.yes / y.n) + '% said yes</b><span>' + esc(y.q) + ' · ' + y.yes + ' of ' + y.n + ' Off Campus players who answered</span></div>'; });
    if (h) { var el = document.getElementById('live'); el.innerHTML = h; el.hidden = false; }
  }).catch(function(){});
})();
</script>'''
open(OUT + 'index.html', 'w').write(f'<title>Off Campus</title>\n<meta name="claude:viewport-fit-sides" content="cover">\n{FONTS}\n<style>{BASE_CSS}{home_css}</style>\n{BG}\n<main class="wrap">\n{home_body}\n{FOOT}\n</main>\n{COUNTDOWN_JS}\n{HOME_JS}\n')

# =============== PARTY GAMES ===============
cab_css = open(SP + '/site/cabinets.css').read()
cab_html = open(SP + '/site/cabinets.html').read()
grid = cab_html[cab_html.index('<section class="grid"'):cab_html.index('</section>') + len('</section>')]
party_css = '''
.cab{position:relative;display:flex;flex-direction:column;justify-content:space-between;gap:clamp(10px,1.6vh,18px);min-height:clamp(280px,46vh,520px);padding:clamp(18px,2.6vh,30px);border-radius:clamp(18px,2.4vh,28px);
  text-decoration:none;color:inherit;overflow:hidden;isolation:isolate;transition:transform .35s var(--ease-pop), box-shadow .35s;outline:none}
.cab:focus-visible,.cab:hover{transform:translateY(-8px) scale(1.015)}
.cab .art{position:absolute;inset:0;z-index:-1}
.cab .top{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.cab .num{font-family:var(--display);font-size:clamp(14px,2vh,20px);opacity:.75}
.cab .who{font-size:clamp(11px,1.5vh,14px);font-weight:700;letter-spacing:.14em;padding:6px 10px;border-radius:999px;white-space:nowrap}
.cab h2{margin:0;line-height:.9;text-wrap:balance}
.cab p{margin:0;font-size:clamp(13px,1.8vh,17px);line-height:1.35;font-weight:600;max-width:34ch}
.cab .play{align-self:flex-start;display:inline-flex;align-items:center;gap:10px;padding:clamp(10px,1.5vh,14px) clamp(18px,1.6vw,24px);border-radius:14px;font-family:var(--display);font-size:clamp(16px,2.4vh,26px);letter-spacing:.03em}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:clamp(14px,1.8vw,26px)}
.howto{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0;padding:0;list-style:none;counter-reset:st}
.howto li{counter-increment:st;display:flex;gap:10px;align-items:center;padding:12px;border-radius:14px;background:var(--night-2);font-size:13px;font-weight:600;line-height:1.35}
.howto li::before{content:counter(st);flex:0 0 auto;display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--cup);font-family:var(--display);font-size:16px;color:var(--text)}
.ph{font-family:var(--marquee);font-weight:400;color:var(--text);text-shadow:0 4px 0 var(--cup)}
@media (max-width:900px){ .grid,.howto{grid-template-columns:1fr} .cab{min-height:250px} }
''' + cab_css.replace('font-size:clamp(34px,min(3.3vw,6.6vh),84px)', 'font-size:clamp(30px,min(3vw,6vh),60px)').replace('font-size:clamp(60px,min(6.4vw,11vh),150px)', 'font-size:clamp(54px,min(5.4vw,10vh),112px)').replace('font-size:clamp(60px,min(6vw,11vh),150px)', 'font-size:clamp(54px,min(5.2vw,10vh),112px)')
party_body = f'''{tabs('party')}
<div class="kick">PLAY THESE WITH YOUR FRIENDS</div>
<h1 class="h1 ph">PARTY GAMES</h1>
<ol class="howto"><li>Plug a laptop into the TV, or everyone huddles round a phone</li><li>Turn the sound up and pick a game</li><li>Teams, pointing, yelling. Friendships not guaranteed.</li></ol>
{grid}'''
open(OUT + 'party.html', 'w').write(subpage('Off Campus Party Games', party_css, party_body))

# =============== PRIZES ===============
prize_css = '''
.howwin{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:0;padding:0;list-style:none;counter-reset:st}
.howwin li{counter-increment:st;padding:12px;border-radius:14px;background:var(--night-2);font-size:12.5px;font-weight:600;line-height:1.35}
.howwin li::before{content:counter(st);display:block;font-family:var(--display);font-size:20px;color:var(--gold);margin-bottom:2px}
.jack{display:flex;gap:16px;align-items:center;padding:18px;border-radius:20px;background:var(--gold);color:var(--ink);box-shadow:0 7px 0 var(--gold-deep)}
.jack .star{flex:0 0 auto;display:grid;place-items:center;width:64px;height:64px;border-radius:16px;background:var(--ink);color:var(--gold);font-family:var(--display);font-size:30px}
.jack small{display:block;font-size:11px;font-weight:700;letter-spacing:.2em}
.jack b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(20px,2.6vw,28px);line-height:1.05}
.jack span{display:block;font-size:12.5px;font-weight:600;margin-top:4px}
.spots{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,330px),1fr));gap:12px}
.spot{display:flex;flex-direction:column;gap:12px;padding:16px;border-radius:20px;background:var(--cream);color:var(--ink)}
.spot .hd{display:flex;align-items:center;gap:12px}
.spot .lg{flex:0 0 auto;display:grid;place-items:center;width:52px;height:52px;border-radius:14px;font-family:var(--display);font-size:20px;color:var(--text)}
.spot h3{margin:0;font-family:var(--tall);font-weight:900;font-size:24px;line-height:1;text-transform:uppercase}
.spot .kind{font-size:11px;font-weight:700;letter-spacing:.1em;color:color-mix(in srgb, var(--ink) 60%, transparent)}
.spot .sz{margin-left:auto;align-self:flex-start;font-size:10px;font-weight:700;letter-spacing:.1em;padding:4px 7px;border-radius:6px;background:var(--ink);color:var(--gold);white-space:nowrap}
.spot ul{margin:0;padding:0;list-style:none;display:grid;gap:6px}
.spot li{display:flex;justify-content:space-between;align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:color-mix(in srgb, var(--ink) 7%, transparent);font-size:13.5px;font-weight:700}
.spot li em{flex:0 0 auto;font-style:normal;font-size:10px;letter-spacing:.14em;padding:3px 7px;border-radius:5px;background:var(--ink);color:var(--cream)}
.spot li.big{background:var(--gold)}
.spot li.big em{background:var(--red);color:var(--text)}
.spot .link{min-height:46px;border-radius:12px;border:2px dashed color-mix(in srgb, var(--ink) 35%, transparent);font-size:12px;font-weight:700;letter-spacing:.06em;color:color-mix(in srgb, var(--ink) 70%, transparent)}
.cta2{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap;padding:18px;border-radius:20px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--gold)}
.cta2 b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(18px,2.4vw,26px)}
.cta2 span{font-size:13px;font-weight:600;color:var(--muted)}
@media (max-width:760px){ .howwin{grid-template-columns:1fr 1fr} }
'''
def spot_card(b):
    size = 'COMES UP MOST' if b['slice'] >= 1.5 else 'COMES UP MORE' if b['slice'] > 1 else ''
    return f'''<article class="spot"><div class="hd"><span class="lg" style="background:{b["col"]}">{b["mono"]}</span><div><h3>{e(b["name"])}</h3><div class="kind">{e(b["kind"].upper())}</div></div>{f'<span class="sz">{size}</span>' if size else ''}</div>
  <ul><li>{e(b["small"])}<em>MOST SPINS</em></li><li class="big">{e(b["big"])}<em>BIG WIN</em></li></ul>
  <button class="link" onclick="ocToast('THEIR SITE + INSTAGRAM GO HERE')">THEIR WEBSITE + INSTAGRAM GO HERE</button></article>'''
TEASE = [('FREE','COFFEE','#C8782A'),('BOGO','COOKIES','#E8608A'),('20%','ESCAPE ROOMS','#6C4BE0'),('VIP','NIGHTS OUT 19+','#B03BD1'),('FREE','CLIMBING','#3E8E5A'),('15%','MERCH','#2E5BD8')]
tease = ''.join(f'<div class="tz" style="background:{c}"><b>{m}</b><span>{t}</span></div>' for m, t, c in TEASE)
prize_css += """
.tzs{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}
.tz{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:6px;height:120px;border-radius:18px;color:var(--text);text-align:center;padding:0 6px}
.tz b{font-family:var(--display);font-weight:400;font-size:30px;line-height:1}
.tz span{font-family:var(--display);font-size:12px;letter-spacing:.03em}
.soon{display:flex;flex-direction:column;gap:12px;padding:20px;border-radius:20px;background:var(--night-2);box-shadow:inset 0 0 0 3px var(--gold)}
.soon b{font-family:var(--display);font-weight:400;font-size:clamp(22px,3vw,30px);line-height:1}
.soon p{margin:0;font-size:14px;font-weight:600;line-height:1.5;color:var(--muted)}
@media (max-width:420px){ .tzs{grid-template-columns:1fr 1fr} }
"""
prize_body = f'''{tabs('prizes')}
<div class="kick">QUEEN'S · PRESEASON</div>
<h1 class="h1">PRIZES <span>DROP SOON</span></h1>
<p class="lede">The prize spin is almost here. Score {UNLOCK} in today's five and you'll spin for free stuff from Kingston spots. Here's the kind of thing that'll be on it:</p>
<section class="tzs" aria-label="Coming soon">{tease}</section>
<div class="jack"><span class="star">★</span><div><small>WEEKLY JACKPOT</small><b>A big one every week</b><span>On the spinner every day. Post your win, tag the spot, and we double it.</span></div></div>
<ol class="howwin"><li>Play today's five</li><li>Score {UNLOCK} out of 5,000</li><li>Spin for a spot, then spin for your prize</li><li>Show your code at the counter</li></ol>
<div class="soon"><b>BE FIRST WHEN IT DROPS</b><p>Follow us on Instagram and we'll post the second the prize wheel goes live.</p><a class="btn" href="https://instagram.com/offcampuskingston" target="_blank" rel="noopener">FOLLOW US ON INSTAGRAM</a></div>
<div class="cta2"><div><b>OWN A SPOT IN KINGSTON?</b><span>Get your business on the spinner. First month free.</span></div><a class="btn" href="brands.html">FOR BRANDS &rarr;</a></div>'''
open(OUT + 'prizes.html', 'w').write(subpage('Off Campus Prizes', prize_css, prize_body))

# =============== FOR BRANDS (its own file) ===============
exec(open(SP + '/site/brands_page.py').read())
print('built')

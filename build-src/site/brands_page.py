# The "For Brands" landing page. Run through site.py (uses its FONTS, BASE_CSS, BG, BRANDS, CONTACT, UNLOCK, e, OUT).
# Personal link for a business: brands.html?spot=Name&offer=15%25%20off&big=A%20free%20latte&col=C8782A&kind=Coffee

b_css = '''
.ints{border:0;margin:0;padding:0;display:grid;gap:8px}.ints legend{font-size:11px;font-weight:700;letter-spacing:.16em;margin-bottom:6px}.ck{display:flex!important;flex-direction:row!important;gap:10px;align-items:flex-start;font-size:13px;line-height:1.4;font-weight:600;letter-spacing:0!important;text-transform:none}.ck input{width:20px!important;height:20px!important;min-height:0!important;margin:2px 0 0;flex:0 0 auto;accent-color:#3BD67A}.ck b{font-weight:800}
html{overflow-x:clip}
.wrap{max-width:1120px;gap:0;padding-block:0 28px}
section{padding:clamp(34px,6vh,64px) 0}
.bb{position:sticky;top:0;z-index:30;display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 0;background:color-mix(in srgb, var(--night) 88%, transparent);-webkit-backdrop-filter:blur(8px);backdrop-filter:blur(8px)}
.bb .logo{font-family:var(--display);font-size:20px;line-height:1;text-decoration:none}
.bb .logo span{color:var(--gold)}
.bb .logo small{display:block;font-family:var(--mono);font-size:9.5px;font-weight:700;letter-spacing:.2em;color:var(--mint);margin-top:3px}
.bb .try{display:inline-flex;align-items:center;min-height:42px;padding:0 14px;border-radius:12px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--gold);font-family:var(--display);font-size:13px;letter-spacing:.03em;text-decoration:none;white-space:nowrap}
.kick{font-size:11.5px}
h2.h{margin:0 0 10px;font-family:var(--display);font-weight:400;font-size:clamp(30px,4.4vw,52px);line-height:.95;text-wrap:balance}
h2.h span{color:var(--gold)}
.sub{margin:0 0 22px;font-size:clamp(14px,1.7vw,17px);line-height:1.55;font-weight:600;color:var(--muted);max-width:60ch}
.sub b{color:var(--text)}
/* hero */
.hero{display:grid;grid-template-columns:1.25fr .75fr;gap:clamp(20px,4vw,56px);align-items:center;padding-top:clamp(18px,4vh,40px)}
.hero h1{margin:10px 0 14px;font-family:var(--display);font-weight:400;font-size:clamp(36px,5.4vw,70px);line-height:.92;text-wrap:balance}
.hero .sub+.sub{margin-top:-8px}
.hero .sub em{font-style:normal;color:var(--gold)}
.hero h1 span{color:var(--gold);text-shadow:0 0 30px color-mix(in srgb, var(--gold) 45%, transparent)}
.ctas{display:flex;flex-wrap:wrap;gap:12px;margin-top:6px}
.ctas .btn{flex:1 1 250px;white-space:nowrap;font-size:clamp(15px,1.5vw,18px)}
.btn.alt{background:var(--night-2);color:var(--text);box-shadow:inset 0 0 0 2px var(--text)}
.btn.alt:active{box-shadow:inset 0 0 0 2px var(--text)}
.trust{display:flex;flex-wrap:wrap;gap:6px 16px;margin-top:16px;font-size:12px;font-weight:700;color:var(--mint)}
.trust span::before{content:"✓ ";color:var(--good)}
.mine{display:none;margin-bottom:12px;padding:8px 12px;border-radius:10px;background:var(--cream);color:var(--ink);font-size:12px;font-weight:700;letter-spacing:.06em;width:max-content;max-width:100%}
.is-mine .mine{display:block}
/* phone */
.phone{justify-self:center;width:250px;height:500px;border-radius:40px;padding:12px;background:#000;box-shadow:0 0 0 2px #2a2740, 0 30px 80px color-mix(in srgb, var(--gold) 18%, transparent);position:relative}
.screen{position:relative;width:100%;height:100%;border-radius:30px;overflow:hidden;background:var(--night-2);display:flex;flex-direction:column;align-items:center;gap:12px;padding:40px 0 0}
.screen .t{font-family:var(--display);font-size:20px;color:var(--gold);letter-spacing:.02em}
.screen .s{font-size:10px;font-weight:700;letter-spacing:.16em;color:var(--mint)}
.mreel{position:relative;width:100%;height:96px;overflow:hidden;background:var(--night);box-shadow:inset 0 2px 0 var(--gold-deep), inset 0 -2px 0 var(--gold-deep)}
.mstrip{position:absolute;left:0;top:8px;display:flex;gap:6px;animation:roll 7s infinite}
.mc{flex:0 0 70px;height:80px;border-radius:10px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;color:var(--text);text-align:center}
.mc b{font-family:var(--display);font-weight:400;font-size:20px;line-height:1}
.mc span{font-family:var(--display);font-size:7.5px;letter-spacing:.02em;line-height:1.1;padding:0 3px}
.mc.jp{background:var(--gold);color:var(--ink)}
.mmark{position:absolute;left:50%;top:0;bottom:0;width:3px;margin-left:-1.5px;background:var(--red);box-shadow:0 0 10px var(--red);z-index:2}
@keyframes roll{0%{transform:translateX(0);animation-timing-function:cubic-bezier(.12,.75,.2,1)}42%,100%{transform:translateX(var(--end))}}
.mwin{position:absolute;left:12px;right:12px;bottom:18px;display:flex;flex-direction:column;gap:6px;padding:14px;border-radius:16px;background:var(--cream);color:var(--ink);animation:winin 7s infinite}
@keyframes winin{0%,46%{opacity:0;transform:translateY(16px)}52%,93%{opacity:1;transform:none}100%{opacity:0}}
.mwin small{font-size:9px;font-weight:700;letter-spacing:.16em;color:var(--red)}
.mwin b{font-family:var(--display);font-weight:400;font-size:19px;line-height:1.05}
.mwin span{font-size:10.5px;font-weight:700;color:color-mix(in srgb, var(--ink) 65%, transparent)}
.mwin i{display:block;margin-top:4px;padding:8px;border-radius:10px;background:var(--ink);color:var(--hi);font-style:normal;font-family:var(--display);font-size:16px;text-align:center;letter-spacing:.08em}
/* numbers */
.nums{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.num{padding:18px 16px;border-radius:18px;background:var(--cream);color:var(--ink)}
.num b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(28px,3.6vw,44px);line-height:1}
.num span{display:block;margin-top:8px;font-size:12.5px;font-weight:700;line-height:1.35}
.src{margin:10px 0 0;font-size:10.5px;color:var(--muted);line-height:1.5}
.src a{color:var(--muted)}
/* problem / fix */
.vs2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.col{padding:20px;border-radius:20px;background:var(--night-2)}
.col h3{margin:0 0 12px;font-family:var(--display);font-weight:400;font-size:20px}
.col ul{margin:0;padding:0;list-style:none;display:grid;gap:10px}
.col li{display:flex;gap:10px;font-size:14px;font-weight:600;line-height:1.45;color:var(--muted)}
.col li b{color:var(--text)}
.col li::before{flex:0 0 auto;display:grid;place-items:center;width:24px;height:24px;border-radius:7px;font-family:var(--display);font-size:13px}
.col.bad li::before{content:"✕";background:color-mix(in srgb, var(--red) 25%, transparent);color:var(--red)}
.col.good{box-shadow:inset 0 0 0 2px var(--good)}
.col.good li::before{content:"✓";background:var(--good);color:var(--ink)}
/* steps */
.steps4{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:0;padding:0;list-style:none;counter-reset:st}
.steps4 li{counter-increment:st;padding:16px;border-radius:18px;background:var(--night-2);font-size:13.5px;font-weight:600;line-height:1.45;color:var(--muted)}
.steps4 li b{display:block;color:var(--text);font-family:var(--display);font-weight:400;font-size:18px;margin-bottom:6px}
.steps4 li::before{content:counter(st);display:grid;place-items:center;width:36px;height:36px;border-radius:10px;background:var(--gold);color:var(--ink);font-family:var(--display);margin-bottom:12px}
/* everything we do */
.perks{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.perk{display:flex;flex-direction:column;gap:8px;padding:18px;border-radius:20px;background:var(--night-2);box-shadow:inset 0 0 0 1.5px var(--night-3)}
.perk .ic{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;font-family:var(--display);font-size:18px;color:var(--ink)}
.perk h3{margin:0;font-family:var(--display);font-weight:400;font-size:18px;line-height:1.1}
.perk p{margin:0;font-size:13.5px;line-height:1.5;font-weight:600;color:var(--muted)}
.perk p b{color:var(--text)}
.perk.star{background:var(--gold);color:var(--ink);box-shadow:none}
.perk.star p{color:color-mix(in srgb, var(--ink) 75%, transparent)} .perk.star p b{color:var(--ink)}
.perk.star .ic{background:var(--ink);color:var(--gold)}
/* offers */
.offers{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.offer{display:flex;flex-direction:column;gap:8px;padding:18px;border-radius:20px;background:var(--cream);color:var(--ink)}
.offer small{font-size:10.5px;font-weight:700;letter-spacing:.16em;color:color-mix(in srgb, var(--ink) 60%, transparent)}
.offer b{font-family:var(--display);font-weight:400;font-size:20px;line-height:1.05}
.offer p{margin:0;font-size:13px;font-weight:600;line-height:1.45}
.offer em{margin-top:auto;font-style:normal;font-size:11px;font-weight:700;letter-spacing:.06em;padding:6px 8px;border-radius:8px;background:color-mix(in srgb, var(--ink) 8%, transparent);width:max-content;max-width:100%}
.offer.hot{background:var(--hi)}
.note{margin:14px 0 0;padding:14px 16px;border-radius:16px;background:var(--night-2);font-size:13.5px;font-weight:600;line-height:1.5;color:var(--muted)}
.note b{color:var(--gold)}
/* control */
.ctrl{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:0;padding:0;list-style:none}
.ctrl li{display:flex;gap:12px;align-items:flex-start;padding:16px;border-radius:18px;background:var(--night-2);font-size:13.5px;font-weight:600;line-height:1.45;color:var(--muted)}
.ctrl li b{display:block;color:var(--text);font-size:14.5px}
.ctrl li::before{content:"✓";flex:0 0 auto;display:grid;place-items:center;width:28px;height:28px;border-radius:8px;background:var(--good);color:var(--ink);font-family:var(--display);font-size:14px}
/* dashboard */
.dash{padding:20px;border-radius:22px;background:var(--cream);color:var(--ink);box-shadow:0 8px 0 var(--gold-deep)}
.dash .top{display:flex;justify-content:space-between;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:16px}
.dash .who{display:flex;align-items:center;gap:10px}
.dash .who i{display:grid;place-items:center;width:44px;height:44px;border-radius:12px;color:var(--text);font-style:normal;font-family:var(--display);font-size:16px}
.dash .who b{font-family:var(--tall);font-weight:900;font-size:24px;text-transform:uppercase;line-height:1}
.dash .who span{display:block;font-size:11px;font-weight:700;letter-spacing:.1em;color:color-mix(in srgb, var(--ink) 60%, transparent)}
.dash .tag{font-size:10px;font-weight:700;letter-spacing:.14em;padding:5px 8px;border-radius:6px;background:var(--ink);color:var(--gold)}
.kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}
.kpi{padding:12px;border-radius:14px;background:color-mix(in srgb, var(--ink) 7%, transparent)}
.kpi small{display:block;font-size:10.5px;font-weight:700;letter-spacing:.06em;line-height:1.3;color:color-mix(in srgb, var(--ink) 65%, transparent);min-height:2.6em}
.kpi b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(24px,3vw,34px);line-height:1.1;font-variant-numeric:tabular-nums}
.kpi.hot{background:var(--ink);color:var(--gold)} .kpi.hot small{color:var(--stone)}
.week{display:grid;grid-template-columns:repeat(7,1fr);gap:8px;align-items:end;height:120px;margin-top:16px}
.week div{display:flex;flex-direction:column;align-items:center;justify-content:flex-end;gap:4px;height:100%;font-size:10px;font-weight:700;color:color-mix(in srgb, var(--ink) 60%, transparent)}
.week i{width:100%;border-radius:6px 6px 2px 2px;background:var(--ink)}
.week div:nth-child(5) i,.week div:nth-child(6) i{background:var(--red)}
.week em{font-style:normal;font-family:var(--display);font-size:12px;color:var(--ink)}
.dash .foot{margin:12px 0 0;font-size:11px;color:color-mix(in srgb, var(--ink) 60%, transparent)}
/* categories */
.cats{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}
.cat{display:flex;justify-content:space-between;align-items:center;gap:8px;padding:16px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--night-3);font-family:var(--display);font-size:15px}
.cat em{font-style:normal;font-family:var(--mono);font-size:10px;font-weight:700;letter-spacing:.12em;padding:4px 7px;border-radius:6px;background:var(--good);color:var(--ink)}
/* founding deal */
.deal{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.deal .free{padding:24px;border-radius:22px;background:var(--good);color:var(--ink)}
.deal .free small{font-size:11px;font-weight:700;letter-spacing:.2em}
.deal .free b{display:block;margin:8px 0;font-family:var(--display);font-weight:400;font-size:clamp(34px,4.6vw,56px);line-height:.92}
.deal .free p{margin:0;font-size:14px;font-weight:600;line-height:1.5}
.deal ul{margin:0;padding:24px;border-radius:22px;background:var(--night-2);list-style:none;display:grid;gap:12px;align-content:start}
.deal li{display:flex;gap:10px;font-size:14px;font-weight:600;line-height:1.45;color:var(--muted)}
.deal li b{color:var(--text)}
.deal li::before{content:"★";flex:0 0 auto;color:var(--gold);font-size:16px}
/* x2 */
.x2{display:grid;grid-template-columns:auto 1fr;gap:20px;align-items:center;padding:24px;border-radius:22px;background:var(--hi);color:var(--ink)}
.x2 .big{font-family:var(--display);font-size:clamp(56px,8vw,96px);line-height:.8}
.x2 b{display:block;font-family:var(--display);font-weight:400;font-size:clamp(22px,2.8vw,32px);line-height:1}
.x2 p{margin:8px 0 0;font-size:14px;font-weight:600;line-height:1.5}
/* faq */
.faq{display:grid;gap:8px}
.faq details{border-radius:16px;background:var(--night-2)}
.faq summary{cursor:pointer;list-style:none;display:flex;justify-content:space-between;align-items:center;gap:12px;min-height:56px;padding:0 18px;font-family:var(--display);font-size:16px}
.faq summary::-webkit-details-marker{display:none}
.faq summary::after{content:"+";font-size:22px;color:var(--gold);transition:transform .25s var(--ease-out)}
.faq details[open] summary::after{transform:rotate(45deg)}
.faq details p{margin:0;padding:0 18px 18px;font-size:14px;font-weight:600;line-height:1.55;color:var(--muted);max-width:70ch}
/* join */
.join{display:grid;grid-template-columns:1fr 1fr;gap:clamp(16px,3vw,40px);align-items:start;padding:clamp(22px,4vw,40px);border-radius:26px;background:var(--night-2);box-shadow:0 0 0 3px var(--gold), 0 0 60px color-mix(in srgb, var(--gold) 22%, transparent)}
.join h2{margin:0 0 10px;font-family:var(--display);font-weight:400;font-size:clamp(30px,4.4vw,52px);line-height:.95}
.join h2 span{color:var(--gold)}
form{display:grid;gap:10px}
label{display:grid;gap:6px;font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--muted)}
input,select,textarea{box-sizing:border-box;width:100%;min-height:50px;padding:12px 14px;border:0;border-radius:12px;background:var(--cream);color:var(--ink);font:600 15px var(--mono)}
textarea{min-height:90px;resize:vertical}
form .btn{width:100%;border:0;cursor:pointer}
.dm{margin:4px 0 0;font-size:13px;font-weight:600;color:var(--muted)}
.dm a{color:var(--gold)}
@media (max-width:900px){
  .hero,.vs2,.deal,.join{grid-template-columns:1fr}
  .phone{transform:scale(.86);margin:-30px 0 -50px}
  .perk{display:grid;grid-template-columns:44px 1fr;column-gap:12px;row-gap:4px;padding:14px}
  .perk .ic{grid-row:1 / span 2}
  .perk h3{align-self:end}
  .nums,.offers,.cats{grid-template-columns:1fr 1fr}
  .perks,.ctrl{grid-template-columns:1fr 1fr}
  .steps4{grid-template-columns:1fr 1fr}
  .kpis{grid-template-columns:1fr 1fr} .kpi.hot{grid-column:1 / -1}
}
@media (max-width:560px){ .perks,.ctrl,.steps4,.offers{grid-template-columns:1fr} .x2{grid-template-columns:1fr;gap:6px} }
.nums>*,.offers>*,.cats>*,.perks>*,.ctrl>*,.steps4>*,.kpis>*,.vs2>*,.deal>*,.join>*{min-width:0}
'''

sample = BRANDS[3]   # Limestone Bean Co., used when no personal link is given
days = [('MON', 6), ('TUE', 8), ('WED', 9), ('THU', 13), ('FRI', 17), ('SAT', 14), ('SUN', 7)]
mx = max(v for _, v in days)
week = ''.join(f'<div><em>{v}</em><i style="height:{v / mx * 78:.0f}%"></i>{d}</div>' for d, v in days)
reel_cards = BRANDS + BRANDS[:4] + [sample] + BRANDS[5:8]   # 16 cards; the 4th from the end (the sample) is where it stops
reel_pool = ''.join(f'<div class="mc" style="background:{b["col"]}"><b>{b["mono"]}</b><span>{e(b["name"].upper())}</span></div>' for b in reel_cards)

PERKS = [
  ('star', '1', 'A spot on the daily spinner', 'Every student who unlocks a spin sees your <b>name, logo and offer</b> fly past, every single day.'),
  ('', '2', 'Your own card on the Prizes page', 'What you give, plus buttons to <b>your website and Instagram</b>. Every click is counted for you.'),
  ('', '3', 'A round all about you', 'Once a month the daily features you: a Survey Showdown board like <b>"Name a drink at your spot"</b>, or your storefront as the Drop the Pin photo, so students learn exactly where you are.'),
  ('', '4', 'Winners post you', 'Winners who <b>post their prize and tag you</b> will get it doubled. Real students putting your spot on their story, in front of their friends.'),
  ('', '5', 'Instagram and TikTok features', 'On <b>@offcampuskingston</b>: a launch post with every founding partner, a "Spot of the Week" feature, and winner shoutouts.'),
  ('', '6', 'Ask Queen\'s anything', 'Thinking about a new item or new hours? We put your question in a round and send you <b>real answers from Queen\'s students</b>.'),
  ('', '7', 'The January Cup', 'Queen\'s vs Western, the big event we\'re planning. Founding partners are on <b>the prizes and the promo</b>.'),
  ('', '8', 'A counter card', 'A print-ready QR card for your counter. Customers play while they wait, and <b>come back to use what they win</b>.'),
  ('', '9', 'A weekly report', 'How many students <b>landed on you, clicked, won a code and walked in</b>. Plain numbers, every week.'),
]
perk_cols = ['var(--gold)', 'var(--mint)', 'var(--pin)', 'var(--hi)', 'var(--mint)', 'var(--amber)', 'var(--red)', 'var(--mint)', 'var(--gold)']
perks = ''.join(f'<div class="perk {k}"><span class="ic" style="background:{perk_cols[i] if k != "star" else "var(--ink)"}">{n}</span><h3>{t}</h3><p>{d}</p></div>' for i, (k, n, t, d) in enumerate(PERKS))

FAQ = [
  ('What does it cost?', 'Your first month is free; you only cover the prizes students win. After that it\'s a flat monthly fee that we set together with founding partners, and founding partners keep the best rate. We never take a cut of your sales.'),
  ('Do I need an app, a tablet or any tech?', 'No. Students will show the code on their phone. Your staff look at it, check the live clock is ticking (so it isn\'t a screenshot), and tap redeem. That\'s it.'),
  ('What stops people from cheating?', 'Each code will work once, one per student, with a live clock so a screenshot won\'t pass. You\'ll also set a weekly cap, so you never give out more than you planned.'),
  ('What if too many students show up?', 'You set how many codes go out each week and which days and hours they work. When they\'re gone, your spot rests until next week.'),
  ('Will this just bring in bargain hunters who never come back?', 'That\'s the big problem with coupon sites, and why we built this differently. Students earn your offer by playing a game about their school, it\'s a daily game, so they can see you every day, and the best offers are "free with purchase" or slow-hour deals that bring in paying customers. Your weekly report shows how many come in.'),
  ('Who plays?', 'Queen\'s students. The game is about Queen\'s, made for Queen\'s, and promoted through Queen\'s student channels. We launch at Queen\'s in January.'),
  ('Can I change my offer or stop?', 'Anytime. No contract. Message us and it\'s changed the same day.'),
  ('Who\'s behind Off Campus?', 'Josh Crane, building games for Ontario university students, starting with Queen\'s. Message him directly on Instagram at @offcampuskingston.'),
]
faq = ''.join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in FAQ)

cats = ''.join(f'<div class="cat">{c}<em>OPEN</em></div>' for c in ['COFFEE + CAFÉ', 'FOOD + TAKEOUT', 'BAR + CLUB (19+)', 'FITNESS + STUDIOS', 'ACTIVITIES', 'BEAUTY + HAIR', 'CLOTHING + MERCH', 'STUDENT SERVICES'])

ig = 'https://ig.me/m/offcampuskingston'
b_body = f'''<header class="bb"><a class="logo" href="./">OFF <span>CAMPUS</span><small>FOR KINGSTON BUSINESSES</small></a><a class="try" id="try2" href="daily.html">TRY THE GAME &rarr;</a></header>

<section class="hero">
  <div>
    <div class="mine" id="mine">MADE FOR YOUR SPOT</div>
    <div class="kick">FOUNDING PARTNERS · LAUNCHING AT QUEEN'S IN JANUARY</div>
    <h1>GIVE US YOUR STUDENT DEAL AND A FEW PRIZES. <span>WE'LL PUT YOUR SPOT IN FRONT OF QUEEN'S STUDENTS.</span></h1>
    <p class="sub">All we need from you is the student deal you already offer (or any deal that's worth it to you), plus a few free prizes now and then. <b>That's it.</b></p>
    <p class="sub">In return, Off Campus will put your business in front of Queen's students, inside a daily game they choose to play. They play, they win your deal, and they walk in to use it. <b>A flyer gets ignored and a coupon gets forgotten, but a prize someone <em>won</em> gets claimed.</b></p>
    <div class="ctas"><a class="btn" href="#join">CLAIM A FOUNDING SPOT</a><a class="btn alt" id="try" href="daily.html">SEE YOUR SPOT IN THE GAME &rarr;</a></div>
    <div class="trust"><span>First month free</span><span>No commission</span><span>No contract</span><span>No tech needed</span></div>
  </div>
  <div class="phone" aria-hidden="true"><div class="screen">
    <div class="s">SPIN 1 OF 2</div><div class="t">PICK YOUR SPOT</div>
    <div class="mreel"><div class="mstrip" id="mstrip">{reel_pool}</div><div class="mmark"></div></div>
    <div class="mwin"><small>YOU WON!</small><b id="mOffer">{e(sample["big"])}</b><span id="mName">at {e(sample["name"])}</span><i>OC-7K2Q</i></div>
  </div></div>
</section>

<section>
  <div class="kick">THE MARKET ON YOUR DOORSTEP</div>
  <h2 class="h">KINGSTON'S BIGGEST CROWD IS <span>RIGHT HERE.</span></h2>
  <div class="nums">
    <div class="num"><b>28,561</b><span>full-time students at Queen's this year</span></div>
    <div class="num"><b>5,477</b><span>new first-years every fall who haven't picked their spots yet</span></div>
    <div class="num"><b>$237M</b><span>spent by Queen's students in Kingston every year</span></div>
    <div class="num"><b>85%</b><span>of Gen Z are more likely to shop where there's a student deal</span></div>
  </div>
  <p class="src">Sources: <a href="https://www.queensu.ca/gazette/stories/queen-s-2025-26-enrolment-report-highlights-academic-strength-diversity-and-success" target="_blank" rel="noopener">Queen's 2025-26 enrolment report</a> · <a href="https://www.queensu.ca/gazette/stories/queens-economic-and-social-impact" target="_blank" rel="noopener">Deloitte impact study for Queen's (2022)</a> · <a href="https://wearepion.com/blog-posts/7-reasons-why-your-brand-should-offer-a-student-discount" target="_blank" rel="noopener">Pion (Student Beans) Gen Z research</a></p>
</section>

<section>
  <div class="kick">WHY THIS IS DIFFERENT</div>
  <h2 class="h">REACHING STUDENTS IS HARD. <span>WE MADE IT A GAME.</span></h2>
  <div class="vs2">
    <div class="col bad"><h3>What usually happens</h3><ul>
      <li><span><b>Flyers and posters</b> get walked past.</span></li>
      <li><span><b>Instagram ads</b> get skipped in half a second.</span></li>
      <li><span><b>Coupon sites</b> send one-time bargain hunters and take a cut of every sale.</span></li></ul></div>
    <div class="col good"><h3>With Off Campus</h3><ul>
      <li><span>Students <b>earn your offer by playing</b>, so it feels like a win, not an ad.</span></li>
      <li><span>It's a <b>new game every day</b>, so your name can be in front of them every day.</span></li>
      <li><span><b>You set the offer and the limits</b>, and we never take a cut.</span></li></ul></div>
  </div>
</section>

<section>
  <div class="kick">HOW IT WORKS</div>
  <h2 class="h">FOUR STEPS. <span>ZERO WORK FOR YOU.</span></h2>
  <ol class="steps4">
    <li><b>You pick an offer</b>Start with the student deal you already give. Add a bigger prize if you want to be seen more.</li>
    <li><b>Students play the daily</b>Five rounds about Queen's. From launch, a high score unlocks the prize spin.</li>
    <li><b>They land on you</b>Spin one picks the spot, spin two reveals your prize. Your name front and centre.</li>
    <li><b>They walk in</b>They show the code at your counter, staff tap redeem, done. You see it in your weekly report.</li>
  </ol>
</section>

<section>
  <div class="kick">EVERYTHING YOU GET</div>
  <h2 class="h">MORE THAN A DISCOUNT. <span>WE MAKE YOU KNOWN.</span></h2>
  <p class="sub">Getting students in the door is the start. Here's every way Off Campus puts your spot in front of Queen's.</p>
  <div class="perks">{perks}</div>
</section>

<section>
  <div class="kick">WHAT TO OFFER</div>
  <h2 class="h">START WITH WHAT YOU <span>ALREADY GIVE.</span></h2>
  <div class="offers">
    <div class="offer"><small>EASIEST</small><b>Your student discount</b><p>The 10 or 15% you already give. Now students actually hear about it.</p><em>COSTS YOU: NOTHING NEW</em></div>
    <div class="offer"><small>SMART</small><b>Free with purchase</b><p>A free cookie with any coffee, a free side with any meal. They still pay for the main thing.</p><em>COSTS YOU: PENNIES</em></div>
    <div class="offer"><small>FILL QUIET HOURS</small><b>A slow-hour deal</b><p>Only works Monday to Wednesday, 2 to 5. Turn your emptiest hours into your busiest.</p><em>COSTS YOU: EMPTY SEATS</em></div>
    <div class="offer hot"><small>GETS POSTED</small><b>A big prize, a few a week</b><p>A free room for 4, two free entries, a free crewneck. You pick how many. This is what students screenshot and share.</p><em>COSTS YOU: YOU DECIDE</em></div>
  </div>
  <p class="note"><b>Bigger prize, more spins.</b> Spots with better offers come up more often on the spinner and sit higher on the Prizes page. Everyone's competing for the same students, and the best offer wins the most of them.</p>
</section>

<section>
  <div class="x2"><span class="big">×2</span><div><b>POST IT, DOUBLE IT.</b><p>Every winner will get the same deal: post your prize on your story, tag the spot, and we double it. For the cost of one extra coffee, you get a Queen's student showing your spot to all their friends.</p></div></div>
</section>

<section>
  <div class="kick">YOU'RE IN CONTROL · BUILT FOR OUR JANUARY LAUNCH</div>
  <h2 class="h">YOUR OFFER, <span>YOUR RULES.</span></h2>
  <ul class="ctrl">
    <li><span><b>Set a weekly cap</b>Never give out more than you planned.</span></li>
    <li><span><b>Pick days and hours</b>Only weekdays, only afternoons, whatever works.</span></li>
    <li><span><b>One per student</b>Each code will work once, with a live clock so screenshots don't pass.</span></li>
    <li><span><b>Nothing for staff to learn</b>Look at the phone, tap redeem. Ten seconds.</span></li>
    <li><span><b>Change it anytime</b>New offer, pause for exams, back in September. One message.</span></li>
    <li><span><b>No cut of your sales</b>No commission, no card fees, no contract.</span></li>
  </ul>
</section>

<section>
  <div class="kick">YOUR WEEKLY REPORT · STARTS AT LAUNCH</div>
  <h2 class="h">EVERY CLICK, CODE AND VISIT, <span>COUNTED.</span></h2>
  <div class="dash"><div class="top"><div class="who"><i id="dMono" style="background:{sample["col"]}">{sample["mono"]}</i><div><b id="dName">{e(sample["name"])}</b><span>YOUR WEEK ON OFF CAMPUS</span></div></div><span class="tag">EXAMPLE NUMBERS</span></div>
    <div class="kpis">
      <div class="kpi hot"><small>Codes redeemed in store</small><b>74</b></div>
      <div class="kpi"><small>Students who landed on you</small><b>1,240</b></div>
      <div class="kpi"><small>Clicks to your site + Instagram</small><b>312</b></div>
      <div class="kpi"><small>Codes won</small><b>186</b></div>
      <div class="kpi"><small>Winners who posted you</small><b>21</b></div>
    </div>
    <div class="week" aria-label="Codes redeemed by day">{week}</div>
    <p class="foot">Codes redeemed by day. Example of the report you'd get every week.</p></div>
</section>

<section>
  <div class="kick">ONE SPOT PER CATEGORY</div>
  <h2 class="h">ONE COFFEE SHOP. ONE GYM. ONE BAR. <span>FIRST COME, FIRST SERVED.</span></h2>
  <p class="sub">To make every spot worth it, founding partners get their category to themselves at launch. Once a category is taken, the next business in it waits for an opening.</p>
  <div class="cats">{cats}</div>
</section>

<section>
  <div class="kick">THE FOUNDING PARTNER DEAL</div>
  <h2 class="h">GET IN BEFORE <span>JANUARY.</span></h2>
  <div class="deal">
    <div class="free"><small>FOUNDING PARTNERS</small><b>FIRST MONTH FREE</b><p>You only cover the prizes students win. No contract, no commission, cancel anytime.</p></div>
    <ul>
      <li><span><b>Your category, locked</b> for launch.</span></li>
      <li><span><b>Your logo on the launch posts</b> and the January Cup promo.</span></li>
      <li><span><b>The founding rate, kept</b> after your free month.</span></li>
      <li><span><b>First say on new features</b>: tell us what you need and we build it.</span></li>
    </ul>
  </div>
</section>

<section>
  <div class="kick">QUESTIONS</div>
  <h2 class="h">GOOD <span>QUESTIONS.</span></h2>
  <div class="faq">{faq}</div>
</section>

<section id="join">
  <div class="join">
    <div><div class="kick">CLAIM A FOUNDING SPOT</div><h2>LET'S PUT YOUR SPOT <span>IN THE GAME.</span></h2>
      <p class="sub">Tell us who you are and what you might offer. Josh will message you within a day to set it up. No commitment until you say yes.</p>
      <p class="dm">Rather message? <a href="{ig}" target="_blank" rel="noopener">DM @offcampuskingston on Instagram</a></p>
      <p class="dm"><a id="try3" href="daily.html">Or try the game first &rarr;</a></p></div>
    <form name="founding-partner" method="POST" action="thanks.html" data-netlify="true" netlify-honeypot="company-site">
      <input type="hidden" name="form-name" value="founding-partner">
      <p hidden><label>Leave this empty <input name="company-site"></label></p>
      <label>YOUR BUSINESS<input name="business" id="fBiz" required autocomplete="organization"></label>
      <label>YOUR NAME<input name="name" required autocomplete="name"></label>
      <label>EMAIL OR INSTAGRAM<input name="contact" required></label>
      <label>WHAT YOU MIGHT OFFER<select name="offer"><option>My existing student discount</option><option>Something free with purchase</option><option>A slow-hour deal</option><option>A big prize a few times a week</option><option>Not sure yet, help me pick</option></select></label>
      <fieldset class="ints"><legend>ALSO INTERESTED IN</legend>
        <label class="ck"><input type="checkbox" name="interest" value="Crew deal"><span><b>A crew deal</b> · a group offer a house unlocks together (bookings, big orders)</span></label>
        <label class="ck"><input type="checkbox" name="interest" value="Sponsored question"><span><b>A sponsored question</b> · your question in the daily game, plus what Queen's students really answered</span></label>
        <label class="ck"><input type="checkbox" name="interest" value="Club night"><span><b>A club night</b> · sponsor a Queen's club's game night or challenge</span></label>
        <label class="ck"><input type="checkbox" name="interest" value="Parents offer"><span><b>A parents offer</b> · winners send it home and parents pay the rest (cleaning, meal prep, storage)</span></label>
      </fieldset>
      <label>ANYTHING ELSE<textarea name="message"></textarea></label>
      <button class="btn" type="submit">CLAIM A FOUNDING SPOT</button>
    </form>
  </div>
</section>'''

b_js = '''<script>
(function(){
  var q = new URLSearchParams(location.search), spot = (q.get('spot') || '').trim();
  var end = function(){ var s = document.getElementById('mstrip'); if (!s) return; var cards = s.children, idx = cards.length - 4, w = 76;
    s.style.setProperty('--end', (s.parentNode.clientWidth / 2 - (idx * w + 35)) + 'px'); };
  if (spot) {
    var offer = (q.get('offer') || 'A student deal').trim(), big = (q.get('big') || '').trim();
    var col = (q.get('col') || '').replace('#', ''); col = /^[0-9a-f]{6}$/i.test(col) ? '#' + col : '#E3262B';
    var words = spot.split(/\\s+/).filter(function(w){ return /[a-z0-9]/i.test(w); });
    var mono = (words.length > 1 ? words[0][0] + words[1][0] : spot.replace(/[^a-z0-9]/gi, '').slice(0, 2)).toUpperCase();
    document.body.classList.add('is-mine');
    document.getElementById('mine').textContent = 'MADE FOR ' + spot.toUpperCase();
    document.getElementById('mOffer').textContent = big || offer;
    document.getElementById('mName').textContent = 'at ' + spot;
    document.getElementById('dName').textContent = spot;
    var dm = document.getElementById('dMono'); dm.textContent = mono; dm.style.background = col;
    var fb = document.getElementById('fBiz'); if (fb) fb.value = spot;
    var s = document.getElementById('mstrip'), card = document.createElement('div');
    card.className = 'mc'; card.style.background = col;
    var b = document.createElement('b'); b.textContent = mono; var sp = document.createElement('span'); sp.textContent = spot.toUpperCase().slice(0, 18);
    card.appendChild(b); card.appendChild(sp);
    s.replaceChild(card, s.children[s.children.length - 4]);
    var link = 'daily.html' + location.search;
    ['try', 'try2', 'try3'].forEach(function(id){ var a = document.getElementById(id); if (a) a.href = link; });
    document.getElementById('try').innerHTML = 'SEE ' + spot.toUpperCase().replace(/[<>&]/g, '') + ' IN THE GAME &rarr;';
    document.title = 'Off Campus × ' + spot;
  }
  end(); addEventListener('resize', end);
})();
</script>'''

page_html = ('<!doctype html>\n<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
  '<title>Off Campus for Kingston Businesses</title>\n<meta name="description" content="Get Queen\'s students through your door. Off Campus is the free daily game for Queen\'s students, with prizes from Kingston spots. Founding partners: first month free.">\n'
  '<meta property="og:title" content="Off Campus for Kingston Businesses">\n<meta property="og:description" content="Turn Queen\'s students into regulars. First month free for founding partners.">\n'
  f'{FONTS}\n<style>{BASE_CSS}{b_css}</style>\n</head><body>\n{BG}\n<main class="wrap">\n{b_body}\n'
  '<footer><span><b>Off Campus</b> · Kingston, Ontario · Not affiliated with Queen\'s University</span><span>The spots on the game demo are made-up examples.</span></footer>\n</main>\n'
  f'{b_js}\n</body></html>\n')
open(OUT + 'brands.html', 'w').write(page_html)

# thank-you page after the form
thanks = ('<!doctype html>\n<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<title>Thanks | Off Campus</title>\n'
  f'{FONTS}\n<style>{BASE_CSS}.box{{margin:12vh auto 0;max-width:560px;text-align:center;display:flex;flex-direction:column;gap:16px;padding:32px 22px;border-radius:24px;background:var(--night-2);box-shadow:0 0 0 3px var(--gold)}}.box h1{{margin:0;font-family:var(--display);font-weight:400;font-size:clamp(36px,8vw,56px);line-height:.95}}.box h1 span{{color:var(--gold)}}.box p{{margin:0;font-size:15px;font-weight:600;line-height:1.55;color:var(--muted)}}</style>\n</head><body>\n{BG}\n<main class="wrap"><div class="box"><h1>YOU\'RE ON <span>THE LIST.</span></h1><p>Thanks! Josh will message you within a day to set up your founding spot.</p><a class="btn" href="daily.html">PLAY TODAY\'S FIVE WHILE YOU WAIT</a><a href="./" style="font-size:13px;font-weight:700;color:var(--muted)">Back to Off Campus</a></div></main>\n</body></html>\n')
open(OUT + 'thanks.html', 'w').write(thanks)

# link maker for Josh: build a personal preview link for a business
maker = ('<!doctype html>\n<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">\n<meta name="robots" content="noindex">\n<title>Link maker | Off Campus</title>\n'
  f'{FONTS}\n<style>{BASE_CSS}form{{display:grid;gap:10px}}label{{display:grid;gap:6px;font-size:11px;font-weight:700;letter-spacing:.14em;color:var(--muted)}}input{{box-sizing:border-box;width:100%;min-height:50px;padding:12px 14px;border:0;border-radius:12px;background:var(--cream);color:var(--ink);font:600 15px var(--mono)}}input[type=color]{{padding:4px;height:50px}}.out{{display:grid;gap:8px;padding:14px;border-radius:16px;background:var(--night-2)}}.out code{{word-break:break-all;font-size:12px;color:var(--mint)}}.out button{{min-height:46px;border-radius:12px;background:var(--gold);color:var(--ink);font-family:var(--display);font-size:15px}}h1{{margin:0;font-family:var(--display);font-weight:400;font-size:40px}}</style>\n</head><body>\n'
  '<main class="wrap" style="max-width:640px"><h1>LINK MAKER</h1><p class="lede">Fill this in for a business, then send them their link. Their spot shows up in the game and on the brand page.</p>\n'
  '<form id="f" onsubmit="return false"><label>BUSINESS NAME<input id="spot" placeholder="The business name"></label><label>WHAT KIND<input id="kind" placeholder="Coffee · Princess St"></label>'
  '<label>THEIR EVERYDAY OFFER<input id="offer" placeholder="15% off any drink"></label><label>THEIR BIG PRIZE (OPTIONAL)<input id="big" placeholder="A free latte"></label><label>BRAND COLOUR<input id="col" type="color" value="#C8782A"></label></form>\n'
  '<div class="out"><b>BRAND PAGE (send this one)</b><code id="o1"></code><button data-t="o1">COPY</button></div><div class="out"><b>STRAIGHT INTO THE GAME</b><code id="o2"></code><button data-t="o2">COPY</button></div></main>\n'
  '<script>(function(){var ids=["spot","kind","offer","big","col"];function upd(){var p=new URLSearchParams();ids.forEach(function(i){var v=document.getElementById(i).value.trim();if(i==="col")v=v.replace("#","");if(v)p.set(i,v);});'
  'var base="https://offcampusontario.ca/";document.getElementById("o1").textContent=base+"brands.html?"+p.toString();document.getElementById("o2").textContent=base+"daily.html?"+p.toString();}'
  'ids.forEach(function(i){document.getElementById(i).addEventListener("input",upd);});upd();'
  'document.querySelectorAll("[data-t]").forEach(function(b){b.onclick=function(){navigator.clipboard.writeText(document.getElementById(b.dataset.t).textContent).then(function(){b.textContent="COPIED";setTimeout(function(){b.textContent="COPY"},1200);});};});})();</script>\n</body></html>\n')
open(OUT + 'link.html', 'w').write(maker)

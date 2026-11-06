/* ================= SCORE CARD, RESULTS, ALREADY-PLAYED SCREEN ================= */
const IG_URL = 'https://instagram.com/offcampuskingston';
const SHARE_URL = 'offcampusontario.ca';
async function drawCard(total, pts, types, stamp){
  try { await document.fonts.ready; } catch (e) {}
  const c = document.createElement('canvas'); c.width = 1080; c.height = 1350; const x = c.getContext('2d');
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const g = x.createRadialGradient(540, 0, 50, 540, 300, 1100); g.addColorStop(0, '#3a2a06'); g.addColorStop(1, css('--night'));
  x.fillStyle = css('--night'); x.fillRect(0, 0, 1080, 1350); x.fillStyle = g; x.fillRect(0, 0, 1080, 1350);
  x.strokeStyle = css('--gold'); x.lineWidth = 10; x.strokeRect(40, 40, 1000, 1270);
  x.textAlign = 'center'; x.fillStyle = css('--mint'); x.font = '700 34px "IBM Plex Mono", monospace';
  x.fillText(`${DAY.school.toUpperCase()} DAILY · NO. ${pad3(DAY.no)}`, 540, 150);
  x.fillStyle = css('--text'); x.font = '96px "Bowlby One", Impact, sans-serif'; x.fillText('OFF CAMPUS', 540, 270);
  x.fillStyle = css('--gold'); x.font = '230px "Bowlby One", Impact, sans-serif'; x.fillText(fmt(total), 540, 560);
  x.fillStyle = css('--muted'); x.font = '700 38px "IBM Plex Mono", monospace'; x.fillText('OUT OF 5,000', 540, 630);
  const sz = 150, gap = 26, x0 = 540 - (5 * sz + 4 * gap) / 2;
  pts.forEach((p, k) => { const cx = x0 + k * (sz + gap); x.fillStyle = p >= 800 ? css('--good') : p >= 500 ? css('--mid') : p >= 200 ? css('--low') : css('--bad');
    x.beginPath(); if (x.roundRect) x.roundRect(cx, 700, sz, sz, 22); else x.rect(cx, 700, sz, sz); x.fill();
    x.fillStyle = css('--ink'); x.font = '44px "Bowlby One", Impact, sans-serif'; x.fillText(SQLAB[types[k]], cx + sz / 2, 792); });
  x.save(); x.translate(540, 990); x.rotate(-.05); x.font = '60px "Bowlby One", Impact, sans-serif';
  const w = Math.min(900, x.measureText(stamp).width + 90); x.fillStyle = css('--stamp'); x.fillRect(-w / 2, -70, w, 120);
  x.fillStyle = css('--paper'); x.fillText(stamp, 0, 12); x.restore();
  x.fillStyle = css('--text'); x.font = '700 42px "IBM Plex Mono", monospace'; x.fillText('Can you beat me?', 540, 1170);
  x.fillStyle = css('--gold'); x.font = '40px "Bowlby One", Impact, sans-serif'; x.fillText(SHARE_URL.toUpperCase(), 540, 1240);
  return c.toDataURL('image/png');
}
function saveDay(){
  const rec = { total:S.total, pts:S.results.map(r => r.pts), types:S.results.map(r => r.type) };
  const prevBest = (store.get('oc-streak') || {}).best || 0;
  store.set(PLAY_KEY, rec);
  const st = store.get('oc-streak') || { last:0, n:0, best:0, days:0 };
  if (st.last !== DAY.no) { st.n = st.last === DAY.no - 1 ? st.n + 1 : 1; st.last = DAY.no; st.days = (st.days || 0) + 1; }
  st.best = Math.max(st.best || 0, S.total); store.set('oc-streak', st);
  return { st, newBest: S.total > prevBest && prevBest > 0 };
}
function stampFor(st, newBest){ return st.n >= 2 ? `${st.n}-DAY STREAK` : newBest ? 'NEW PERSONAL BEST' : `DAY ${pad3(DAY.no)} DONE`; }
function wireShare(total, pts, types, stamp){
  const text = `Off Campus · ${DAY.school} Daily #${pad3(DAY.no)}\n${fmt(total)}/5,000 ${pts.map(sqEmoji).join('')}\nCan you beat me? https://${SHARE_URL}/?ref=share`;
  let png = null; const getPng = async () => png || (png = await drawCard(total, pts, types, stamp));
  const copy = async () => { try { await navigator.clipboard.writeText(text); toast('COPIED, PASTE IT ANYWHERE'); } catch (e) { toast('COULDN\'T COPY'); } };
  $('#see').onclick = async () => { SFX.tap(); const src = await getPng(); const d = document.createElement('div'); d.className = 'lightbox'; d.innerHTML = `<img src="${src}" alt="Your score card" style="border-radius:14px;max-height:84vh">`; d.onclick = () => d.remove(); document.body.appendChild(d); };
  $('#share').onclick = async () => { SFX.tap(); track('share');
    try { const blob = await (await fetch(await getPng())).blob(), file = new File([blob], 'off-campus-daily.png', { type:'image/png' });
      if (navigator.canShare && navigator.canShare({ files:[file] })) { await navigator.share({ files:[file], text }); return; }
      if (navigator.share) { await navigator.share({ text }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
    copy(); };
  const f = $('#follow'); if (f) f.onclick = () => { track('follow'); };
}
const statsRow = st => `<div class="today"><h3>YOU</h3><div><small>STREAK</small><b>${st.n || 0}</b></div><div><small>BEST</small><b>${fmt(st.best || 0)}</b></div><div><small>DAYS</small><b>${st.days || 0}</b></div></div>`;
const tailHTML = () => `<div class="row2"><button class="btn ghost" id="share">SHARE MY SCORE</button><button class="btn ghost" id="see">SEE THE IMAGE</button></div>
    <a class="btn ghost" id="follow" href="${IG_URL}" target="_blank" rel="noopener" style="text-decoration:none;color:var(--text)">FOLLOW US ON INSTAGRAM</a>
    <div class="cd">NEXT FIVE IN <b id="cd">${nextDropText()}</b></div>`;
function startCountdown(){ const cdT = setInterval(() => { const e = $('#cd'); if (!e) return clearInterval(cdT); e.textContent = nextDropText(); }, 1000); }
async function results(){
  document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);
  const ok = S.total >= UNLOCK || !!GUEST;
  let stamp, st = { n:0, best:S.total, days:1 };
  if (GUEST) stamp = `BEAT ${beatPct(S.total)}% OF ${DAY.school.toUpperCase()} TODAY`;
  else { const r = saveDay(); st = r.st; stamp = stampFor(st, r.newBest); track('finish'); if (S.total >= UNLOCK) track('unlocked'); }
  const pts = S.results.map(r => r.pts), types = S.results.map(r => r.type);
  const live = PRIZES_LIVE || !!GUEST;
  app.innerHTML = `<section class="screen">${TABS('daily')}
    <div class="card"><div class="top"><span>${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)}</span><span>${esc(DAY.date.toUpperCase())}</span></div>
      <div class="total" id="big">0</div><div class="of">OUT OF 5,000</div>
      <div class="squares">${S.results.map((r, k) => `<div class="sq"><i style="background:${sqColor(r.pts)};animation-delay:${600 + k * 120}ms"></i><span>${SQLAB[r.type]}</span><b>${fmt(r.pts)}</b></div>`).join('')}</div>
      <span class="rankstamp">${esc(stamp)}</span></div>
    ${ok
      ? (live ? `<div class="gate ok"><b>YOU UNLOCKED A PRIZE!</b><span>You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.</span></div><button class="btn pulse dock go" id="prize">SPIN FOR YOUR PRIZE!</button>`
              : `<div class="gate ok"><b>YOU'D HAVE UNLOCKED A PRIZE!</b><span>You beat ${fmt(UNLOCK)}. The prize wheel drops soon.</span></div><button class="btn pulse dock go" id="prize">SEE WHAT'S COMING</button>`)
      : `<div class="gate"><b>${fmt(UNLOCK - S.total)} POINTS SHORT</b><span>${live ? `You needed ${fmt(UNLOCK)} to unlock the prize spin.` : `When prizes drop, ${fmt(UNLOCK)} unlocks the spin.`} New five at 4am.</span></div><a class="btn mint dock" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a>`}
    ${GUEST ? '' : statsRow(st)}
    ${tailHTML()}
    ${GUEST ? '<p class="demo-note">Brand preview: player numbers and "beat %" are samples.</p>' : ''}
  </section>`;
  if (S.total >= UNLOCK) { SFX.fanfare(); vibe([40, 30, 40, 30, 120]); } else { SFX.ok(); vibe(30); }
  countUp($('#big'), S.total, 1500);
  startCountdown();
  wireShare(S.total, pts, types, stamp);
  if (ok) $('#prize').onclick = () => { SFX.ok(); vibe(20); live ? prize() : prizeTeaser(); };
}
function doneScreen(rec){
  document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);
  const st = store.get('oc-streak') || { n:1, best:rec.total, days:1 };
  const stamp = st.n >= 2 ? `${st.n}-DAY STREAK` : `DAY ${pad3(DAY.no)} DONE`;
  app.innerHTML = `<section class="screen">${TABS('daily')}
    <div class="kick">YOU'VE PLAYED TODAY'S FIVE</div>
    <div class="card"><div class="top"><span>${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)}</span><span>${esc(DAY.date.toUpperCase())}</span></div>
      <div class="total">${fmt(rec.total)}</div><div class="of">OUT OF 5,000</div>
      <div class="squares">${rec.pts.map((p, k) => `<div class="sq"><i style="background:${sqColor(p)}"></i><span>${SQLAB[rec.types[k]]}</span><b>${fmt(p)}</b></div>`).join('')}</div>
      <span class="rankstamp" style="animation-delay:0s">${esc(stamp)}</span></div>
    ${statsRow(st)}
    <div class="gate ok" style="box-shadow:inset 0 0 0 2px var(--gold)"><b style="color:var(--gold)">PRIZE WHEEL DROPS SOON</b><span>Score ${fmt(UNLOCK)} and you'll spin for free stuff from Kingston spots.</span></div>
    ${tailHTML()}
    <a class="btn mint dock" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a>
  </section>`;
  startCountdown();
  wireShare(rec.total, rec.pts, rec.types, stamp);
}

/* ================= PRESEASON PRIZE TEASER =================
   Same sliding strip as the real spin, but it stops on "COMING SOON". Turn PRIZES_LIVE on when brands are in. */
const TEASE = [
  { m:'FREE', s:'COFFEE', c:'#C8782A' }, { m:'BOGO', s:'COOKIES', c:'#E8608A' }, { m:'20%', s:'ESCAPE ROOM', c:'#6C4BE0' },
  { m:'VIP', s:'NIGHT OUT 19+', c:'#B03BD1' }, { m:'FREE', s:'CLIMB', c:'#3E8E5A' }, { m:'15%', s:'MERCH', c:'#2E5BD8' }, { m:'★', s:'JACKPOT', c:'jp' } ];
async function prizeTeaser(){
  window.scrollTo(0, 0); track('teaser');
  const strip = Array.from({ length:REEL_LEN }, (_, i) => TEASE[(i * 3 + 1) % TEASE.length]);
  strip[REEL_STOP] = { lock:true }; strip[REEL_STOP + 1] = TEASE[6];
  const card = s => s.lock ? `<div class="rc lock"><b>SOON</b><span>PRIZES DROPPING</span></div>`
    : s.c === 'jp' ? `<div class="rc jp"><b>★</b><span>JACKPOT</span></div>` : `<div class="rc" style="--c:${s.c}"><b>${s.m}</b><span>${s.s}</span></div>`;
  app.innerHTML = `<section class="screen"><div class="prize-head"><div class="kick">PRESEASON</div><h2>THE PRIZE SPIN</h2><p>Kingston spots fly by. Wherever it stops, that's who you win from.</p></div>
    <div class="reel" id="reel"><div class="strip" id="strip">${strip.map(card).join('')}</div><div class="marker" aria-hidden="true"></div></div>
    <div id="out"></div>
    <button class="btn pulse dock go" id="sp">TRY THE SPIN</button></section>`;
  const reelEl = $('#reel'), stripEl = $('#strip');
  const place = x => { stripEl.style.transform = `translateX(${x}px)`; };
  const startX = reelEl.clientWidth / 2 - REEL_CARD * 2.5; place(startX);
  $('#sp').onclick = async () => {
    const b = $('#sp'); b.disabled = true; b.classList.remove('pulse'); b.textContent = 'SPINNING…'; SFX.whoosh(); vibe(20);
    const endX = reelEl.clientWidth / 2 - (REEL_STOP * REEL_CARD + (REEL_CARD - 8) / 2) + (Math.random() - .5) * (REEL_CARD - 50);
    const ms = reduced ? 300 : 5200, t0 = performance.now(); let last = -1; const ease = p => 1 - Math.pow(1 - p, 5);
    await new Promise(res => { (function f(now){ const p = Math.min(1, (now - t0) / ms), x = startX + (endX - startX) * ease(p); place(x);
      const u = Math.floor((reelEl.clientWidth / 2 - x) / REEL_CARD); if (u !== last) { last = u; SFX.click(); if (p > .55) vibe(5); }
      if (p < 1) requestAnimationFrame(f); else res(); })(t0); });
    stripEl.children[REEL_STOP].classList.add('hit'); SFX.stamp(); vibe([40, 30, 80]); b.remove();
    $('#out').innerHTML = `<div class="won"><div class="lbl" style="color:var(--red)">SO CLOSE</div>
      <h3>The prize wheel drops soon.</h3>
      <p style="margin:0;font-size:14px;font-weight:600;line-height:1.5">Free coffee, cookies, escape rooms, nights out and a weekly jackpot from Kingston spots. When it drops, scoring ${fmt(UNLOCK)} gets you a real spin. Follow us so you know the second it's live.</p>
      <a class="btn" href="${IG_URL}" target="_blank" rel="noopener" style="text-decoration:none" id="follow2">FOLLOW US ON INSTAGRAM</a></div>
      <div class="after"><a class="btn mint" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a><button class="btn ghost" id="back">BACK TO MY SCORE</button></div>`;
    $('#follow2').onclick = () => track('follow');
    $('#back').onclick = () => { SFX.tap(); const rec = store.get(PLAY_KEY); if (rec) doneScreen(rec); else intro(); };
    $('#out').scrollIntoView({ behavior:reduced ? 'auto' : 'smooth', block:'start' });
  };
}


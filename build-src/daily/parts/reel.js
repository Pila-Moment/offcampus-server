/* first spin: a strip of spots slides past a marker and slows down (you never see the whole list) */
const REEL_CARD = 124;   // card width + gap, px
const REEL_LEN = 48, REEL_STOP = 40;
async function prize(){
  window.scrollTo(0, 0);
  const spots = BRANDS.concat([JACKPOT]);
  const pickSpot = () => spots[pickW(spots.map(s => ({ w:s.slice })))];
  const forced = /[?&]jackpot\b/.test(location.search);
  const win = forced ? JACKPOT : pickSpot();
  const strip = Array.from({ length:REEL_LEN }, pickSpot);
  strip[REEL_STOP] = win;
  if (win !== JACKPOT && Math.random() < .6) strip[REEL_STOP + (Math.random() < .5 ? 1 : -1)] = JACKPOT;   // so close
  const card = s => s === JACKPOT
    ? `<div class="rc jp"><b>★</b><span>JACKPOT</span></div>`
    : `<div class="rc" style="--c:${s.col}"><b>${esc(s.mono)}</b><span>${esc(s.short)}</span></div>`;
  app.innerHTML = `<section class="screen"><div class="prize-head"><div class="kick">SPIN 1 OF 2</div><h2>PICK YOUR SPOT</h2><p>Kingston spots fly by. Wherever it stops, that's who you win from.</p></div>
    <div class="reel" id="reel"><div class="strip" id="strip">${strip.map(card).join('')}</div><div class="marker" aria-hidden="true"></div></div>
    <div id="landed" class="landed"></div>
    <button class="btn pulse dock go" id="sp">SPIN!</button><div id="out"></div>
    <p class="demo-note">Sample prizes from made-up Kingston spots. Real partners are added as they sign on.</p></section>`;
  const reelEl = $('#reel'), stripEl = $('#strip');
  const place = x => { stripEl.style.transform = `translateX(${x}px)`; };
  const startX = reelEl.clientWidth / 2 - REEL_CARD * 2.5;
  place(startX);
  $('#sp').onclick = async () => {
    const b = $('#sp'); b.disabled = true; b.classList.remove('pulse'); b.textContent = 'SPINNING…'; SFX.whoosh(); vibe(20);
    const endX = reelEl.clientWidth / 2 - (REEL_STOP * REEL_CARD + (REEL_CARD - 8) / 2) + (Math.random() - .5) * (REEL_CARD - 40);
    const ms = reduced ? 300 : 5600, t0 = performance.now(); let lastCard = -1;
    const ease = p => 1 - Math.pow(1 - p, 5);
    await new Promise(res => { (function f(now){
      const p = Math.min(1, (now - t0) / ms), x = startX + (endX - startX) * ease(p);
      place(x);
      const under = Math.floor((reelEl.clientWidth / 2 - x) / REEL_CARD);
      if (under !== lastCard) { lastCard = under; SFX.click(); if (p > .55) vibe(5); }
      if (p < 1) requestAnimationFrame(f); else res();
    })(t0); });
    stripEl.children[REEL_STOP].classList.add('hit');
    if (win === JACKPOT) { SFX.fanfare(); confetti(); vibe([60, 40, 60, 40, 200]); b.remove(); return showWin(JACKPOT, JACKPOT.prize, true); }
    SFX.ding(); vibe(40);
    $('#landed').innerHTML = `YOU LANDED ON <b style="color:${win.col}">${esc(win.name.toUpperCase())}</b>`;
    b.textContent = 'NEXT: YOUR PRIZE';
    await wait(reduced ? 0 : 1300);
    wheel2(win);
  };
}

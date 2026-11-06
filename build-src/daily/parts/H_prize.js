/* ================= THE PRIZE: two spins ================= */
// Slices can be different sizes (s.w). Angles are measured clockwise from the top.
function layout(slices){ const tot = slices.reduce((a, s) => a + (s.w || 1), 0); let a = 0; return slices.map(s => { const span = 360 * (s.w || 1) / tot, o = { a0:a, a1:a + span, mid:a + span / 2, span }; a += span; return o; }); }
function wheelSVG(slices, id){
  const R0 = 200, cx = 200, cy = 200, L2 = layout(slices);
  const pt = (deg, r) => { const t = (deg - 90) * Math.PI / 180; return [cx + r * Math.cos(t), cy + r * Math.sin(t)]; };
  const parts = slices.map((s, k) => {
    const { a0, a1, mid, span } = L2[k], [x0, y0] = pt(a0, R0), [x1, y1] = pt(a1, R0), large = span > 180 ? 1 : 0;
    const [tx, ty] = pt(mid, R0 * .62);
    const fs = Math.min(span < 30 ? 12 : 17, s.label.length > 12 ? 13 : s.label.length > 9 ? 15 : 17);
    return `<path d="M${cx} ${cy}L${x0.toFixed(1)} ${y0.toFixed(1)}A${R0} ${R0} 0 ${large} 1 ${x1.toFixed(1)} ${y1.toFixed(1)}Z" fill="${s.col}" stroke="var(--night)" stroke-width="3"/>
      <text x="${tx.toFixed(1)}" y="${ty.toFixed(1)}" transform="rotate(${(mid > 180 ? mid + 90 : mid - 90).toFixed(1)} ${tx.toFixed(1)} ${ty.toFixed(1)})" text-anchor="middle" dominant-baseline="middle" font-family="Bowlby One, Impact, sans-serif" font-size="${fs}" fill="${s.ink || '#FFFFFF'}" style="letter-spacing:.02em">${esc(s.label)}</text>`;
  }).join('');
  const bulbs = Array.from({ length:20 }, (_, k) => { const [bx, by] = pt(k * 18, R0 + 9); return `<circle cx="${bx.toFixed(1)}" cy="${by.toFixed(1)}" r="4" fill="${k % 2 ? 'var(--cream)' : 'var(--gold)'}"/>`; }).join('');
  return `<svg class="wheel" viewBox="-20 -20 440 440" aria-hidden="true"><circle cx="200" cy="200" r="214" fill="var(--gold-deep)"/>${bulbs}<g id="${id}">${parts}</g></svg>`;
}
const POINTER = '<svg class="pointer" viewBox="0 0 34 44" aria-hidden="true"><path d="M17 42L3 8a14 14 0 0 1 28 0z" fill="var(--red)" stroke="var(--cream)" stroke-width="3"/><circle cx="17" cy="12" r="5" fill="var(--cream)"/></svg>';
function spin(gEl, slices, target, ms){
  // land somewhere inside slice `target` under the pointer, after several turns
  const L2 = layout(slices), T = L2[target], into = T.a0 + T.span * (.2 + Math.random() * .6);
  const end = 360 * (5 + Math.floor(Math.random() * 2)) + (360 - into);
  const t0 = performance.now(); let lastSlice = -1;
  const ease = p => 1 - Math.pow(1 - p, 4);
  const sliceAt = rot => { const top = ((360 - rot % 360) % 360 + 360) % 360; return L2.findIndex(o => top >= o.a0 && top < o.a1); };
  return new Promise(res => { (function f(now){
    const p = Math.min(1, (now - t0) / ms), rot = end * ease(p);
    gEl.setAttribute('transform', `rotate(${rot.toFixed(2)} 200 200)`);
    const sl = sliceAt(rot); if (sl !== lastSlice) { lastSlice = sl; SFX.click(); if (p > .6) vibe(4); }
    if (p < 1) requestAnimationFrame(f); else res();
  })(t0); });
}
const pickW = arr => { const tot = arr.reduce((s, x) => s + x.w, 0); let r = Math.random() * tot; for (let i = 0; i < arr.length; i++) { r -= arr[i].w; if (r <= 0) return i; } return arr.length - 1; };
function confetti(){
  if (reduced) return; const cols = ['var(--gold)', 'var(--mint)', 'var(--red)', 'var(--hi)', 'var(--blue)', 'var(--cream)'];
  for (let i = 0; i < 90; i++) { const p = document.createElement('i'); p.className = 'confetti'; p.style.left = Math.random() * 100 + 'vw'; p.style.top = '-20px'; p.style.background = cols[i % cols.length]; document.body.appendChild(p);
    p.animate([{ transform:'translate(0,0) rotate(0)' }, { transform:`translate(${(Math.random() - .5) * 200}px, ${innerHeight + 60}px) rotate(${Math.random() * 900}deg)` }], { duration:1600 + Math.random() * 1600, easing:'cubic-bezier(.2,.6,.4,1)', delay:Math.random() * 400 }).onfinish = () => p.remove(); }
}
async function prize(){
  window.scrollTo(0, 0);
  const spots = BRANDS.slice(); spots.splice(4, 0, JACKPOT);
  const slices = spots.map(b => ({ label:b.short, col:b.id === 'jackpot' ? 'var(--gold)' : b.col, ink:b.id === 'jackpot' ? '#111111' : null, w:b.slice }));
  app.innerHTML = `<section class="screen"><div class="prize-head"><div class="kick">SPIN 1 OF 2</div><h2>PICK YOUR SPOT</h2><p>Every Kingston spot on the wheel. Bigger prizes get bigger slices.</p></div>
    <div class="wheelbox" id="wb">${POINTER}${wheelSVG(slices, 'w1')}<div class="hub">FREE<br>SPIN</div></div>
    <button class="btn pulse" id="sp">SPIN FOR YOUR SPOT</button><div id="out"></div>
    <p class="demo-note">Sample prizes from made-up Kingston spots. Real partners are added as they sign on.</p></section>`;
  $('#sp').onclick = async () => {
    const b = $('#sp'); b.disabled = true; b.classList.remove('pulse'); b.textContent = 'SPINNING…'; SFX.whoosh(); vibe(20);
    const forced = /[?&]jackpot\b/.test(location.search);
    const target = forced ? spots.indexOf(JACKPOT) : pickW(spots.map(s => ({ w:s.slice })));
    await spin($('#w1'), slices, target, reduced ? 300 : 4600);
    const spot = spots[target];
    if (spot === JACKPOT) { SFX.fanfare(); confetti(); vibe([60, 40, 60, 40, 200]); return showWin(JACKPOT, JACKPOT.prize, true); }
    SFX.ding(); vibe(40);
    b.textContent = spot.name.toUpperCase();
    await wait(reduced ? 0 : 900);
    wheel2(spot);
  };
}
async function wheel2(brand){
  window.scrollTo(0, 0);
  const sl = []; brand.prizes.forEach((p, k) => { for (let i = 0; i < (p.big ? 1 : 3); i++) sl.push({ ...p, k }); });
  const ring = [sl[0], sl[1], sl[sl.length - 1], sl[2]].filter(Boolean);
  const slices = ring.map(p => ({ label:p.s, col:p.big ? 'var(--gold)' : brand.col, ink:p.big ? '#111111' : '#FFFFFF', p }));
  app.innerHTML = `<section class="screen"><div class="prize-head"><div class="kick">SPIN 2 OF 2 · YOU LANDED ON</div><h2 class="bname">${esc(brand.name.toUpperCase())}</h2><p><span class="dot" style="background:${brand.col}"></span>${esc(brand.kind)}</p></div>
    <div class="wheelbox small">${POINTER}${wheelSVG(slices, 'w2')}<div class="hub" style="color:${brand.col};box-shadow:0 0 0 5px ${brand.col}">${esc(brand.mono)}</div></div>
    <button class="btn pulse" id="sp2">REVEAL MY PRIZE</button><div id="out"></div></section>`;
  $('#sp2').onclick = async () => {
    const b = $('#sp2'); b.disabled = true; b.classList.remove('pulse'); b.textContent = 'SPINNING…'; SFX.whoosh();
    const k = pickW(brand.prizes); const prizeObj = brand.prizes[k];
    const candidates = slices.map((s, i) => s.p.k === k ? i : -1).filter(i => i >= 0);
    const target = candidates[Math.floor(Math.random() * candidates.length)];
    await spin($('#w2'), slices, target, reduced ? 300 : 3400);
    if (prizeObj.big) { SFX.fanfare(); confetti(); vibe([60, 40, 60, 40, 200]); } else { SFX.great(); vibe([40, 30, 80]); }
    showWin(brand, prizeObj, false);
  };
}
function showWin(brand, p, jackpot){
  const a = 2 + Math.floor(Math.random() * 8), b2 = 3 + Math.floor(Math.random() * 7), c = 1 + Math.floor(Math.random() * 9), ans = a * b2 - c;
  const code = 'OC-' + Math.random().toString(36).slice(2, 6).toUpperCase();
  const out = $('#out'); const btn = document.querySelector('#sp, #sp2'); if (btn) btn.remove();
  out.innerHTML = `<div class="won">
    <div class="brand"><span class="logo" style="background:${brand.col};color:${jackpot ? 'var(--ink)' : 'var(--paper)'}">${esc(brand.mono)}</span><div><b>${esc(brand.name)}</b><span>${esc(brand.kind.toUpperCase())}</span></div></div>
    <div class="lbl" style="color:var(--red)">${jackpot ? 'YOU HIT THE WEEKLY JACKPOT' : p.big ? 'BIG WIN' : 'YOU WON'}</div>
    <h3>${esc(p.t)}</h3>
    <div class="stq" id="stq"><label for="sa">One quick skill-testing question to claim it: ${a} × ${b2} − ${c} = ?</label><div><input id="sa" inputmode="numeric" autocomplete="off"><button class="btn" id="sok">CLAIM</button></div></div>
    <div id="claimed"></div>
    ${jackpot ? '' : `<button class="visit" id="visit">VISIT ${esc(brand.name.toUpperCase())} &rarr;</button>`}
    <p class="fine">No purchase necessary. Free to play. Prizes have no cash value. Demo prize: not redeemable.</p></div>
    <div class="after"><a class="btn mint" href="party.html" style="text-decoration:none">PLAY THE PARTY GAMES</a><a class="btn ghost" href="prizes.html" style="text-decoration:none">SEE EVERY PRIZE</a><button class="btn ghost" id="again">REPLAY THE DEMO</button></div>`;
  out.scrollIntoView({ behavior:reduced ? 'auto' : 'smooth', block:'start' });
  $('#again').onclick = () => { SFX.tap(); intro(); };
  const v = $('#visit'); if (v) v.onclick = () => { SFX.tap(); toast('THEIR SITE + INSTAGRAM GO HERE'); };
  $('#sok').onclick = () => {
    if (+$('#sa').value !== ans) { SFX.buzz(); toast('NOT QUITE, TRY AGAIN'); return; }
    SFX.ok(); $('#stq').remove();
    const cl = $('#claimed');
    cl.innerHTML = `<div class="code" id="cb"><small>SHOW THIS AT THE COUNTER</small><b>${code}</b><span class="clock" id="ck"></span></div>
      <div class="post"><b>DOUBLE IT:</b> post your prize on your story, tag Off Campus and ${esc(jackpot ? 'Night Shift' : brand.name)}, and we double it.</div>
      <button class="btn" id="red">TAP TO REDEEM IN FRONT OF STAFF</button>`;
    const ck = $('#ck'); const tick = () => { if (!document.body.contains(ck)) return clearInterval(iv); ck.textContent = new Date().toLocaleTimeString('en-CA', { hour:'numeric', minute:'2-digit', second:'2-digit' }); }; const iv = setInterval(tick, 1000); tick();
    $('#red').onclick = () => {
      SFX.stamp(); vibe(60); const cb = $('#cb'); cb.classList.add('used'); $('#red').remove();
      let left = 300; cb.querySelector('small').textContent = 'REDEEMED · STAFF: CHECK THE LIVE CLOCK';
      cb.insertAdjacentHTML('beforeend', '<span class="clock" id="left">5:00 LEFT TO SHOW STAFF</span>');
      const iv2 = setInterval(() => { const l = $('#left'); if (!l) return clearInterval(iv2); left--; l.textContent = `${Math.floor(left / 60)}:${String(left % 60).padStart(2, '0')} LEFT TO SHOW STAFF`; if (left <= 0) { clearInterval(iv2); cb.querySelector('b').textContent = 'USED'; l.textContent = 'THIS CODE IS USED'; } }, 1000);
    };
  };
}


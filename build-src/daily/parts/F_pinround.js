async function pinRound(){
  const r = R(), P = r.photo; let guess = null, year = YEAR_START, pin = null, locked = false;
  const nix = y => String(y).split('').map(c => `<i>${c}</i>`).join('');
  app.innerHTML = `<section class="screen">${hud()}
    <div id="top"><div class="photo" id="ph"><img src="${esc(P.img)}" alt="A photo somewhere in Kingston"><span class="zoom">TAP TO ZOOM</span></div></div>
    <div class="mapwrap" id="mw"><div id="map"></div><div class="maphint" id="hint">TAP THE MAP TO DROP YOUR PIN</div><div class="mapbtns"><button id="zi" aria-label="Zoom in">+</button><button id="zo" aria-label="Zoom out">&minus;</button></div></div>
    <div id="lower"><div class="yearbox"><div class="lbl">WHAT YEAR?</div>
      <div class="yrow"><button class="step" id="ym" aria-label="One year earlier">&minus;</button><div class="nix" id="nx">${nix(year)}</div><button class="step" id="yp" aria-label="One year later">+</button></div>
      <input type="range" id="yr" min="${YEAR_MIN}" max="${YEAR_MAX}" step="1" value="${year}" aria-label="Year"><div class="ylab"><span>${YEAR_MIN}</span><span>1900</span><span>1950</span><span>2000</span><span>${YEAR_MAX}</span></div></div>
      <button class="btn" id="lock" disabled style="margin-top:12px">DROP A PIN FIRST</button></div></section>`;
  wireSound(); SFX.shutter();
  $('#ph').onclick = () => { const d = document.createElement('div'); d.className = 'lightbox'; d.innerHTML = `<img src="${esc(P.img)}" alt="Photo, full size">`; d.onclick = () => d.remove(); document.body.appendChild(d); SFX.tap(); };
  let lastY = year;
  const setYear = (y, snd) => { year = Math.max(YEAR_MIN, Math.min(YEAR_MAX, y)); $('#nx').innerHTML = nix(year); $('#yr').value = year; if (snd) SFX.tick(); };
  $('#yr').oninput = e => { setYear(+e.target.value, false); if (Math.abs(year - lastY) >= 3) { SFX.tick(); lastY = year; } };
  $('#ym').onclick = () => setYear(year - 1, true); $('#yp').onclick = () => setYear(year + 1, true);
  await buildMap($('#map'), ll => {
    if (locked) return; guess = ll; SFX.pin(); vibe(20); $('#hint').classList.add('gone');
    if (pin) pin.setLatLng(ll); else { pin = L.marker(ll, { icon:L.divIcon({ className:'', html:PIN_HTML, iconSize:[36,46], iconAnchor:[18,45] }), draggable:true, keyboard:false }).addTo(map); pin.on('dragend', () => { guess = pin.getLatLng(); SFX.pin(); }); }
    const b = $('#lock'); b.disabled = false; b.textContent = 'LOCK IT IN';
  });
  $('#zi').onclick = () => map.zoomIn(); $('#zo').onclick = () => map.zoomOut();
  $('#lock').onclick = async () => {
    if (locked || !guess) return; locked = true; vibe([30, 40, 60]); SFX.whoosh();
    const truth = L.latLng(P.lat, P.lng), dist = metres(guess, truth), dy = year - P.year;
    const place = placePts(dist), when = yearPts(dy), pts = place + when;
    if (pin) { pin.dragging && pin.dragging.disable(); }
    const yrs = n => `${n} year${n === 1 ? '' : 's'}`;
    // 1) the year, 2) the map, 3) the points. All at the top so nothing hides below the map.
    $('#top').innerHTML = `<div class="pinrev">
      <div class="yrev"><small>THE PHOTO WAS TAKEN IN</small><b id="ry">${YEAR_MIN}</b><span>You said ${year} · ${dy === 0 ? 'exactly right' : yrs(Math.abs(dy)) + (dy > 0 ? ' too late' : ' too early')}</span></div>
      <div class="facts"><div><small>WHERE · ${distText(dist)} OFF</small><b id="pw">0</b></div><div><small>WHEN · ${dy === 0 ? 'EXACT' : yrs(Math.abs(dy)).toUpperCase() + ' OFF'}</small><b id="pn">0</b></div></div>
      <div class="pts">+<span id="rp">0</span><small> / 1,000</small></div></div>`;
    $('#lower').innerHTML = `<div style="display:flex;flex-direction:column;gap:12px">
      <button class="btn" id="nx2">SEE MY SCORE</button>
      <div class="pincard"><h3>${esc(P.title)}</h3><p>${esc(P.blurb)}</p>${P.now ? `<p class="now">${esc(P.now)}</p>` : ''}</div>
      <p class="credit">Photo: ${esc(P.credit)} · <a href="${esc(P.source)}" target="_blank" rel="noopener">${esc(P.license)}</a></p></div>`;
    $('#nx2').style.visibility = 'hidden';
    window.scrollTo({ top:0, behavior:reduced ? 'auto' : 'smooth' });
    // year flips up to the real one
    const ry = $('#ry'); const t0 = performance.now(), from = YEAR_MIN;
    await new Promise(res => { (function f(now){ const p = Math.min(1, (now - t0) / (reduced ? 1 : 1100)), e = 1 - Math.pow(1 - p, 3); ry.textContent = Math.round(from + (P.year - from) * e); if (p < 1) { if (Math.random() < .35) SFX.tick(); requestAnimationFrame(f); } else res(); })(t0); });
    SFX.stamp(); vibe(40);
    await wait(reduced ? 0 : 300);
    L.polyline([guess, truth], { className:'m-line', interactive:false }).addTo(map);
    L.marker(truth, { icon:L.divIcon({ className:'', html:FLAG_HTML, iconSize:[40,48], iconAnchor:[8,46] }), interactive:false, zIndexOffset:1000 }).addTo(map);
    const mid = L.latLng((guess.lat + truth.lat) / 2, (guess.lng + truth.lng) / 2);
    L.marker(mid, { icon:L.divIcon({ className:'', html:`<div class="dist-chip" style="transform:translate(-50%,-50%)">${distText(dist)}</div>`, iconSize:[0,0] }), interactive:false }).addTo(map);
    map.flyToBounds(L.latLngBounds([guess, truth]), { paddingTopLeft:[50, 80], paddingBottomRight:[60, 40], maxZoom:17, duration:reduced ? 0 : 1.1 });
    SFX.ok(); await wait(reduced ? 0 : 1100);
    addScore(pts, { dist, dy });
    await countUp($('#pw'), place, 500); await countUp($('#pn'), when, 500); await countUp($('#rp'), pts, 500);
    if (pts >= 800) SFX.great(); else if (pts >= 400) SFX.ok(); else SFX.womp();
    const nb = $('#nx2'); nb.style.visibility = ''; nb.onclick = () => { SFX.tap(); next(); };
  };
}


async function results(){
  document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);
  const beat = beatPct(S.total), ok = S.total >= UNLOCK;
  const played = TODAY.n + 1, rank = Math.max(1, Math.round(played * (100 - beat) / 100));
  const avg = Math.round((TODAY.avg * TODAY.n + S.total) / played);
  app.innerHTML = `<section class="screen">${TABS('daily')}
    <div class="card"><div class="top"><span>${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)}</span><span>${esc(DAY.date.toUpperCase())}</span></div>
      <div class="total" id="big">0</div><div class="of">OUT OF 5,000</div>
      <div class="squares">${S.results.map((r, k) => `<div class="sq"><i style="background:${sqColor(r.pts)};animation-delay:${600 + k * 120}ms"></i><span>${SQLAB[r.type]}</span><b>${fmt(r.pts)}</b></div>`).join('')}</div>
      <span class="rankstamp">BEAT ${beat}% OF ${esc(DAY.school.toUpperCase())} TODAY</span></div>
    ${ok
      ? `<div class="gate ok"><b>PRIZE SPIN UNLOCKED</b><span>You needed ${fmt(UNLOCK)}. You got ${fmt(S.total)}.</span></div><button class="btn pulse" id="prize">SPIN FOR YOUR PRIZE</button>`
      : `<div class="gate"><b>${fmt(UNLOCK - S.total)} POINTS SHORT</b><span>You needed ${fmt(UNLOCK)} to unlock the prize spin. New five at 4am, try again tomorrow.</span></div><a class="btn mint" href="party.html">PLAY THE PARTY GAMES</a>`}
    <div class="today"><h3>${esc(DAY.school.toUpperCase())} TODAY</h3>
      <div><small>PLAYED</small><b>${fmt(played)}</b></div><div><small>AVERAGE</small><b>${fmt(avg)}</b></div><div><small>YOU</small><b>#${fmt(rank)}</b></div></div>
    <div class="row2"><button class="btn ghost" id="share">SHARE MY SCORE</button><button class="btn ghost" id="see">SEE THE IMAGE</button></div>
    <div class="cd">NEXT FIVE IN <b id="cd">${nextDropText()}</b></div>
    <p class="demo-note">Demo: player numbers and "beat %" are samples.</p>
  </section>`;
  if (ok) { SFX.fanfare(); vibe([40, 30, 40, 30, 120]); } else { SFX.ok(); vibe(30); }
  countUp($('#big'), S.total, 1500);
  const cdT = setInterval(() => { const e = $('#cd'); if (!e) return clearInterval(cdT); e.textContent = nextDropText(); }, 1000);
  const text = `Off Campus · ${DAY.school} Daily #${pad3(DAY.no)}\n${fmt(S.total)}/5,000 ${S.results.map(r => sqEmoji(r.pts)).join('')}\nBeat ${beat}% of ${DAY.school} today. Can you beat me?`;
  const png = await drawCard(beat);
  const copy = async () => { try { await navigator.clipboard.writeText(text); toast('COPIED, PASTE IT ANYWHERE'); } catch (e) { toast('COULDN\'T COPY'); } };
  $('#see').onclick = () => { SFX.tap(); const d = document.createElement('div'); d.className = 'lightbox'; d.innerHTML = `<img src="${png}" alt="Your score card" style="border-radius:14px;max-height:84vh">`; d.onclick = () => d.remove(); document.body.appendChild(d); };
  $('#share').onclick = async () => { SFX.tap();
    try { const blob = await (await fetch(png)).blob(), file = new File([blob], 'off-campus-daily.png', { type:'image/png' });
      if (navigator.canShare && navigator.canShare({ files:[file] })) { await navigator.share({ files:[file], text }); return; }
      if (navigator.share) { await navigator.share({ text }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
    copy(); };
  if (ok) $('#prize').onclick = () => { SFX.ok(); vibe(20); prize(); };
}


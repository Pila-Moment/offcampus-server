const TABS = on => `<nav class="tabs" aria-label="Off Campus"><a class="home" href="./" aria-label="Off Campus home">OC</a><a href="daily.html" class="${on === 'daily' ? 'on' : ''}">DAILY</a><a href="party.html" class="${on === 'party' ? 'on' : ''}">PARTY GAMES</a><a href="prizes.html" class="${on === 'prizes' ? 'on' : ''}">PRIZES</a></nav>`;
const unlockText = t => t >= UNLOCK ? 'PRIZE SPIN UNLOCKED' : `${fmt(UNLOCK - t)} MORE TO UNLOCK THE PRIZE SPIN`;
function hud(){
  return `<div class="hud"><div class="rn"><small>${KIND[R().type]}</small>ROUND ${S.i + 1}/${DAY.rounds.length}</div>
    <div class="dots">${DAY.rounds.map((_, k) => `<i class="${k < S.i ? 'done' : k === S.i ? 'now' : ''}"></i>`).join('')}</div>
    <div class="score"><small>SCORE</small><span id="tot">${fmt(S.total)}</span></div>${soundBtn()}</div>
    <div class="unlock ${S.total >= UNLOCK ? 'done' : ''}" id="ul"><i style="width:${Math.min(100, S.total / UNLOCK * 100)}%"></i><span>${unlockText(S.total)}</span></div>`;
}
function updUnlock(){
  const u = $('#ul'); if (!u) return;
  u.querySelector('i').style.width = Math.min(100, S.total / UNLOCK * 100) + '%';
  u.querySelector('span').textContent = unlockText(S.total);
  if (S.total >= UNLOCK && !u.classList.contains('done')) { u.classList.add('done'); SFX.ding(); toast('PRIZE SPIN UNLOCKED'); }
}
function next(){
  S.i++;
  if (S.i >= DAY.rounds.length) return results();
  const r = R(); document.body.dataset.mode = r.type;
  window.scrollTo(0, 0);
  if (r.type === 'receipts') receipts(); else if (r.type === 'survey') survey(); else pinRound();
}
function addScore(n, detail){ S.results.push({ type:R().type, pts:n, ...detail }); const from = S.total; S.total += n; countUp($('#tot'), S.total, 700, from); setTimeout(updUnlock, 750); }

/* ================= intro ================= */
function intro(){
  fresh(); document.body.dataset.mode = 'intro'; window.scrollTo(0, 0);
  app.innerHTML = `<section class="screen intro">${TABS('daily')}
    <div class="kick">${esc(DAY.school.toUpperCase())} DAILY · NO. ${pad3(DAY.no)} · ${esc(DAY.date.toUpperCase())}</div>
    <h1>TODAY'S <span>FIVE</span></h1>
    <p class="sub">Five rounds about ${esc(DAY.school)}, about three minutes. Everyone at ${esc(DAY.school)} gets the same five today.</p>
    <div class="goal"><b>${fmt(UNLOCK)}</b><span>Score ${fmt(UNLOCK)} out of 5,000 to unlock today's <em>free prize spin</em>.</span></div>
    <ol class="lineup">
      <li><span class="tag t-r">RECEIPTS</span>Yes or no, then guess what % said yes</li>
      <li><span class="tag t-s">SHOWDOWN</span>Name the top answers before 3 X's</li>
      <li><span class="tag t-r">RECEIPTS</span>Another one, a little spicier</li>
      <li><span class="tag t-s">SHOWDOWN</span>Another board</li>
      <li><span class="tag t-p">DROP PIN</span>Where and when was this photo taken?</li>
    </ol>
    <button class="btn pulse" id="go">PLAY TODAY'S 5</button>
    <p class="demo-note">Demo build. Percentages, survey boards, player numbers and prizes are samples.</p>
  </section>`;
  $('#go').onclick = () => { SFX.ok(); vibe(20); next(); };
}


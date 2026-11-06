/* ================= CREWS: friend groups that compare today's scores =================
   Talks to the Crews API on the same site (Netlify Function). If CREWS_API is empty, Crews stay hidden and the game works as before. */
const CREWS_API = (() => { const t = new URLSearchParams(location.search).get('api'); if (t && /^http:\/\/localhost:\d+$/.test(t)) return t; return CREWS_URL; })();
const CREW_INVITE_BASE = 'https://offcampusontario.ca/daily.html';
const randId = () => { const a = new Uint8Array(15); (crypto.getRandomValues ? crypto.getRandomValues(a) : a.forEach((_, i) => a[i] = Math.random() * 256)); return Array.from(a, b => 'abcdefghijklmnopqrstuvwxyz0123456789'[b % 36]).join(''); };
const PLAYER_ID = (() => { let id = store.get('oc-pid'); if (!id || !/^[a-z0-9]{12,40}$/.test(id)) { id = randId() + randId().slice(0, 5); store.set('oc-pid', id); } return id; })();
const getNick = () => store.get('oc-nick') || '';
const INVITE_CODE = (() => { const c = (new URLSearchParams(location.search).get('crew') || '').toUpperCase(); return /^[A-Z0-9]{6}$/.test(c) ? c : ''; })();
async function api(method, p, body){
  if (!CREWS_API) throw new Error('off');
  const ctl = new AbortController(); const t = setTimeout(() => ctl.abort(), 8000);
  try { const r = await fetch(CREWS_API + p, { method, headers: body ? { 'Content-Type':'application/json' } : {}, body: body ? JSON.stringify(body) : undefined, signal: ctl.signal });
    const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.error || 'error'); return j; }
  finally { clearTimeout(t); }
}
async function postScore(rec){ try { await api('POST', '/api/score', { playerId:PLAYER_ID, nick:getNick(), day:DAY.no, total:rec.total, pts:rec.pts }); } catch (e) {} }

function crewBoardHTML(c){
  const shown = c.members.map((m, i) => ({ m, i })).filter(({ m, i }) => i < CREW_ROWS - 1 || m.you || (i === CREW_ROWS - 1 && !c.members.slice(CREW_ROWS).some(x => x.you)));
  const rows = shown.map(({ m, i }) => `<li class="${m.you ? 'me' : ''} ${m.total === null ? 'wait' : ''}"><span class="rk">${m.total === null ? '–' : i + 1}</span><span class="nk">${esc(m.nick)}${m.you ? ' <em>YOU</em>' : ''}${m.streak >= 2 ? ` <i>${m.streak}-day streak</i>` : ''}</span><b>${m.total === null ? 'not played yet' : fmt(m.total)}</b></li>`).join('');
  const hidden = c.size - shown.length;
  const waiting = c.size - c.played;
  return `<div class="crew" data-code="${c.code}"><div class="ch"><b>${esc(c.name)}</b><span>${c.played} / ${c.size} PLAYED TODAY</span></div>
    <ol>${rows}</ol>${hidden > 0 ? `<p class="cnote">+ ${hidden} more in the crew</p>` : ''}
    ${c.size < 2 ? `<p class="cnote">Just you so far. Send the invite to your house, floor or friends.</p>` : waiting ? `<p class="cnote">${waiting} ${waiting === 1 ? "hasn't" : "haven't"} played yet. Give them a nudge.</p>` : ''}
    <button class="btn ghost inv" data-code="${c.code}" data-name="${esc(c.name)}">INVITE TO ${esc(c.name.toUpperCase())}</button></div>`;
}
function newCrewFormHTML(first){
  return `<form class="crewform" id="crewform" autocomplete="off">${first ? `<b class="cf-h">PLAY WITH YOUR FRIENDS</b><p>Start a crew for your house, floor or friends. Everyone plays on their own phone, and you see who won today.</p>` : `<b class="cf-h">START ANOTHER CREW</b>`}
    <input id="cfName" maxlength="28" placeholder="Crew name, e.g. The Princess St House" required>
    ${getNick() ? '' : '<input id="cfNick" maxlength="16" placeholder="Your nickname" required>'}
    <button class="btn" type="submit">START A CREW</button></form>`;
}
const CREW_ROWS = 5;   // rows shown per crew board before "+N more"
function crewCtaHTML(){
  return `<button class="crewcta" id="crewcta" type="button"><b>PLAY WITH FRIENDS</b><span>Start a crew for your house or floor. See who wins today.</span><i>START A CREW</i></button>`;
}
async function renderCrews(el, myScore){
  if (!CREWS_API || !el) return;
  if (!el.innerHTML) el.innerHTML = `<div class="crews">${crewCtaHTML()}</div>`;
  let me; try { me = await api('GET', '/api/me?playerId=' + PLAYER_ID); } catch (e) { el.innerHTML = ''; return; }
  const crews = me.crews || [];
  el.innerHTML = `<div class="crews">${crews.length ? crews.map(crewBoardHTML).join('') + `<details class="more"><summary>+ START ANOTHER CREW</summary>${newCrewFormHTML(false)}</details>` : crewCtaHTML()}</div>`;
  el.querySelectorAll('.inv').forEach(b => b.onclick = () => invite(b.dataset.code, b.dataset.name, myScore));
  const cta = el.querySelector('#crewcta');
  if (cta) cta.onclick = () => { SFX.tap(); vibe(15); track('crew-open'); cta.outerHTML = newCrewFormHTML(true); wireForm(); const n = el.querySelector('#cfName'); if (n) n.focus(); };
  const wireForm = () => {
    const f = el.querySelector('#crewform'); if (!f) return;
    f.onsubmit = async e => {
      e.preventDefault(); const name = el.querySelector('#cfName').value.trim(); const nk = el.querySelector('#cfNick'); if (nk) { const v = nk.value.trim(); if (!v) return; store.set('oc-nick', v); }
      if (!name) return; const btn = f.querySelector('button'); btn.disabled = true; btn.textContent = 'STARTING…';
      try { const c = await api('POST', '/api/crews', { playerId:PLAYER_ID, nick:getNick(), name }); SFX.ok(); track('crew-start');
        const rec = store.get(PLAY_KEY); if (rec) await postScore(rec);
        await renderCrews(el, myScore); invite(c.code, c.name, myScore); }
      catch (err) { btn.disabled = false; btn.textContent = 'START A CREW'; toast('COULDN\'T START IT, TRY AGAIN'); }
    };
  };
  wireForm();
}
async function invite(code, name, myScore){
  SFX.tap(); track('crew-invite');
  const url = `${CREW_INVITE_BASE}?crew=${code}&ref=crew`;
  const text = myScore ? `Join "${name}" on Off Campus. I got ${fmt(myScore)} today. Beat me:` : `Join "${name}" on Off Campus, the daily game for Queen's. Let's see who wins today:`;
  try { if (navigator.share) { await navigator.share({ text, url }); return; } } catch (e) { if (e && e.name === 'AbortError') return; }
  try { await navigator.clipboard.writeText(text + ' ' + url); toast('INVITE LINK COPIED'); } catch (e) { toast(url); }
}
async function joinCard(el){
  if (!CREWS_API || !INVITE_CODE || !el) return;
  let c; try { c = await api('GET', `/api/crews/${INVITE_CODE}?playerId=${PLAYER_ID}`); } catch (e) { return; }
  if (c.members.some(m => m.you)) { el.innerHTML = `<div class="joincard in"><b>YOU'RE IN ${esc(c.name.toUpperCase())}</b><span>${c.played} of ${c.size} have played today.</span></div>`; return; }
  const top = c.members.find(m => m.total !== null);
  el.innerHTML = `<form class="joincard" id="joinf" autocomplete="off"><small>YOU'VE BEEN INVITED TO</small><b>${esc(c.name.toUpperCase())}</b>
    <span>${c.size} ${c.size === 1 ? 'player' : 'players'}${top ? ` · ${esc(top.nick)} leads with ${fmt(top.total)} today` : ''}</span>
    ${getNick() ? '' : '<input id="jfNick" maxlength="16" placeholder="Your nickname" required>'}
    <button class="btn" type="submit">JOIN THE CREW</button></form>`;
  el.querySelector('#joinf').onsubmit = async e => {
    e.preventDefault(); const nk = el.querySelector('#jfNick'); if (nk) { const v = nk.value.trim(); if (!v) return; store.set('oc-nick', v); }
    try { const j = await api('POST', `/api/crews/${INVITE_CODE}/join`, { playerId:PLAYER_ID, nick:getNick() }); SFX.ding(); track('crew-join');
      el.innerHTML = `<div class="joincard in"><b>YOU'RE IN ${esc(j.name.toUpperCase())}</b><span>Play today's five and your score shows up on the crew board.</span></div>`;
      const rec = store.get(PLAY_KEY); if (rec) { await postScore(rec); const cr = $('#crewsbox'); if (cr) renderCrews(cr, rec.total); } }
    catch (err) { toast('COULDN\'T JOIN, TRY AGAIN'); }
  };
}


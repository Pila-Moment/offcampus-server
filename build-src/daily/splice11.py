# Save your spot (Nov 4): nickname + 4-digit PIN so the same person is the same player in Instagram's browser,
# Safari and on another phone. Save sheet pops up after a game (until saved); PLAYED BEFORE? LOG IN on the start screen.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)

rep("function newCrewFormHTML(first){", r'''/* ================= SAVE YOUR SPOT (name + PIN) ================= */
const IN_INSTAGRAM = /Instagram/i.test(navigator.userAgent);
function sheet(html){
  const d = document.createElement('div'); d.className = 'sheet-bg'; d.innerHTML = `<div class="sheet" role="dialog">${html}</div>`;
  d.addEventListener('click', e => { if (e.target === d) d.remove(); }); document.body.appendChild(d); return d;
}
const pinInput = id => `<input id="${id}" class="pin" inputmode="numeric" pattern="[0-9]*" maxlength="4" autocomplete="off" placeholder="4-number PIN" required>`;
function saveSheet(){
  if (!CREWS_API || GUEST || store.get('oc-saved')) return;
  const d = sheet(`<b class="sh-h">SAVE YOUR STREAK</b><p>Pick a name and a 4-number PIN. Then you can log in on any phone or browser, even inside Instagram, and keep your crew and streak.</p>
    <form id="svf" autocomplete="off"><input id="svn" maxlength="16" placeholder="Your name" value="${esc(getNick())}" required>${pinInput('svp')}<button class="btn" type="submit">SAVE IT</button></form>
    <button class="sh-later" id="svl" type="button">LATER</button>`);
  track('save-shown');
  d.querySelector('#svl').onclick = () => { store.set('oc-savelater', DAY.no); d.remove(); };
  d.querySelector('#svf').onsubmit = async e => {
    e.preventDefault(); const nick = d.querySelector('#svn').value.trim(), pin = d.querySelector('#svp').value.trim();
    if (!/^\d{4}$/.test(pin)) { toast('PIN IS 4 NUMBERS'); return; }
    const btn = d.querySelector('#svf button'); btn.disabled = true; btn.textContent = 'SAVING…';
    try { await api('POST', '/api/pin', { playerId:PLAYER_ID, nick, pin }); store.set('oc-saved', 1); store.set('oc-nick', nick); track('save-done'); SFX.ok(); d.remove(); toast('SAVED. LOG IN ANYWHERE'); }
    catch (err) { btn.disabled = false; btn.textContent = 'SAVE IT'; toast(/taken/.test(err.message) ? 'NAME TAKEN, TRY ANOTHER' : 'COULDN\'T SAVE, TRY AGAIN'); }
  };
}
function loginSheet(){
  const d = sheet(`<b class="sh-h">WELCOME BACK</b><p>Log in with the name and PIN you saved. Your crew, streak and today's score come with you.</p>
    <form id="lgf" autocomplete="off"><input id="lgn" maxlength="16" placeholder="Your name" required>${pinInput('lgp')}<button class="btn" type="submit">LOG IN</button></form>
    <button class="sh-later" id="lgx" type="button">CANCEL</button>`);
  d.querySelector('#lgx').onclick = () => d.remove();
  d.querySelector('#lgf').onsubmit = async e => {
    e.preventDefault(); const btn = d.querySelector('#lgf button'); btn.disabled = true; btn.textContent = 'CHECKING…';
    try {
      const r = await api('POST', '/api/login', { nick:d.querySelector('#lgn').value.trim(), pin:d.querySelector('#lgp').value.trim() });
      store.set('oc-pid', r.playerId); store.set('oc-nick', r.nick); store.set('oc-saved', 1); track('login');
      if (r.streak) store.set('oc-streak', r.streak);
      if (r.today) store.set(PLAY_KEY, { total:r.today.total, pts:r.today.pts, types:['receipts','survey','receipts','survey','pin'] });
      location.href = location.pathname;   // reload as that player
    } catch (err) { btn.disabled = false; btn.textContent = 'LOG IN'; toast(/too many/.test(err.message) ? 'TOO MANY TRIES, WAIT A BIT' : 'WRONG NAME OR PIN'); }
  };
}

function newCrewFormHTML(first){''')
# results: offer to save after the score has counted up (once a day until saved)
rep("  if (ok) $('#prize').onclick = () => { SFX.ok(); vibe(20); live ? prize() : prizeTeaser(); };",
    "  if (ok) $('#prize').onclick = () => { SFX.ok(); vibe(20); live ? prize() : prizeTeaser(); };\n  if (!GUEST && store.get('oc-savelater') !== DAY.no) setTimeout(saveSheet, 2600);")
# server says this player already saved (e.g. logged in before)
rep("  let me; try { me = await api('GET', '/api/me?playerId=' + PLAYER_ID); } catch (e) { el.innerHTML = ''; return; }",
    "  let me; try { me = await api('GET', '/api/me?playerId=' + PLAYER_ID); } catch (e) { el.innerHTML = ''; return; }\n  if (me.saved) store.set('oc-saved', 1);")
# start screen: log-in link + Instagram tip
rep('''    <p class="demo-note">Free to play. One go per day. A new five every day at 4am.</p>''',
'''    <p class="demo-note">${IN_INSTAGRAM && !store.get('oc-saved') ? 'In Instagram? Tap ⋯ then Open in browser so your streak saves.' : 'Free to play. One go per day. A new five every day at 4am.'}${CREWS_API && !GUEST && !store.get('oc-saved') ? ' <button class="linkbtn" id="login" type="button">PLAYED BEFORE? LOG IN</button>' : ''}</p>''')
rep("  $('#go').onclick = () => { SFX.ok(); vibe(20); track('start'); next(); };",
    "  $('#go').onclick = () => { SFX.ok(); vibe(20); track('start'); next(); };\n  const lg = $('#login'); if (lg) lg.onclick = () => { SFX.tap(); loginSheet(); };")
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>", """/* save your spot */
.sheet-bg{position:fixed;inset:0;z-index:70;display:flex;align-items:flex-end;justify-content:center;background:color-mix(in srgb, var(--night) 70%, transparent);animation:screenin .25s var(--ease-out)}
.sheet{box-sizing:border-box;width:100%;max-width:560px;display:flex;flex-direction:column;gap:10px;padding:20px 18px max(20px, env(safe-area-inset-bottom, 0px));border-radius:22px 22px 0 0;background:var(--night-2);box-shadow:0 -2px 0 var(--mint)}
.sheet .sh-h{font-family:var(--display);font-weight:400;font-size:24px;color:var(--mint)}
.sheet p{margin:0;font-size:13px;font-weight:600;line-height:1.45;color:var(--muted)}
.sheet form{display:flex;flex-direction:column;gap:9px}
.sheet input{box-sizing:border-box;width:100%;height:52px;border:0;border-radius:12px;padding:0 14px;background:var(--cream);color:var(--ink);font:700 17px var(--mono)}
.sheet input.pin{letter-spacing:.5em;text-align:center}
.sheet .btn{min-height:54px;font-size:18px}
.sh-later{min-height:44px;color:var(--muted);font:700 12px var(--mono);letter-spacing:.14em}
.linkbtn{display:inline;min-height:0;padding:6px 2px;color:var(--mint);font:700 11px var(--mono);letter-spacing:.06em;text-decoration:underline}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice11 ok')

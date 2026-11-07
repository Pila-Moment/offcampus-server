# House League (Nov 7): after the Daily, show how today's score helped your house, with a way to the standings and to invite a roommate.
# The intro gets one small line for players already in a house. Crews keep working and are worded as the casual option.
s = open('src.html').read()
def rep(a, b, n=1):
    global s
    assert s.count(a) == n, ('COUNT %d: ' % s.count(a)) + a[:100]
    s = s.replace(a, b)

rep('.linkbtn{', '''.hstrip{display:flex;align-items:center;gap:10px;min-height:58px;padding:8px 10px 8px 12px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px color-mix(in srgb, var(--c, var(--gold)) 70%, transparent);color:var(--text);text-decoration:none;animation:hsin .5s var(--ease-pop) both}
@keyframes hsin{from{opacity:0;transform:translateY(8px) scale(.98)}}
.hstrip .hc{position:relative;flex:0 0 34px;height:37px;display:grid;place-items:end center;padding-bottom:5px;color:var(--ink);font-family:var(--display);font-size:13px;line-height:1}
.hstrip .hc::before{content:"";position:absolute;inset:0;background:var(--c, var(--gold));clip-path:polygon(50% 0, 100% 38%, 100% 100%, 0 100%, 0 38%)}
.hstrip .hc b{position:relative;font-weight:400}
.hstrip .ht{flex:1;min-width:0;display:flex;flex-direction:column;gap:2px;color:inherit;text-decoration:none}
.hstrip .ht b{font-family:var(--display);font-weight:400;font-size:14px;line-height:1.05;overflow-wrap:anywhere}
.hstrip .ht small{font-size:11px;font-weight:600;line-height:1.3;color:var(--muted)}
.hstrip .ht small em{font-style:normal;color:var(--c, var(--gold))}
.hstrip.warn{box-shadow:inset 0 0 0 2px var(--red)}
.hstrip i,.hstrip button{flex:0 0 auto;min-height:44px;padding:0 12px;border-radius:12px;background:var(--c, var(--gold));color:var(--ink);font-style:normal;font-family:var(--display);font-size:13px;display:grid;place-items:center}
@media (max-height:900px){.hstrip{min-height:48px;padding:2px 6px 2px 10px}.hstrip .ht small{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.hstrip .hc{flex-basis:28px;height:30px;font-size:11px}#housebox:has(.hstrip) ~ .cd .tmrw{display:none}}
@media (max-height:700px){#housebox:has(.hstrip) ~ #crewsbox .crew .cmeta{display:none}}
#housebox:empty,#housechip:empty{display:none}
.hchip{display:flex;align-items:center;gap:8px;min-height:44px;padding:0 12px;border-radius:12px;background:var(--night-2);box-shadow:inset 0 0 0 1.5px color-mix(in srgb, var(--c, var(--gold)) 60%, transparent);color:var(--text);text-decoration:none;font-size:11.5px;font-weight:700;letter-spacing:.06em}
.hchip em{font-style:normal;color:var(--c, var(--gold))}
.hchip span{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.linkbtn{''')

# ---------- the house strip ----------
rep("/* ================= SEND A QUESTION TO A FRIEND", r'''/* ================= HOUSE LEAGUE ================= */
const HOUSE_SITE = /(^|\.)offcampusontario\.ca$/.test(location.hostname) ? 'https://offcampusontario.ca' : location.origin;   // a preview's invites stay on that preview
const housePage = q => 'house.html' + (q || '') + (CREWS_API && CREWS_API !== CREWS_URL ? (q ? '&' : '?') + 'api=' + encodeURIComponent(CREWS_API) : '');
const hcol = c => `var(--${/^[a-z]+$/.test(c || '') ? c : 'gold'}, var(--gold))`;
// o = { posted:true|false (did POST /api/score succeed), rec:{ total, pts } }. "Counted" only ever comes from the server's own answer.
async function houseStrip(el, o = {}){
  if (!CREWS_API || GUEST || !el) return;
  const retry = msg => { el.innerHTML = `<div class="hstrip warn"><span class="hc"><b>!</b></span><span class="ht"><b>${msg}</b><small>Your score is saved on this phone. Tap to send it again.</small></span><button type="button" id="hretry">TRY AGAIN</button></div>`;
    $('#hretry').onclick = async () => { SFX.tap(); const b = $('#hretry'); b.disabled = true; b.textContent = '…'; const ok2 = await postScore(o.rec); houseStrip(el, { ...o, posted:ok2 }); }; };
  let L; try { L = await api('GET', '/api/league?playerId=' + PLAYER_ID); } catch (e) { if (o.posted === false && o.rec) retry('YOUR SCORE HASN\'T SAVED YET'); return; }
  const m = L.mine;
  if (!m) { if (o.posted === false && o.rec) return retry('YOUR SCORE HASN\'T SAVED YET'); if (document.querySelector('#crewsbox .crew')) return;   // already in a crew: the HOUSES tab is enough
    el.innerHTML = `<a class="hstrip" href="${housePage()}"><span class="hc"><b>+</b></span><span class="ht"><b>QUEEN'S HOUSE LEAGUE</b><small>Your house vs every house at Queen's. Start one with your roommates.</small></span><i>START</i></a>`; return; }
  if (!m.playedToday && o.rec) return retry(`NOT COUNTED FOR ${esc(m.name.toUpperCase())} YET`);
  const R = L.rival, inv = `<button type="button" id="hinv">INVITE</button>`;
  let head, line;
  if (m.countsElsewhere) { head = esc(m.name.toUpperCase()); line = `This week you count for ${esc(m.countsFor || 'your old house')}. From Monday, for ${esc(m.name)}.`; }
  else if (!m.todayCounted) { head = esc(m.name.toUpperCase()); line = `${m.players} of ${L.minPlayers} players this week`; }
  else { head = 'TODAY COUNTED FOR ' + esc(m.name.toUpperCase());
    line = !m.qualified ? `<em>${m.players} of ${L.minPlayers}</em> players · ${m.need} more to enter the league`
      : R && R.dir === 'chase' ? `<em>#${m.rank}</em> · ${R.gap.toFixed(1)} behind ${esc(R.name)} · new five at 4am`
      : R ? `<em>#${m.rank}</em> · ${R.gap.toFixed(1)} ahead of ${esc(R.name)} · defend it tomorrow`
      : `<em>#${m.rank}</em> of ${L.ranked.length} this week · new five at 4am`; }
  el.innerHTML = `<div class="hstrip" style="--c:${hcol(m.color)}"><span class="hc"><b>${esc(m.mono)}</b></span><a class="ht" href="${housePage()}"><b>${head}</b><small>${line}</small></a>${inv}</div>`;
  $('#hinv').onclick = () => { SFX.tap(); track('house-invite'); shareText(houseInviteMsg(m), `${HOUSE_SITE}/house.html?join=${m.code}&ref=house`, 'COPIED, SEND IT TO YOUR ROOMMATES'); };
}
const houseInviteMsg = m => m.qualified ? `${m.name} is #${m.rank} in the Queen's House League. Join the house and play today's five (3 min) to push us up:` : `${m.name} needs ${m.need || 1} more ${m.need === 1 ? 'player' : 'players'} to get into the Queen's House League. Tap to join, then play today's five (3 min):`;
async function houseChip(el){
  if (!CREWS_API || GUEST || !el) return;
  let L; try { L = await api('GET', '/api/league?playerId=' + PLAYER_ID); } catch (e) { return; }
  const m = L.mine; if (!m) return;
  el.innerHTML = `<a class="hchip" href="${housePage()}" style="--c:${hcol(m.color)}"><em>HOUSE</em><span>${esc(m.name.toUpperCase())} · ${m.qualified ? `#${m.rank} THIS WEEK` : `${m.players} OF ${L.minPlayers} PLAYERS`}</span><em>&rarr;</em></a>`;
}

/* ================= SEND A QUESTION TO A FRIEND''')
rep("${GUEST ? '' : '<div id=\"crewsbox\"></div>'}", "${GUEST ? '' : '<div id=\"housebox\"></div><div id=\"crewsbox\"></div>'}")
rep('    <div id="crewsbox"></div>', '    <div id="housebox"></div><div id="crewsbox"></div>')
rep("if (!GUEST) postScore({ total:S.total, pts }).then(() => renderCrews($('#crewsbox'), S.total));",
    "if (!GUEST) postScore({ total:S.total, pts }).then(ok => renderCrews($('#crewsbox'), S.total).then(() => houseStrip($('#housebox'), { posted:ok, rec:{ total:S.total, pts } })));")
rep("  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total));", "  postScore(rec).then(ok => renderCrews($('#crewsbox'), rec.total).then(() => houseStrip($('#housebox'), { posted:ok, rec })));")
rep('<div id="joinbox"></div><div id="crewstrip"></div>', '<div id="joinbox"></div><div id="housechip"></div><div id="crewstrip"></div>')
rep("if (!GUEST) { joinCard($('#joinbox')); crewStrip($('#crewstrip')); }", "if (!GUEST) { joinCard($('#joinbox')); houseChip($('#housechip')); crewStrip($('#crewstrip')); }")
# crews are the casual option now; houses are the league
rep('<b>START A CREW FOR YOUR HOUSE</b><span>Who wins the week? Loser cleans the kitchen.</span><i>START</i>', '<b>START A CREW</b><span>A casual scoreboard for any group of friends.</span><i>START</i>')

# the Daily's top tabs: HOUSES takes the CLUBS spot (clubs are still on the home page)
rep('<a href="clubs.html" class="${on === \'clubs\' ? \'on\' : \'\'}">CLUBS</a></nav>', '<a href="${housePage()}">HOUSES</a></nav>')
rep("async function postScore(rec){ try { await api('POST', '/api/score', { playerId:PLAYER_ID, nick:getNick(), day:DAY.no, total:rec.total, pts:rec.pts, src:SRC }); } catch (e) {} }",
    "async function postScore(rec){ try { await api('POST', '/api/score', { playerId:PLAYER_ID, nick:getNick(), day:DAY.no, total:rec.total, pts:rec.pts, src:SRC }); return true; } catch (e) { return false; } }   // true only when the server saved it")
open('src.html', 'w').write(s)
print('splice15 ok')

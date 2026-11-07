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
.hstrip i,.hstrip button{flex:0 0 auto;min-height:44px;padding:0 12px;border-radius:12px;background:var(--c, var(--gold));color:var(--ink);font-style:normal;font-family:var(--display);font-size:13px;display:grid;place-items:center}
@media (max-height:900px){.hstrip{min-height:48px;padding:2px 6px 2px 10px}.hstrip .ht small{display:none}.hstrip .hc{flex-basis:28px;height:30px;font-size:11px}#housebox:has(.hstrip) ~ .cd .tmrw{display:none}}
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
async function houseStrip(el){
  if (!CREWS_API || GUEST || !el) return;
  let L; try { L = await api('GET', '/api/league?playerId=' + PLAYER_ID); } catch (e) { return; }
  const m = L.mine;
  if (!m) { if (document.querySelector('#crewsbox .crew')) return;   // already in a crew: the HOUSES tab is enough
    el.innerHTML = `<a class="hstrip" href="${housePage()}"><span class="hc"><b>+</b></span><span class="ht"><b>QUEEN'S HOUSE LEAGUE</b><small>Your house vs every house at Queen's. Start one with your roommates.</small></span><i>START</i></a>`; return; }
  const line = m.countsElsewhere ? `You count for ${esc(m.name)} from Monday`
    : m.qualified ? `#${m.rank} of ${L.ranked.length} this week · ${m.pct.toFixed(1)}% house average`
    : `${m.players} of ${L.minPlayers} players this week · ${m.need} more to enter the league`;
  el.innerHTML = `<div class="hstrip" style="--c:${hcol(m.color)}"><span class="hc"><b>${esc(m.mono)}</b></span><a class="ht" href="${housePage()}"><b>${m.countsElsewhere ? esc(m.name.toUpperCase()) : 'TODAY COUNTED FOR ' + esc(m.name.toUpperCase())}</b><small>${line} · SEE THE LEAGUE &rarr;</small></a><button type="button" id="hinv">INVITE</button></div>`;
  $('#hinv').onclick = () => { SFX.tap(); track('house-invite'); shareText(`Join ${m.name} in the Queen's House League. Play the Daily and your score counts for the house:`, `${HOUSE_SITE}/house.html?join=${m.code}&ref=house`, 'COPIED, SEND IT TO YOUR ROOMMATES'); };
}
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
    "if (!GUEST) postScore({ total:S.total, pts }).then(() => renderCrews($('#crewsbox'), S.total)).then(() => houseStrip($('#housebox')));")
rep("  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total));", "  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total)).then(() => houseStrip($('#housebox')));")
rep('<div id="joinbox"></div><div id="crewstrip"></div>', '<div id="joinbox"></div><div id="housechip"></div><div id="crewstrip"></div>')
rep("if (!GUEST) { joinCard($('#joinbox')); crewStrip($('#crewstrip')); }", "if (!GUEST) { joinCard($('#joinbox')); houseChip($('#housechip')); crewStrip($('#crewstrip')); }")
# crews are the casual option now; houses are the league
rep('<b>START A CREW FOR YOUR HOUSE</b><span>Who wins the week? Loser cleans the kitchen.</span><i>START</i>', '<b>START A CREW</b><span>A casual scoreboard for any group of friends.</span><i>START</i>')

# the Daily's top tabs: HOUSES takes the CLUBS spot (clubs are still on the home page)
rep('<a href="clubs.html" class="${on === \'clubs\' ? \'on\' : \'\'}">CLUBS</a></nav>', '<a href="${housePage()}">HOUSES</a></nav>')
open('src.html', 'w').write(s)
print('splice15 ok')

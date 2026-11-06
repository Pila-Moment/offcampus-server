# Crews: crew boards on the results and played-today screens, invite links, join card.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:70]; s=s.replace(a,b,1)
rep("const PRIZES_LIVE = false;", "const PRIZES_LIVE = false;\nconst CREWS_URL = /(^|\\.)offcampusontario\\.ca$|\\.netlify\\.app$/.test(location.hostname) ? location.origin : '';   // Crews run on the same site (Netlify). Anywhere else, Crews stay hidden.")
rep("/* ================= SCORE CARD, RESULTS, ALREADY-PLAYED SCREEN", open('parts/crews.js').read() + "/* ================= SCORE CARD, RESULTS, ALREADY-PLAYED SCREEN")
# results
rep("      <span class=\"rankstamp\">${esc(stamp)}</span></div>\n    ${ok", "      <span class=\"rankstamp\">${esc(stamp)}</span></div>\n    ${GUEST ? '' : '<div id=\"crewsbox\"></div>'}\n    ${ok")
rep("  wireShare(S.total, pts, types, stamp);\n  if (ok)", "  wireShare(S.total, pts, types, stamp);\n  if (!GUEST) postScore({ total:S.total, pts }).then(() => renderCrews($('#crewsbox'), S.total));\n  if (ok)")
# done screen
rep("    <div class=\"kick\">YOU'VE PLAYED TODAY'S FIVE</div>", "    <div id=\"joinbox\"></div>\n    <div class=\"kick\">YOU'VE PLAYED TODAY'S FIVE</div>")
rep("      <span class=\"rankstamp\" style=\"animation-delay:0s\">${esc(stamp)}</span></div>\n    ${statsRow(st)}", "      <span class=\"rankstamp\" style=\"animation-delay:0s\">${esc(stamp)}</span></div>\n    <div id=\"crewsbox\"></div>\n    ${statsRow(st)}")
rep("  startCountdown();\n  wireShare(rec.total, rec.pts, rec.types, stamp);\n}", "  startCountdown();\n  wireShare(rec.total, rec.pts, rec.types, stamp);\n  joinCard($('#joinbox'));\n  postScore(rec).then(() => renderCrews($('#crewsbox'), rec.total));\n}")
# intro: join card
rep("    <div class=\"five\" aria-label=\"Today's rounds\">", "    <div id=\"joinbox\"></div>\n    <div class=\"five\" aria-label=\"Today's rounds\">")
rep("  const sk = $('#skip'); if (sk) sk.onclick", "  if (!GUEST) joinCard($('#joinbox'));\n  const sk = $('#skip'); if (sk) sk.onclick")
rep("@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}\n</style>",
"""/* crews */
.crews{display:flex;flex-direction:column;gap:10px}
.crew{display:flex;flex-direction:column;gap:10px;padding:14px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--mint)}
.crew .ch{display:flex;justify-content:space-between;align-items:baseline;gap:10px}
.crew .ch b{font-family:var(--display);font-weight:400;font-size:18px;line-height:1.1}
.crew .ch span{flex:0 0 auto;font-size:10.5px;font-weight:700;letter-spacing:.12em;color:var(--mint)}
.crew ol{margin:0;padding:0;list-style:none;display:grid;gap:6px}
.crew li{display:flex;align-items:center;gap:10px;padding:9px 10px;border-radius:10px;background:var(--night)}
.crew li.me{box-shadow:inset 0 0 0 2px var(--gold)}
.crew li.wait{opacity:.6}
.crew .rk{flex:0 0 22px;font-family:var(--display);font-size:16px;color:var(--gold)}
.crew .nk{flex:1;min-width:0;font-size:13.5px;font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.crew .nk em{font-style:normal;font-size:9.5px;letter-spacing:.12em;padding:2px 5px;border-radius:4px;background:var(--gold);color:var(--ink);vertical-align:2px}
.crew .nk i{font-style:normal;font-size:10.5px;color:var(--red);font-weight:700}
.crew li b{font-family:var(--display);font-weight:400;font-size:15px;font-variant-numeric:tabular-nums}
.crew li.wait b{font-family:var(--mono);font-size:11px;font-weight:700;color:var(--muted)}
.cnote{margin:0;font-size:12px;font-weight:600;line-height:1.4;color:var(--muted)}
.crew .inv{min-height:48px;font-size:14px;color:var(--text)}
.crewform{display:flex;flex-direction:column;gap:10px;padding:14px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--mint)}
.crewform .cf-h{font-family:var(--display);font-weight:400;font-size:18px;color:var(--mint)}
.crewform p{margin:0;font-size:13px;font-weight:600;line-height:1.45;color:var(--muted)}
.crewform input,.joincard input{box-sizing:border-box;width:100%;height:50px;border:0;border-radius:12px;padding:0 14px;background:var(--cream);color:var(--ink);font:600 15px var(--mono)}
.crewform .btn,.joincard .btn{min-height:52px;font-size:17px}
.more summary{cursor:pointer;list-style:none;font-size:12px;font-weight:700;letter-spacing:.12em;color:var(--mint);padding:8px 0}
.more summary::-webkit-details-marker{display:none}
.joincard{display:flex;flex-direction:column;gap:8px;padding:14px;border-radius:16px;background:var(--mint);color:var(--ink)}
.joincard small{font-size:10.5px;font-weight:700;letter-spacing:.16em}
.joincard b{font-family:var(--display);font-weight:400;font-size:22px;line-height:1.05}
.joincard span{font-size:12.5px;font-weight:700}
.joincard.in{background:var(--night-2);color:var(--text);box-shadow:inset 0 0 0 2px var(--mint)}
.joincard.in b{color:var(--mint);font-size:18px}
.crewcta{all:unset;box-sizing:border-box;width:100%;display:grid;grid-template-columns:1fr auto;align-items:center;gap:2px 12px;padding:12px 14px;border-radius:16px;background:var(--night-2);box-shadow:inset 0 0 0 2px var(--mint);cursor:pointer;min-height:64px;-webkit-tap-highlight-color:transparent}
.crewcta b{grid-column:1;font-family:var(--display);font-weight:400;font-size:19px;line-height:1.05;color:var(--mint)}
.crewcta span{grid-column:1;font-size:11.5px;font-weight:600;line-height:1.35;color:var(--muted)}
.crewcta i{grid-column:2;grid-row:1 / span 2;font-style:normal;font-family:var(--display);font-size:15px;padding:11px 12px;border-radius:12px;background:var(--mint);color:var(--ink);white-space:nowrap}
.crewcta:active{transform:scale(.98)}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}
</style>""")
open('src.html','w').write(s)
print('splice5 ok')

# No prize talk for players (Nov 4): until real prizes are live, the daily never mentions prizes.
# Brand preview links (GUEST) still show the prize spin, because that's what the business is looking at.
s=open('src.html').read()
def rep(a,b):
    global s
    assert a in s, a[:90]; s=s.replace(a,b,1)
rep('<a href="prizes.html" class="${on === \'prizes\' ? \'on\' : \'\'}">PRIZES</a>', '<a href="clubs.html" class="${on === \'clubs\' ? \'on\' : \'\'}">CLUBS</a>')
rep('    <div class="goal"><b>${fmt(UNLOCK)}</b><span>${PRIZES_LIVE || GUEST ?', '    ${PRIZES_LIVE || GUEST ? `<div class="goal"><b>${fmt(UNLOCK)}</b><span>${PRIZES_LIVE || GUEST ?')
rep("<em>Prizes from Kingston spots drop soon.</em>`}</span></div>", "<em>Prizes from Kingston spots drop soon.</em>`}</span></div>` : ''}")
rep("    ${ok\n      ? (live ?", "    ${!live ? '' : ok\n      ? (live ?")
rep("  if (ok) $('#prize').onclick =", "  if (ok && $('#prize')) $('#prize').onclick =")
rep('''    <div class="gate ok" style="box-shadow:inset 0 0 0 2px var(--gold)"><b style="color:var(--gold)">PRIZE WHEEL DROPS SOON</b><span>Score ${fmt(UNLOCK)} and you'll spin for free stuff from Kingston spots.</span></div>\n''', '''    ${PRIZES_LIVE ? `<div class="gate ok" style="box-shadow:inset 0 0 0 2px var(--gold)"><b style="color:var(--gold)">PRIZE WHEEL DROPS SOON</b><span>Score ${fmt(UNLOCK)} and you'll spin for free stuff from Kingston spots.</span></div>` : ''}\n''')
open('src.html','w').write(s)
print('splice12 ok')

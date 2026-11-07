# Copies the bundle into host/, adds the full page wrapper to index.html and the play counter to every page, then zips it.
import glob, os, shutil, subprocess
SP='/tmp/claude-0/-home-claude/5bf8c0ba-cb85-583b-8189-97cffac50747/scratchpad'
H=SP+'/host'; shutil.rmtree(H, ignore_errors=True); os.makedirs(H)
for f in ['daily.html','party.html','brands.html','thanks.html','link.html','showdown.html','droppin.html','thecall.html','kingston-map.json']:
    shutil.copy(SP+'/bundle/'+f, H)
shutil.copytree(SP+'/bundle/photos', H+'/photos')
shutil.copy(SP+'/site/stats.html', H)
for f in ['club.html', 'clubs.html']: shutil.copy(SP+'/site/'+f, H)   # club games (exec builder + member game) and the page for club execs   # Josh's stats page (not linked anywhere, no counter)
body=open(SP+'/bundle/index.html').read()
head='''<!doctype html>
<html lang="en-CA"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="description" content="Know your school? Prove it. The daily game for Queen's students, plus party games and club games.">
<meta property="og:title" content="Off Campus">
<meta property="og:description" content="Know your school? Prove it. Five new rounds about Queen's every day.">
<meta property="og:url" content="https://offcampusontario.ca/">
'''
e=body.index('</style>')+len('</style>')
open(H+'/index.html','w').write(head+body[:e]+'\n</head><body>\n'+body[e:]+'\n</body></html>\n')

# Party games: a HOME button next to the sound button on every screen (the title screen keeps its own "ALL GAMES" link).
HOME_CSS = '<style>.ocr{display:inline-flex;align-items:center;gap:8px;margin-left:auto;flex:0 0 auto}.ocr .ochome{text-decoration:none}.ocr:has(~ *){margin-left:0}:has(> a[onclick*="__allGames"]) > .ocr .ochome{display:none}</style>'
for g, cls in [('droppin','sound'), ('showdown','sound'), ('thecall','pill')]:
    f = H + '/' + g + '.html'; s = open(f).read()
    n = s.count('${soundBtn()}'); assert n >= 4, (g, n)
    if g == 'showdown':   # the party Showdown boards are ours, not a survey of 100 students
        for a, b in [("We asked 100 Queen's students. Can you guess what they said?", "Our board of top answers. Can you guess them?"), ("WE ASKED 100 QUEEN'S STUDENTS", "THE BOARD"), ("'SURVEY SAYS…'", "'THE BOARD SAYS…'")]:
            assert s.count(a) == 1, a; s = s.replace(a, b)
    s = s.replace('${soundBtn()}', '<span class="ocr"><a class="' + cls + ' ochome" href="index.html">&larr; HOME</a>${soundBtn()}</span>')
    s = s.replace("location.href='./';return false;", "location.href='party.html';return false;", 1)
    s = s.replace('</head>', HOME_CSS + '</head>', 1)
    open(f, 'w').write(s)

# App icon (same as the Instagram profile picture) on every page
for n in ['apple-touch-icon.png','icon-192.png','icon-512.png','favicon-32.png']: shutil.copy(SP+'/icons/'+n, H)
ICON = '<link rel="apple-touch-icon" href="/apple-touch-icon.png"><link rel="icon" type="image/png" sizes="32x32" href="/favicon-32.png"><link rel="icon" type="image/png" sizes="192x192" href="/icon-192.png"><meta name="apple-mobile-web-app-title" content="Off Campus">'
for f in glob.glob(H+'/*.html'):
    t = open(f).read()
    if 'apple-touch-icon' in t: continue
    t = t.replace('</head>', ICON + '</head>', 1) if '</head>' in t else ICON + t
    open(f, 'w').write(t)

# Link preview (iMessage, Instagram DMs, WhatsApp): the same image and words on every page people share
shutil.copy(SP+'/site/og.jpg', H)
OG = {'daily.html':("Off Campus · The Queen's Daily", "How well do you know Queen's? Today's five: 3 minutes, free, same five for everyone at Queen's.", "https://offcampusontario.ca/daily.html"),
      'index.html':("Off Campus", "Know your school? Prove it. Five new rounds about Queen's every day.", "https://offcampusontario.ca/"),
      'club.html':("Your club's game · Off Campus", "How well do you know your club? 5 questions, 2 minutes. See how everyone really answered.", "https://offcampusontario.ca/clubs"),
      'party.html':("Off Campus · Party Games", "Party games made for Queen's. Plug in the laptop and play together.", "https://offcampusontario.ca/party.html")}
for f in glob.glob(H+'/*.html'):
    n = os.path.basename(f); t = open(f).read()
    if n in ('stats.html', 'link.html', 'thanks.html') or 'og:image' in t: continue
    title, desc, url = OG.get(n, ("Off Campus", "Games made for Queen's students.", "https://offcampusontario.ca/" + n))
    tags = ''
    if 'og:title' not in t: tags += f'<meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="{url}">'
    tags += '<meta property="og:type" content="website"><meta property="og:image" content="https://offcampusontario.ca/og.jpg"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">'
    t = t.replace('</head>', tags + '</head>', 1) if '</head>' in t else tags + t
    open(f, 'w').write(t)
# Visit counter (GoatCounter). It only loads on the real site, so deploy previews and local tests never add to the real numbers.
GC='<script data-goatcounter="https://offcampusontario.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
GC_LIVE_ONLY='<script>if(/^(www\\.)?offcampusontario\\.ca$/.test(location.hostname)){var gc=document.createElement("script");gc.async=true;gc.src="https://gc.zgo.at/count.js";gc.setAttribute("data-goatcounter","https://offcampusontario.goatcounter.com/count");document.head.appendChild(gc);}</script>'
for f in glob.glob(H+'/*.html'):
    s=open(f).read()
    if f.endswith('link.html') or f.endswith('stats.html'): continue
    if GC in s: s=s.replace(GC, GC_LIVE_ONLY)                      # pages that carry their own counter tag
    elif 'goatcounter' in s: continue                               # club.html: has its own track() but no counter tag (unchanged)
    else: s=s.replace('</body></html>', GC_LIVE_ONLY+'\n</body></html>',1)
    open(f,'w').write(s)
z=SP+'/offcampus-site.zip'
if os.path.exists(z): os.remove(z)
subprocess.run(['zip','-qr',z,'.'],cwd=H,check=True)
print('zip', os.path.getsize(z))

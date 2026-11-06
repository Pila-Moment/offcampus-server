# Builds parts/days.js: 21 days of Queen's Daily content (2 Receipts, 2 Showdown boards, 1 photo per day).
# Edit the lists below, then rerun: python3 content.py
import json
SP = '/tmp/claude-0/-home-claude/5bf8c0ba-cb85-583b-8189-97cffac50747/scratchpad'

# Receipts: (question, % who said yes). In each pair, the first is milder, the second spicier.
RECEIPTS = [
  ("Have you ever gone to Stauffer just to see someone?", 41), ("Have you ever hooked up with someone from your first-year floor?", 24),
  ("Have you ever skipped a class you were already on campus for?", 68), ("Have you ever texted your ex after a night out?", 35),
  ("Have you ever fallen asleep in a lecture?", 81), ("Have you ever had a crush on your TA?", 29),
  ("Have you ever pretended to be on the phone to avoid someone on University Ave?", 52), ("Have you ever left a party without telling anyone?", 63),
  ("Have you ever gone to a lecture hungover?", 74), ("Have you ever hooked up with someone in your program?", 33),
  ("Have you ever cried in Stauffer?", 37), ("Have you ever ghosted someone after a first date?", 42),
  ("Have you ever said you were 'almost there' when you hadn't left yet?", 83), ("Have you ever had a situationship that lasted longer than a semester?", 38),
  ("Have you ever lied to your parents about your grades?", 46), ("Have you ever DMed someone you saw at the ARC?", 11),
  ("Have you ever had a fight with your roommate over dishes?", 57), ("Have you ever been in a group chat that got screenshotted?", 47),
  ("Have you ever studied for an exam only the night before?", 64), ("Have you ever walked home from Aberdeen at 3am?", 45),
  ("Have you ever walked to class in your pyjamas?", 39), ("Have you ever posted something and deleted it within an hour?", 49),
  ("Have you ever gone a full week without cooking a real meal?", 55), ("Have you ever lost a shoe on a night out?", 13),
  ("Have you ever gone to class just for the attendance marks?", 58), ("Have you ever been turned away at the door of a bar on Princess?", 21),
  ("Have you ever ordered food at 2am after a night out?", 77), ("Have you ever been kicked out of a house party?", 14),
  ("Have you ever pulled an all-nighter in Stauffer?", 34), ("Have you ever gone on a date with someone from your faculty?", 43),
  ("Have you ever gone to a party where you only knew one person?", 71), ("Have you ever had a noise complaint at your house?", 26),
  ("Have you ever eaten Osmow's more than twice in one week?", 31), ("Have you ever lost your student card on a night out?", 33),
  ("Have you ever stayed in Kingston over reading week?", 36), ("Have you ever had a professor learn your name for the wrong reason?", 16),
  ("Have you ever paid your rent late?", 22), ("Have you ever slept through a midterm?", 12),
  ("Have you ever changed your program?", 27), ("Have you ever stolen a street sign?", 9),
  ("Have you ever sat in on a lecture you weren't enrolled in?", 18), ("Have you ever skipped a midterm and just taken the zero?", 8),
]

NEW_BOARDS = [
 { 'id':'procrastinate', 'q':"Name something you do instead of studying.", 'a':[
   { 't':'Scroll on my phone', 'p':33, 'k':['phone','scroll','tiktok','instagram','insta','reels','social media','snap','snapchat','doomscroll'] },
   { 't':'Take a nap', 'p':20, 'k':['nap','sleep','sleeping','bed'] },
   { 't':'Watch Netflix', 'p':16, 'k':['netflix','tv','show','shows','youtube','movie','stream','binge'] },
   { 't':'Clean my room', 'p':12, 'k':['clean','cleaning','tidy','organize','laundry','room'] },
   { 't':'Get a snack', 'p':11, 'k':['snack','eat','food','fridge','cook','coffee'] },
   { 't':'Go to the gym', 'p':8, 'k':['gym','arc','workout','work out','run','lift','exercise'] } ]},
 { 'id':'kingstonbest', 'q':"Name the best thing about Kingston.", 'a':[
   { 't':'The lake', 'p':29, 'k':['lake','water','lake ontario','waterfront','breakwater','pier','beach'] },
   { 't':'Downtown', 'p':22, 'k':['downtown','princess','princess street','shops','restaurants','food'] },
   { 't':'Everything is walkable', 'p':16, 'k':['walk','walkable','close','small','everything close','walking'] },
   { 't':'The people', 'p':14, 'k':['people','friends','students','community','queens'] },
   { 't':'The bars', 'p':11, 'k':['bars','bar','nightlife','going out','clubs','stages','ale house'] },
   { 't':'The old buildings', 'p':8, 'k':['buildings','limestone','history','old','architecture','historic','fort henry'] } ]},
 { 'id':'owns', 'q':"Name something every Queen's student owns.", 'a':[
   { 't':'A Canada Goose', 'p':27, 'k':['canada goose','goose','parka','winter jacket','jacket','coat'] },
   { 't':'A Queen\'s hoodie', 'p':24, 'k':['hoodie','queens hoodie','sweater','crewneck','merch','sweatshirt'] },
   { 't':'AirPods', 'p':17, 'k':['airpods','headphones','earbuds','pods'] },
   { 't':'A Stanley cup', 'p':13, 'k':['stanley','water bottle','bottle','cup','hydro flask','yeti'] },
   { 't':'A MacBook', 'p':11, 'k':['macbook','laptop','mac','computer','apple'] },
   { 't':'Lululemon', 'p':8, 'k':['lululemon','lulu','leggings','belt bag','aritzia'] } ]},
 { 'id':'gohome', 'q':"Name a reason you go home for the weekend.", 'a':[
   { 't':'Free food', 'p':31, 'k':['food','home food','cooking','moms cooking','meals','free food','groceries'] },
   { 't':'Laundry', 'p':22, 'k':['laundry','wash','clothes','washing'] },
   { 't':'A family thing', 'p':17, 'k':['family','birthday','event','parents','mom','dad','holiday','thanksgiving'] },
   { 't':'See my home friends', 'p':12, 'k':['friends','high school','home friends','boyfriend','girlfriend','partner'] },
   { 't':'Actually sleep', 'p':10, 'k':['sleep','rest','quiet','bed','relax'] },
   { 't':'An appointment', 'p':8, 'k':['appointment','doctor','dentist','haircut','job','work','shift'] } ]},
 { 'id':'groupproject', 'q':"Name something that happens in every group project.", 'a':[
   { 't':'One person does everything', 'p':34, 'k':['one person','does everything','carry','carries','all the work','me'] },
   { 't':'Someone ghosts', 'p':23, 'k':['ghost','ghosts','disappears','never responds','no show','ghosting','mia'] },
   { 't':'It\'s done last minute', 'p':16, 'k':['last minute','night before','procrastinate','late','deadline','cram'] },
   { 't':'The group chat dies', 'p':11, 'k':['group chat','gc','chat','dead','no one answers'] },
   { 't':'Someone argues', 'p':9, 'k':['argue','argument','fight','drama','disagree'] },
   { 't':'A Google Doc mess', 'p':7, 'k':['google doc','doc','docs','slides','formatting','powerpoint'] } ]},
 { 'id':'firstyear', 'q':"Name a way you can tell someone's a first-year.", 'a':[
   { 't':'Wearing a lanyard', 'p':29, 'k':['lanyard','keys','student card','card on neck'] },
   { 't':'Lost on campus', 'p':22, 'k':['lost','directions','map','asking','cant find','confused'] },
   { 't':'Frosh week shirt', 'p':17, 'k':['frosh','frosh shirt','orientation','shirt','tam','coveralls'] },
   { 't':'Travelling in a huge group', 'p':14, 'k':['group','huge group','pack','herd','floor','squad'] },
   { 't':'Goes to every lecture', 'p':10, 'k':['every lecture','lecture','attends','front row','notes','early'] },
   { 't':'Talks about residence', 'p':8, 'k':['residence','res','dorm','floor','don','leonard','vic','chown'] } ]},
 { 'id':'complain', 'q':"Name something students complain about in Kingston.", 'a':[
   { 't':'Rent and landlords', 'p':31, 'k':['rent','landlord','landlords','housing','expensive','price','prices'] },
   { 't':'The cold and the wind', 'p':23, 'k':['cold','wind','windy','winter','snow','weather','freezing'] },
   { 't':'The buses', 'p':15, 'k':['bus','buses','transit','transportation','uber','ubers'] },
   { 't':'Mould', 'p':12, 'k':['mould','mold','damp','gross house'] },
   { 't':'The bar lines', 'p':10, 'k':['line','lines','bar line','bars','waiting','cover'] },
   { 't':'Nothing to do', 'p':9, 'k':['nothing to do','boring','small','bored','dead'] } ]},
 { 'id':'arcsee', 'q':"Name something you'll see at the ARC.", 'a':[
   { 't':'People on their phones', 'p':28, 'k':['phone','phones','scrolling','texting','tiktok','sitting on machine'] },
   { 't':'Mirror selfies', 'p':21, 'k':['selfie','selfies','mirror','pictures','photos','filming'] },
   { 't':'A huge line for Tims', 'p':17, 'k':['tims','tim hortons','line','coffee','food'] },
   { 't':'Lululemon everywhere', 'p':14, 'k':['lululemon','lulu','leggings','gymshark','gym clothes','outfits'] },
   { 't':'Someone hogging a machine', 'p':12, 'k':['hogging','machine','bench','squat rack','rack','waiting'] },
   { 't':'People studying', 'p':8, 'k':['studying','study','homework','laptop','reading'] } ]},
 { 'id':'eattoo', 'q':"Name a food you eat way too much of at school.", 'a':[
   { 't':'Pasta', 'p':29, 'k':['pasta','kd','kraft dinner','mac and cheese','spaghetti','noodles'] },
   { 't':'Ramen', 'p':21, 'k':['ramen','instant noodles','mr noodles','cup noodles'] },
   { 't':'Osmow\'s', 'p':16, 'k':['osmows','osmow','shawarma','on the rocks','pita'] },
   { 't':'Pizza', 'p':14, 'k':['pizza','slice','dominos','pizza pizza'] },
   { 't':'Cereal', 'p':11, 'k':['cereal','oatmeal','granola'] },
   { 't':'Eggs', 'p':9, 'k':['eggs','egg','omelette','scrambled'] } ]},
 { 'id':'late9am', 'q':"Name a reason you're late to a 9am.", 'a':[
   { 't':'Slept through my alarm', 'p':37, 'k':['alarm','overslept','slept','sleep','snooze','woke up late'] },
   { 't':'The coffee line', 'p':19, 'k':['coffee','line','tims','starbucks','cogro'] },
   { 't':'It was too cold', 'p':14, 'k':['cold','snow','weather','winter','wind'] },
   { 't':'Couldn\'t find the room', 'p':12, 'k':['room','lost','find','building','wrong room','wrong building'] },
   { 't':'Hungover', 'p':10, 'k':['hungover','hangover','last night','out last night','drinking'] },
   { 't':'Was getting ready', 'p':8, 'k':['ready','shower','outfit','hair','makeup','getting dressed'] } ]},
]

EXISTING_DAILY = [
 { 'id':'udhouse', 'q':"Name something you'll find in every University District house.", 'a':[
   { 't':'A beer pong table', 'p':28, 'k':['pong','beer pong','pong table','table','beirut'] },
   { 't':'Mould', 'p':21, 'k':['mould','mold','black mold','black mould','damp','mildew'] },
   { 't':'A couch on the porch', 'p':16, 'k':['couch','porch couch','sofa','porch','futon'] },
   { 't':'A stolen street sign', 'p':13, 'k':['sign','street sign','stop sign','stolen sign','road sign','pylon','cone'] },
   { 't':'String lights', 'p':12, 'k':['lights','string lights','fairy lights','christmas lights','led lights','led strip','fairy'] },
   { 't':'A dead plant', 'p':10, 'k':['plant','dead plant','plants','cactus'] } ]},
 { 'id':'hungover', 'q':"Name the first thing you do when you wake up hungover.", 'a':[
   { 't':'Check my phone', 'p':30, 'k':['phone','check phone','texts','snap','snapchat','instagram','insta','messages','who i texted'] },
   { 't':'Drink water', 'p':22, 'k':['water','drink water','gatorade','hydrate','liquid iv','electrolytes','pedialyte'] },
   { 't':'Order food', 'p':18, 'k':['food','order food','uber eats','skip','doordash','osmows','pizza','mcdonalds','eat','breakfast','greasy food'] },
   { 't':'Check my bank account', 'p':12, 'k':['bank','bank account','money','account','card','spent','venmo','etransfer'] },
   { 't':'Go back to sleep', 'p':10, 'k':['sleep','go back to sleep','back to bed','nap','bed','roll over'] },
   { 't':'Ask the group chat', 'p':8, 'k':['group chat','gc','ask friends','what happened','friends','chat'] } ]},
]

sd = json.load(open(SP + '/daily/parts/showdown_boards.json'))
tame = [b for b in sd if not b.get('spicy')] + NEW_BOARDS
spicy = [b for b in sd if b.get('spicy')]
# Day 1 keeps the two boards from the demo. After that: one milder board, then one spicier board each day.
first = EXISTING_DAILY
photos = {p['id']: p for p in json.load(open(SP + '/droppin/photos.json'))}
PHOTO_ORDER = ['cavalry1916', 'chalmers2009', 'princess1899', 'richardson2019', 'grant1905', 'pitapit2019', 'market1902', 'goodes2015', 'eclipse2024', 'fdr1938',
               'jduc2025', 'pen2013', 'queen1959', 'mcd2023', 'fort1920', 'mcburney2024', 'buskers2014', 'cityhall2017', 'ferry2008', 'drydock1891', 'leons2021']
N = 21
assert len(RECEIPTS) >= 2 * N, len(RECEIPTS)
days = []
ti = si = 0
for d in range(N):
    if d == 0:
        b1, b2 = first
    else:
        b1 = tame[ti]; ti += 1
        if si < len(spicy): b2 = spicy[si]; si += 1
        else: b2 = tame[ti]; ti += 1
    r1, r2 = RECEIPTS[2 * d], RECEIPTS[2 * d + 1]
    p = photos[PHOTO_ORDER[d]]
    clean = lambda b: { 'type':'survey', 'q':b['q'], 'a':[{ 't':x['t'], 'p':x['p'], 'k':x['k'] } for x in b['a']] }
    days.append({ 'rounds':[
        { 'type':'receipts', 'q':r1[0], 'pct':r1[1] }, clean(b1),
        { 'type':'receipts', 'q':r2[0], 'pct':r2[1] }, clean(b2),
        { 'type':'pin', 'photo':{ k: p[k] for k in ['img','year','lat','lng','title','blurb','credit','license','source'] } } ] })
used = [d['rounds'][1]['q'] for d in days] + [d['rounds'][3]['q'] for d in days]
assert len(set(used)) == len(used), 'repeat board'
open(SP + '/daily/parts/days.js', 'w').write('const DAYS = ' + json.dumps(days, ensure_ascii=False) + ';\n')
print('days', len(days), 'boards', len(used), 'tame', len(tame), 'spicy', len(spicy))

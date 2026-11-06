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

# Questions made to be sent to someone: (question, % yes, who to send it to). The reveal says "SEND THIS TO ...".
SEND_QS = [
  ("Do you think engineers are annoying?", 80, "your engineer friend"),
  ("Would you date someone who goes to Western?", 18, "your friend at Western"),
  ("Do you think Commerce kids act like they already work on Bay Street?", 74, "your Commerce friend"),
  ("Do you think your roommate is the messy one?", 64, "your roommate"),
  ("Do you think Artsci is the easiest degree at Queen's?", 61, "your Artsci friend"),
  ("Do you think Kin students basically live at the ARC?", 77, "your Kin friend"),
]
# Who to send the regular questions to (matched by the start of the question). Anything not listed says "a friend".
SEND_HINTS = {
  "hooked up with someone from your first-year floor": "your first-year floor chat",
  "DMed someone you saw at the ARC": "your gym buddy",
  "cried in Stauffer": "your study buddy",
  "situationship that lasted longer": "your situationship",
  "hooked up with someone in your program": "your program group chat",
  "walked home from Aberdeen": "whoever walked you home",
  "had a crush on your TA": "your TA crush",
  "texted your ex after a night out": "the friend who always does this",
  "been in a group chat that got screenshotted": "the group chat",
  "gone on a date with someone from your faculty": "your faculty",
  "stolen a street sign": "your house group chat",
  "had a fight with your roommate over dishes": "your roommate",
  "gone to Stauffer just to see someone": "your Stauffer crush",
}

# Weeks 4-5 (Nov 24 - Dec 7). Third item = who the reveal says to send it to.
RECEIPTS += [
  ("Have you ever pretended to know the words to the Oil Thigh?", 44, "your frosh group"), ("Have you ever hooked up with someone in your house?", 17, "your housemates"),
  ("Have you ever waited longer in the Stages line than you spent inside?", 39, "your going-out group"), ("Have you ever lied about your program to someone at a bar?", 19, "your wingman"),
  ("Do you think West Campus is basically a different city?", 71, "your friend on West Campus"), ("Have you ever been sexiled from your own room?", 23, "your roommate"),
  ("Do you think Queen's is better than Western at everything?", 84, "your friend at Western"), ("Have you ever had a crush on someone in your frosh group?", 46, "your frosh group"),
  ("Have you ever skipped class because it was too cold to walk?", 48, None), ("Have you ever made out with someone at Hoco?", 41, "your Hoco crew"),
  ("Do you think your house is the messiest on your street?", 29, "your housemates"), ("Have you ever gone to a lecture just because your crush is in it?", 34, "your lecture crush"),
  ("Have you ever lied to your don?", 62, "your old don"), ("Have you ever hooked up with a friend's ex?", 22, "the friend who did this"),
  ("Have you ever walked into the wrong lecture and just stayed?", 27, None), ("Have you ever used ChatGPT on something you weren't supposed to?", 63, "your study group"),
  ("Do you think Nursing students have the hardest degree?", 52, "your Nursing friend"), ("Have you ever paid cover and left within 10 minutes?", 35, "your going-out group"),
  ("Have you ever been to Wolfe Island?", 36, None), ("Have you ever kept dating your high school partner into first year?", 38, None),
  ("Do you think engineers throw the best parties?", 47, "your engineer friend"), ("Have you ever been on a date at the Pier?", 26, None),
  ("Have you ever said you were going home for the weekend and didn't?", 41, None), ("Have you ever fallen asleep before eating your late-night pizza?", 31, None),
  ("Do you think Commerce kids actually go to class?", 38, "your Commerce friend"), ("Have you ever gone to the ARC just to see who's there?", 33, "your gym buddy"),
  ("Have you ever been to Fort Henry for something that wasn't a school trip?", 28, None), ("Have you ever cried at Breakwater?", 21, "your best friend"),
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

EXTRA_BOARDS = [
  { 'id':'pregame', 'q':'Name something that always happens at a pregame.', 'spicy':True, 'a':[{ 't':'Beer pong', 'p':27, 'k':['pong', 'beer pong', 'beirut', 'flip cup', 'games', 'drinking games'] }, { 't':'Someone takes the aux', 'p':22, 'k':['aux', 'music', 'playlist', 'speaker', 'dj', 'song'] }, { 't':'Too many people show up', 'p':16, 'k':['people', 'crowded', 'too many', 'packed', 'uninvited'] }, { 't':'Someone spills', 'p':13, 'k':['spill', 'spills', 'spilled', 'mess'] }, { 't':'Waiting for an Uber', 'p':12, 'k':['uber', 'ride', 'cab', 'taxi', 'waiting'] }, { 't':'Someone gets too drunk', 'p':10, 'k':['drunk', 'wasted', 'throws up', 'puke', 'blackout', 'sick'] }] },
  { 'id':'textback', 'q':"Name a reason they haven't texted you back.", 'spicy':True, 'a':[{ 't':"They're busy", 'p':26, 'k':['busy', 'class', 'work', 'studying'] }, { 't':'Talking to someone else', 'p':22, 'k':['someone else', 'another person', 'talking to someone', 'other girl', 'other guy'] }, { 't':'Playing hard to get', 'p':16, 'k':['hard to get', 'games', 'playing games', 'power move'] }, { 't':"They're asleep", 'p':14, 'k':['asleep', 'sleep', 'sleeping', 'nap'] }, { 't':'Lost interest', 'p':12, 'k':['lost interest', 'not interested', 'bored', 'ghosting', 'ghosted'] }, { 't':'Phone died', 'p':10, 'k':['phone died', 'dead', 'battery', 'charge'] }] },
  { 'id':'ghostreason', 'q':"Name a reason you'd ghost someone after a first date.", 'spicy':True, 'a':[{ 't':'Bad kisser', 'p':24, 'k':['kiss', 'kisser', 'kissing'] }, { 't':'Talked about their ex', 'p':21, 'k':['ex', 'their ex'] }, { 't':'Rude to the server', 'p':16, 'k':['rude', 'server', 'waiter', 'waitress'] }, { 't':'Boring', 'p':15, 'k':['boring', 'dry', 'awkward', 'no conversation'] }, { 't':'Bad breath', 'p':13, 'k':['breath', 'smell', 'hygiene'] }, { 't':'They go to Western', 'p':11, 'k':['western'] }] },
  { 'id':'drunktext', 'q':"Name someone you shouldn't text when you're drunk.", 'spicy':True, 'a':[{ 't':'Your ex', 'p':41, 'k':['ex', 'ex boyfriend', 'ex girlfriend'] }, { 't':'Your crush', 'p':19, 'k':['crush'] }, { 't':'Your parents', 'p':14, 'k':['parents', 'mom', 'dad'] }, { 't':'Your prof or TA', 'p':11, 'k':['prof', 'professor', 'ta'] }, { 't':'Your boss', 'p':8, 'k':['boss', 'manager', 'work'] }, { 't':'The group chat', 'p':7, 'k':['group chat', 'gc'] }] },
  { 'id':'shutdown', 'q':"Name a sign the party's about to get shut down.", 'spicy':True, 'a':[{ 't':'Cops show up', 'p':31, 'k':['cops', 'police', 'bylaw', 'officer'] }, { 't':'Music gets turned off', 'p':19, 'k':['music', 'off', 'quiet'] }, { 't':'Lights come on', 'p':16, 'k':['lights', 'light'] }, { 't':'The host starts yelling', 'p':14, 'k':['host', 'yelling', 'screaming', 'mad'] }, { 't':'Neighbours come over', 'p':11, 'k':['neighbour', 'neighbours', 'neighbor', 'complaint'] }, { 't':'Something gets broken', 'p':9, 'k':['break', 'broke', 'broken', 'smash'] }] },
  { 'id':'hangover', 'q':'Name a hangover cure.', 'spicy':True, 'a':[{ 't':'Water', 'p':28, 'k':['water', 'gatorade', 'liquid iv', 'electrolytes', 'pedialyte'] }, { 't':'Greasy food', 'p':24, 'k':['greasy', 'food', 'mcdonalds', 'burger', 'breakfast', 'pizza', 'poutine'] }, { 't':'Sleep', 'p':17, 'k':['sleep', 'nap', 'bed'] }, { 't':'Advil', 'p':14, 'k':['advil', 'tylenol', 'pills', 'ibuprofen'] }, { 't':'Coffee', 'p':10, 'k':['coffee', 'tims', 'caffeine'] }, { 't':'Hair of the dog', 'p':7, 'k':['hair of the dog', 'another drink', 'drink', 'beer', 'mimosa'] }] },
  { 'id':'phone', 'q':"Name something you'd find on a Queen's student's phone.", 'spicy':True, 'a':[{ 't':'Hinge', 'p':22, 'k':['hinge', 'tinder', 'bumble', 'dating app', 'dating'] }, { 't':'Screenshots of lecture slides', 'p':18, 'k':['notes', 'screenshots', 'slides', 'lecture'] }, { 't':'Blurry party pics', 'p':17, 'k':['pics', 'photos', 'party', 'videos', 'blurry'] }, { 't':'Uber Eats', 'p':15, 'k':['uber eats', 'skip', 'doordash', 'food'] }, { 't':'A million group chats', 'p':15, 'k':['group chat', 'chats', 'messages', 'imessage'] }, { 't':'OnQ', 'p':13, 'k':['onq', 'on q', 'd2l', 'courses'] }] },
  { 'id':'sunday', 'q':'Name something you do on a Sunday after a big weekend.', 'spicy':True, 'a':[{ 't':'Rot in bed', 'p':30, 'k':['bed', 'rot', 'lay in bed', 'sleep', 'nap'] }, { 't':'Order food', 'p':21, 'k':['food', 'order', 'uber eats', 'skip', 'brunch'] }, { 't':"Read last night's texts", 'p':15, 'k':['texts', 'regret', 'check texts', 'messages'] }, { 't':'Pretend to study', 'p':14, 'k':['study', 'stauffer', 'homework', 'assignment'] }, { 't':'Laundry', 'p':11, 'k':['laundry', 'clean', 'cleaning', 'chores'] }, { 't':'Call home', 'p':9, 'k':['call', 'mom', 'parents', 'home', 'family'] }] },
  { 'id':'excuse', 'q':'Name an excuse for not going out tonight.', 'spicy':False, 'a':[{ 't':'I have to study', 'p':30, 'k':['study', 'studying', 'midterm', 'exam', 'assignment', 'essay', 'school'] }, { 't':"I'm tired", 'p':22, 'k':['tired', 'sleep', 'exhausted', 'nap'] }, { 't':"I'm broke", 'p':17, 'k':['money', 'broke', 'cash', 'poor', 'budget'] }, { 't':"I'm sick", 'p':13, 'k':['sick', 'cold', 'flu', 'ill'] }, { 't':'Still hungover', 'p':10, 'k':['hungover', 'hangover', 'last night'] }, { 't':'Nothing to wear', 'p':8, 'k':['clothes', 'outfit', 'wear', 'nothing to wear'] }] },
  { 'id':'stauffpacked', 'q':'Name a reason Stauffer is packed.', 'spicy':False, 'a':[{ 't':'Midterms', 'p':34, 'k':['midterm', 'midterms', 'exam', 'exams', 'finals'] }, { 't':"It's warm inside", 'p':18, 'k':['warm', 'heat', 'cold outside', 'cold'] }, { 't':"Everyone's there to be seen", 'p':16, 'k':['social', 'socializing', 'friends', 'talk', 'seen'] }, { 't':'Group projects', 'p':13, 'k':['group', 'project', 'group project'] }, { 't':'Charging their phone', 'p':10, 'k':['charge', 'charging', 'outlet', 'plug', 'phone'] }, { 't':'The coffee', 'p':9, 'k':['coffee', 'cafe', 'tims', 'starbucks'] }] },
  { 'id':'miss1st', 'q':'Name something you miss about first year.', 'spicy':False, 'a':[{ 't':'The caf', 'p':28, 'k':['caf', 'food', 'meal plan', 'dining hall', 'ban righ', 'leonard'] }, { 't':'Your floor', 'p':24, 'k':['floor', 'floormates', 'res friends', 'res', 'residence'] }, { 't':'No rent', 'p':18, 'k':['rent', 'no rent', 'cheap', 'money'] }, { 't':'Frosh week', 'p':13, 'k':['frosh', 'orientation'] }, { 't':'Easy courses', 'p':10, 'k':['easy', 'courses', 'classes', 'grades'] }, { 't':'Living on campus', 'p':7, 'k':['close', 'campus', 'walk', 'location'] }] },
  { 'id':'landlord', 'q':'Name something your landlord never fixes.', 'spicy':False, 'a':[{ 't':'The heat', 'p':29, 'k':['heat', 'heating', 'furnace', 'cold'] }, { 't':'Mould', 'p':21, 'k':['mould', 'mold'] }, { 't':'Leaks', 'p':16, 'k':['leak', 'leaks', 'roof', 'ceiling', 'water'] }, { 't':'The windows', 'p':13, 'k':['window', 'windows', 'draft'] }, { 't':'Mice', 'p':12, 'k':['mice', 'mouse', 'rats', 'pests', 'bugs'] }, { 't':'Appliances', 'p':9, 'k':['fridge', 'stove', 'oven', 'washer', 'dryer', 'dishwasher', 'appliances'] }] },
  { 'id':'hocowear', 'q':"Name something every Queen's student wears on Hoco.", 'spicy':False, 'a':[{ 't':'Tricolour', 'p':32, 'k':['tricolour', 'tricolor', 'red gold blue', 'colours', 'colors'] }, { 't':'A jersey', 'p':18, 'k':['jersey', 'football jersey'] }, { 't':'A tam', 'p':16, 'k':['tam', 'tams', 'hat'] }, { 't':'Overalls', 'p':13, 'k':['overalls', 'coveralls'] }, { 't':'Face paint', 'p':12, 'k':['face paint', 'paint', 'glitter'] }, { 't':"A Queen's hoodie", 'p':9, 'k':['hoodie', 'sweater', 'crewneck'] }] },
  { 'id':'datespot', 'q':'Name a first-date spot in Kingston.', 'spicy':False, 'a':[{ 't':'A coffee shop', 'p':29, 'k':['coffee', 'cafe', 'coffee shop', 'starbucks'] }, { 't':'Dinner on Princess', 'p':21, 'k':['dinner', 'restaurant', 'princess', 'food', 'sushi'] }, { 't':'A walk by the lake', 'p':17, 'k':['walk', 'lake', 'breakwater', 'pier', 'waterfront'] }, { 't':'Drinks at a bar', 'p':14, 'k':['drinks', 'bar', 'bars', 'pub', 'ale house'] }, { 't':'The movies', 'p':11, 'k':['movie', 'movies', 'theatre', 'cinema'] }, { 't':'Ice cream', 'p':8, 'k':['ice cream', 'mio', 'gelato', 'dessert'] }] },
  { 'id':'examnight', 'q':'Name something you do the night before an exam.', 'spicy':False, 'a':[{ 't':'Cram', 'p':33, 'k':['cram', 'study', 'studying', 'review', 'notes'] }, { 't':'Panic', 'p':20, 'k':['panic', 'cry', 'stress', 'freak out', 'anxiety'] }, { 't':'Pull an all-nighter', 'p':16, 'k':['all nighter', 'allnighter', 'stay up', 'no sleep'] }, { 't':'Chug energy drinks', 'p':12, 'k':['energy drink', 'red bull', 'celsius', 'coffee', 'caffeine'] }, { 't':'Watch lectures at 2x', 'p':11, 'k':['lectures', '2x', 'recordings', 'videos', 'youtube'] }, { 't':'Order food', 'p':8, 'k':['food', 'order', 'uber eats', 'skip', 'doordash', 'snacks'] }] },
  { 'id':'roomfight', 'q':'Name something roommates fight about.', 'spicy':False, 'a':[{ 't':'Dishes', 'p':34, 'k':['dishes', 'sink', 'kitchen'] }, { 't':'Noise', 'p':18, 'k':['noise', 'loud', 'music', 'quiet'] }, { 't':'Bills', 'p':15, 'k':['bills', 'rent', 'money', 'utilities', 'hydro', 'internet', 'wifi'] }, { 't':'Guests staying over', 'p':13, 'k':['guests', 'partner', 'boyfriend', 'girlfriend', 'staying over', 'people over'] }, { 't':'Stolen food', 'p':11, 'k':['food', 'stealing', 'eating my food'] }, { 't':'Cleaning the bathroom', 'p':9, 'k':['bathroom', 'toilet', 'shower', 'cleaning'] }] },
  { 'id':'profsay', 'q':'Name something every prof says on the first day.', 'spicy':False, 'a':[{ 't':'Check the syllabus', 'p':27, 'k':['syllabus', 'onq', 'on q', 'course outline'] }, { 't':'Call me by my first name', 'p':18, 'k':['first name', 'call me'] }, { 't':"Don't use ChatGPT", 'p':17, 'k':['chatgpt', 'ai', 'gpt', 'cheating', 'academic integrity'] }, { 't':'Come to office hours', 'p':15, 'k':['office hours', 'email', 'emails'] }, { 't':'Attendance matters', 'p':12, 'k':['attendance', 'come to class', 'show up'] }, { 't':'This course is hard', 'p':11, 'k':['hard', 'difficult', 'fail', 'drop'] }] },
  { 'id':'missking', 'q':"Name something you'll miss about Kingston after you graduate.", 'spicy':False, 'a':[{ 't':'Your friends', 'p':28, 'k':['friends', 'people', 'housemates'] }, { 't':'Aberdeen', 'p':19, 'k':['aberdeen', 'hoco', 'parties', 'partying'] }, { 't':'The lake', 'p':16, 'k':['lake', 'water', 'breakwater', 'pier'] }, { 't':'Walking everywhere', 'p':14, 'k':['walk', 'walking', 'close'] }, { 't':'The bars', 'p':12, 'k':['bars', 'stages', 'ale house', 'going out', 'nightlife'] }, { 't':'Student life', 'p':11, 'k':['student', 'school', 'campus', 'queens'] }] },
  { 'id':'goose', 'q':'Name something a campus goose does to you.', 'spicy':False, 'a':[{ 't':'Hisses at you', 'p':33, 'k':['hiss', 'hisses', 'hissing'] }, { 't':'Chases you', 'p':26, 'k':['chase', 'chases', 'chased', 'runs at'] }, { 't':'Blocks the path', 'p':15, 'k':['block', 'blocks', 'path', 'in the way', 'stands'] }, { 't':'Poops everywhere', 'p':13, 'k':['poop', 'poops', 'poo', 'mess', 'droppings'] }, { 't':'Bites you', 'p':8, 'k':['bite', 'bites', 'bit', 'attack', 'attacks'] }, { 't':'Stares you down', 'p':5, 'k':['stare', 'stares', 'look', 'watches'] }] },
  { 'id':'bucket', 'q':"Name something on every Queen's student's bucket list.", 'spicy':False, 'a':[{ 't':'Swim at the Pier', 'p':24, 'k':['swim', 'pier', 'jump', 'lake', 'gord downie'] }, { 't':'Go to Wolfe Island', 'p':18, 'k':['wolfe island', 'ferry', 'island'] }, { 't':'Hoco on Aberdeen', 'p':17, 'k':['hoco', 'aberdeen', 'homecoming', 'foco'] }, { 't':'Pull an all-nighter in Stauffer', 'p':14, 'k':['stauffer', 'all nighter', 'library'] }, { 't':'Fort Henry', 'p':14, 'k':['fort henry', 'sunset ceremony', 'fort'] }, { 't':'A Gaels game', 'p':13, 'k':['gaels', 'football', 'game', 'richardson'] }] },
  { 'id':'houserules', 'q':'Name a rule in every student house.', 'spicy':False, 'a':[{ 't':'No shoes inside', 'p':24, 'k':['shoes'] }, { 't':'Wash your dishes', 'p':22, 'k':['dishes', 'clean up'] }, { 't':'Label your food', 'p':17, 'k':['label', 'food', 'fridge'] }, { 't':'Quiet hours', 'p':14, 'k':['quiet', 'noise', 'quiet hours'] }, { 't':'Text before bringing someone home', 'p':12, 'k':['text', 'bring someone', 'guests', 'overnight'] }, { 't':'Take out the garbage', 'p':11, 'k':['garbage', 'trash', 'recycling', 'compost'] }] },
  { 'id':'winter', 'q':'Name the worst part of walking to class in a Kingston winter.', 'spicy':False, 'a':[{ 't':'The wind off the lake', 'p':31, 'k':['wind', 'windy', 'lake'] }, { 't':'Ice', 'p':24, 'k':['ice', 'icy', 'slip', 'slipping'] }, { 't':'Slush', 'p':15, 'k':['slush', 'puddles', 'wet'] }, { 't':'The cold', 'p':13, 'k':['cold', 'freezing'] }, { 't':'Unshovelled sidewalks', 'p':10, 'k':['sidewalk', 'shovel', 'snow', 'snowbank'] }, { 't':"It's dark", 'p':7, 'k':['dark', 'night'] }] },
  { 'id':'examroom', 'q':'Name something you hear in an exam room.', 'spicy':False, 'a':[{ 't':'Sniffling', 'p':24, 'k':['sniff', 'sniffling', 'cough', 'coughing'] }, { 't':'Pen clicking', 'p':20, 'k':['tap', 'tapping', 'pencil', 'pen', 'clicking'] }, { 't':'Chip bags', 'p':16, 'k':['chips', 'snack', 'wrapper', 'crinkle'] }, { 't':'Heavy sighing', 'p':15, 'k':['sigh', 'sighing', 'breathing'] }, { 't':'Someone leaving early', 'p':14, 'k':['leave', 'leaving', 'early', 'done'] }, { 't':'The clock', 'p':11, 'k':['clock', 'ticking', 'time'] }] },
  { 'id':'toronto', 'q':"Name a way you can tell someone's from Toronto.", 'spicy':False, 'a':[{ 't':'Says "the 6ix"', 'p':26, 'k':['6ix', 'six', 'the 6'] }, { 't':'A Canada Goose', 'p':22, 'k':['goose', 'canada goose'] }, { 't':'Talks about the TTC', 'p':16, 'k':['ttc', 'subway', 'streetcar'] }, { 't':'Thinks Kingston is tiny', 'p':14, 'k':['tiny', 'small', 'small town'] }, { 't':'Leafs or Raptors gear', 'p':12, 'k':['raptors', 'leafs', 'jays'] }, { 't':'Goes home every weekend', 'p':10, 'k':['home', 'goes home', 'weekend'] }] },
  { 'id':'housechat', 'q':'Name what every house group chat is used for.', 'spicy':False, 'a':[{ 't':'Splitting bills', 'p':29, 'k':['bills', 'money', 'rent', 'etransfer', 'splitting'] }, { 't':'"Who\'s home?"', 'p':19, 'k':['whos home', 'home', 'who is home'] }, { 't':'Complaining about dishes', 'p':16, 'k':['dishes', 'cleaning', 'complain'] }, { 't':'Pregame plans', 'p':15, 'k':['pregame', 'going out', 'plans', 'tonight'] }, { 't':'Memes', 'p':12, 'k':['memes', 'tiktoks', 'reels', 'funny'] }, { 't':'Borrowing stuff', 'p':9, 'k':['borrow', 'charger', 'clothes', 'stuff'] }] },
  { 'id':'lecture5', 'q':'Name something you do in the first 5 minutes of a lecture.', 'spicy':False, 'a':[{ 't':'Check your phone', 'p':31, 'k':['phone', 'instagram', 'tiktok', 'scroll'] }, { 't':'Find a seat', 'p':18, 'k':['seat', 'sit'] }, { 't':'Open your laptop', 'p':16, 'k':['laptop', 'notes'] }, { 't':'Look for your friends', 'p':13, 'k':['friends', 'look for', 'wave'] }, { 't':'Pull out a coffee', 'p':12, 'k':['coffee', 'drink', 'snack'] }, { 't':"Ask what today's lecture is", 'p':10, 'k':['ask', 'topic', 'whats today'] }] },
  { 'id':'frosh', 'q':'Name something that happens during frosh week.', 'spicy':False, 'a':[{ 't':'Getting your tam', 'p':23, 'k':['tam', 'tams', 'hat'] }, { 't':'Losing your voice', 'p':21, 'k':['voice', 'cheer', 'cheering', 'chant', 'yelling'] }, { 't':'Meeting your best friends', 'p':18, 'k':['friends', 'meet', 'best friends', 'people'] }, { 't':'Learning the Oil Thigh', 'p':15, 'k':['oil thigh', 'song', 'chant'] }, { 't':'No sleep', 'p':13, 'k':['sleep', 'tired', 'no sleep'] }, { 't':'A sunburn', 'p':10, 'k':['sun', 'sunburn', 'burn', 'hot'] }] },
  { 'id':'coffee', 'q':"Name where Queen's students get coffee.", 'spicy':False, 'a':[{ 't':"Tim's", 'p':30, 'k':['tims', 'tim hortons', 'timmies'] }, { 't':'Starbucks', 'p':22, 'k':['starbucks', 'sbux'] }, { 't':'CoGro', 'p':16, 'k':['cogro', 'common ground'] }, { 't':'The Sleepless Goat', 'p':12, 'k':['sleepless goat', 'goat'] }, { 't':'A cafe on Princess', 'p':11, 'k':['princess', 'cafe', 'local'] }, { 't':'At home', 'p':9, 'k':['home', 'make it', 'keurig', 'nespresso'] }] },
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
tame = [b for b in sd if not b.get('spicy')] + NEW_BOARDS + [b for b in EXTRA_BOARDS if not b['spicy']]
spicy = [b for b in sd if b.get('spicy')] + [b for b in EXTRA_BOARDS if b['spicy']]
# Day 1 keeps the two boards from the demo. After that: one milder board, then one spicier board each day.
first = EXISTING_DAILY
photos = {p['id']: p for p in json.load(open(SP + '/droppin/photos.json'))}
N = 35   # through Dec 7, the last week of classes
# ---- CURATED FIRST WEEK (Nov 4): the best questions and the best-known spots go first, while new players are arriving.
# Each line: (Receipts 1, Showdown board 1, Receipts 2, Showdown board 2, photo). Receipts are matched by the start of the question.
CURATED = {
  1: ("hooked up with someone from your first-year floor", 'runinto',  "DMed someone you saw at the ARC",          'parents',    'grant1905'),
  2: ("Do you think engineers are annoying",                                 'engineers', "situationship that lasted longer",       'aberdeen',   'princess1899'),
  3: ("Would you date someone who goes to Western",                      'western',   "hooked up with someone in your program", 'hookupspot', 'richardson2019'),
  4: ("Commerce kids act like",                         'commerce',  "walked home from Aberdeen",                 'groupchat',  'market1902'),
  5: ("Do you think your roommate is the messy one",                      'hoco',      "texted your ex after a night out",       'underbed',   'pitapit2019'),
  6: ("Do you think Artsci",                              'stauffer',  "been kicked out of a house party",       'ex2am',      'fort1920'),
  7: ("Do you think Kin students",       'line',      "gone on a date with someone from your faculty", 'leaveparty', 'eclipse2024'),
}
LATER_PHOTOS = ['goodes2015', 'queen1959', 'jduc2025', 'pen2013', 'cityhall2017', 'mcd2023', 'fdr1938', 'mcburney2024', 'buskers2014', 'chalmers2009', 'ferry2008', 'leons2021', 'drydock1891', 'murney2024', 'fort2011', 'courthouse2010', 'grant2023', 'pen1919', 'skeleton2019', 'police1906', 'bk2023', 'murney1912', 'arena2008', 'barriefield1920', 'transit2012', 'murney1923', 'cavalry1916']
allboards = {b['id']: b for b in tame + spicy}
ALLQ = RECEIPTS + SEND_QS
def rec(start):
    m = [r for r in ALLQ if start.lower() in r[0].lower()]; assert len(m) == 1, start; return m[0]
def send_of(r):
    if len(r) > 2: return r[2]
    for k, v in SEND_HINTS.items():
        if k.lower() in r[0].lower(): return v
    return None
clean = lambda b: { 'type':'survey', 'q':b['q'], 'a':[{ 't':x['t'], 'p':x['p'], 'k':x['k'] } for x in b['a']] }
def day(r1, b1, r2, b2, p):
    R = lambda r: dict({ 'type':'receipts', 'q':r[0], 'pct':r[1] }, **({ 'send':send_of(r) } if send_of(r) else {}))
    return { 'rounds':[ R(r1), clean(b1), R(r2), clean(b2),
        { 'type':'pin', 'photo':{ k: p[k] for k in ['img','year','lat','lng','title','blurb','credit','license','source'] } } ] }
plan = {0: (RECEIPTS[0], first[0], RECEIPTS[1], first[1], photos['cavalry1916'])}   # day 1 already happened: keep it exactly
for d, (a, b, c, e, ph) in CURATED.items(): plan[d] = (rec(a), allboards[b], rec(c), allboards[e], photos[ph])
used_r = {x for v in plan.values() for x in (v[0][0], v[2][0])}
used_b = {x for v in plan.values() for x in (v[1]['q'], v[3]['q'])}
used_p = {v[4]['id'] for v in plan.values()}
left_r = [r for r in RECEIPTS if r[0] not in used_r]
left_t = [b for b in tame if b['q'] not in used_b]; left_s = [b for b in spicy if b['q'] not in used_b]
left_p = [photos[i] for i in LATER_PHOTOS if i not in used_p]
for d in range(N):
    if d in plan: continue
    r1, r2 = left_r.pop(0), left_r.pop(0)
    b1 = left_t.pop(0) if left_t else left_s.pop(0)
    b2 = left_s.pop(0) if left_s else left_t.pop(0)
    plan[d] = (r1, b1, r2, b2, left_p.pop(0) if left_p else photos['grant1905'])   # out of photos: repeat a famous one (we need more photos!)
days = [day(*plan[d]) for d in range(N)]
used = [d['rounds'][1]['q'] for d in days] + [d['rounds'][3]['q'] for d in days]
assert len(set(used)) == len(used), 'repeat board'
open(SP + '/daily/parts/days.js', 'w').write('const DAYS = ' + json.dumps(days, ensure_ascii=False) + ';\n')
print('days', len(days), 'boards', len(used), 'tame', len(tame), 'spicy', len(spicy))

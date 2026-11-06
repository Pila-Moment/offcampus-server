/* ================= TODAY'S DAILY (edit the content here) =================
   Demo note: the Receipts percentages and Survey boards are made up for now.
   Every guess typed in the Survey rounds will become real answer data later.
   Round order alternates: Receipts, Showdown, Receipts, Showdown, then the photo. */
const DAY = {
  school: "Queen's", no: 1, date: 'Tue, Nov 3',
  rounds: [
    { type:'receipts', q:"Have you ever gone to Stauffer just to see someone?", pct:41 },
    { type:'survey', q:"Name something you'll find in every University District house.", a:[
      { t:'A beer pong table', p:28, k:['pong','beer pong','pong table','table','beirut'] },
      { t:'Mould', p:21, k:['mould','mold','black mold','black mould','damp','mildew'] },
      { t:'A couch on the porch', p:16, k:['couch','porch couch','sofa','porch','futon'] },
      { t:'A stolen street sign', p:13, k:['sign','street sign','stop sign','stolen sign','road sign','pylon','cone'] },
      { t:'String lights', p:12, k:['lights','string lights','fairy lights','christmas lights','led lights','led strip','fairy'] },
      { t:'A dead plant', p:10, k:['plant','dead plant','plants','cactus'] } ]},
    { type:'receipts', q:"Have you ever hooked up with someone from your first-year floor?", pct:27 },
    { type:'survey', q:"Name the first thing you do when you wake up hungover.", a:[
      { t:'Check my phone', p:30, k:['phone','check phone','texts','snap','snapchat','instagram','insta','messages','who i texted'] },
      { t:'Drink water', p:22, k:['water','drink water','gatorade','hydrate','liquid iv','electrolytes','pedialyte'] },
      { t:'Order food', p:18, k:['food','order food','uber eats','skip','doordash','osmows','pizza','mcdonalds','eat','breakfast','greasy food'] },
      { t:'Check my bank account', p:12, k:['bank','bank account','money','account','card','spent','venmo','etransfer'] },
      { t:'Go back to sleep', p:10, k:['sleep','go back to sleep','back to bed','nap','bed','roll over'] },
      { t:'Ask the group chat', p:8, k:['group chat','gc','ask friends','what happened','friends','chat'] } ]},
    { type:'pin', photo:{ img:'photos/cavalry1916.jpg', year:1916, lat:44.2268, lng:-76.4895, title:'Cavalry in City Park',
      blurb:"The 53rd Battery riding through the snow in City Park, in front of the Court House, in the middle of the First World War. Thousands of soldiers trained in Kingston before shipping overseas.",
      now:"Today: the same Court House still faces City Park from Court Street.",
      credit:'Marsden Kemp, Archives of Ontario', license:'Public domain', source:'https://commons.wikimedia.org/wiki/File:53_Battery,_Lieut._Patterson,_Mar._4,_(19)16_-_(cavalry_in_front_of_Frontenac_County_Court_House_in_Kingston)_(I0012927).tif' } }
  ]
};

/* ================= SAMPLE PRIZES (made-up Kingston spots for the demo) =================
   slice = how big the spot's slice is on the first wheel. Bigger prizes get bigger slices. */
const BRANDS = [
  { id:'night', name:'Night Shift', short:'NIGHT SHIFT', kind:'Club · student nights · 19+', col:'#B03BD1', mono:'NS', slice:1.5, prizes:[{ t:'Skip the line on Saturday', s:'SKIP LINE', w:4 }, { t:'2 free entries', s:'2 FREE IN', w:1, big:true }] },
  { id:'bean', name:'Limestone Bean Co.', short:'LIMESTONE BEAN', kind:'Coffee · Princess St', col:'#C8782A', mono:'LB', slice:1, prizes:[{ t:'15% off any drink', s:'15% OFF', w:4 }, { t:'A free latte', s:'FREE LATTE', w:1, big:true }] },
  { id:'lock', name:'Locked In Escapes', short:'LOCKED IN', kind:'Escape rooms · downtown', col:'#6C4BE0', mono:'LI', slice:1.3, prizes:[{ t:'20% off any room', s:'20% OFF', w:4 }, { t:'A free room for 4', s:'FREE ROOM', w:1, big:true }] },
  { id:'crumb', name:'Crumb Club Cookies', short:'CRUMB CLUB', kind:'Cookies · pre-order drops', col:'#E8608A', mono:'CC', slice:1, prizes:[{ t:'Buy 2 cookies, get 1 free', s:'BUY 2 GET 1', w:4 }, { t:'A free cookie', s:'FREE COOKIE', w:1, big:true }] },
  { id:'axe', name:'Splitwood Axe Throwing', short:'SPLITWOOD', kind:'Axe throwing · groups', col:'#3E8E5A', mono:'SA', slice:1.2, prizes:[{ t:'2-for-1 lane booking', s:'2 FOR 1', w:4 }, { t:'A free lane for 4', s:'FREE LANE', w:1, big:true }] },
  { id:'flow', name:'Pole & Flow Studio', short:'POLE & FLOW', kind:'Fitness classes', col:'#D04545', mono:'PF', slice:.9, prizes:[{ t:'A free beginner class', s:'FREE CLASS', w:4 }, { t:'A free 3-class pass', s:'3-CLASS PASS', w:1, big:true }] },
  { id:'supply', name:'Stuart St. Supply', short:'STUART ST.', kind:'Student-made merch', col:'#2E5BD8', mono:'SS', slice:1, prizes:[{ t:'15% off any crewneck', s:'15% OFF', w:4 }, { t:'A free crewneck', s:'FREE CREW', w:1, big:true }] },
  { id:'clean', name:'Fresh Start Crew', short:'FRESH START', kind:'Student house cleaning', col:'#2BA3C7', mono:'FS', slice:.8, prizes:[{ t:'$10 off a house clean', s:'$10 OFF', w:4 }, { t:'A free kitchen deep clean', s:'FREE CLEAN', w:1, big:true }] }
];
const JACKPOT = { id:'jackpot', name:'The Weekly Jackpot', short:'JACKPOT', kind:'One winner a week', col:'#FFC83D', mono:'★', slice:.45,
  prize:{ t:'2 VIP tickets to Saturday at Night Shift (19+)', big:true } };


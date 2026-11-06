/* ================= BRAND PREVIEW LINKS =================
   Send a business their own link and they show up in the game:
   daily.html?spot=Lazy%20Scholar&offer=15%25%20off%20any%20drink&big=A%20free%20latte&col=C8782A&kind=Coffee
   Their spot is added to the spinner, the spinner always lands on them, and they can skip straight to the prize. */
const QS = new URLSearchParams(location.search);
const GUEST = (() => {
  const n = (QS.get('spot') || '').trim().slice(0, 40); if (!n) return null;
  const offer = (QS.get('offer') || 'A student deal').trim().slice(0, 60), big = (QS.get('big') || '').trim().slice(0, 60);
  let col = (QS.get('col') || '').trim().replace('#', ''); col = /^[0-9a-f]{6}$/i.test(col) ? '#' + col : '#E3262B';
  const words = n.split(/\s+/).filter(w => /[a-z0-9]/i.test(w));
  const mono = (words.length > 1 ? words[0][0] + words[1][0] : n.replace(/[^a-z0-9]/gi, '').slice(0, 2)).toUpperCase();
  const lab = t => { const w = t.toUpperCase().split(/\s+/); let s = ''; for (const x of w) { if ((s + ' ' + x).trim().length > 12) break; s = (s + ' ' + x).trim(); } return s || w[0].slice(0, 12); };
  const prizes = [{ t:offer, s:lab(offer), w:4 }];
  prizes.push(big ? { t:big, s:lab(big), w:1, big:true } : { t:offer, s:lab(offer), w:1 });
  return { id:'guest', name:n, short:n.toUpperCase().slice(0, 14), kind:(QS.get('kind') || 'Kingston').trim().slice(0, 40), col, mono, slice:1.2, prizes };
})();
if (GUEST) BRANDS.unshift(GUEST);


"""Controleert de systematiek van de Code civil (`seed/systematiek_fr.py`) tegen de officiële LEGI-indeling.

Leest de geïmporteerde Code civil (`wettekst_artikel.pad`, uit de LEGI-dump) alleen-lezend en meldt per knoop:
een andere titel dan de LEGI-sectie die precies zijn artikelen omvat, een LEGI-sectie die verder loopt dan het
bereik, en titres van de Code die in de boom ontbreken. Geen uitvoer behalve 'fouten: 0' = alles klopt.

    .venv/bin/python scripts/systematiek_fr_controle.py [pad/naar/synoptikon.db]
"""
import re, sqlite3, sys, unicodedata
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from synoptikon.seed.systematiek_fr import CC
DB = sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).resolve().parent.parent / "data" / "synoptikon.db")
BEWUST = {"CC-IV-DG"}  # staat in de Code zonder eigen kop direct onder Livre IV
db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
rows = db.execute("select a.nummer,a.pad from wettekst_artikel a join wettekst w on w.id=a.wettekst_id where w.wet_id='LEGITEXT000006070721' order by a.volgorde").fetchall()
nums = [n for n,_ in rows]; idx = {n:i for i,n in enumerate(nums)}
paths = [tuple(s.strip() for s in (p or '').split('›') if s.strip()) for _,p in rows]
def norm(s):
    s = unicodedata.normalize('NFKD', s).encode('ascii','ignore').decode().lower()
    s = re.sub(r'\b1er\b','ier',s); s=re.sub(r'^(section|chapitre|titre|sous-titre|paragraphe|sous-section) 1\b',r'\1 ier',s)
    return re.sub(r'[^a-z0-9]+', ' ', s).strip()
def rng(r):
    r = r.replace('art. ','')
    a,_,b = r.partition('–'); return a.strip(), (b or a).strip()
def lcp(ps):
    p = ps[0]
    for q in ps[1:]:
        k=0
        while k<len(p) and k<len(q) and p[k]==q[k]: k+=1
        p=p[:k]
    return p
seen=set()
fouten=0
def walk(nodes, parent_off):
    global fouten
    for code, titel, r, kids in nodes:
        a,b = rng(r)
        if a not in idx or b not in idx: print(f"?? {code} {r}: grensartikel ontbreekt in LEGI"); walk(kids, None); continue
        i,j = idx[a], idx[b]
        off = lcp(paths[i:j+1])
        naam = titel.replace(' · ',' : ')
        last = off[-1] if off else '(geen)'
        ok_t = off and norm(last) == norm(naam)
        # bereik: valt de officiële sectie buiten ons bereik?
        out = [nums[k] for k in range(len(nums)) if not (i<=k<=j) and paths[k][:len(off)]==off] if off else []
        if i == j and any(norm(x) == norm(naam) for x in off): msg = ''
        elif code in BEWUST: msg = ''
        elif off == parent_off: msg = f"geen eigen officiële sectie (zelfde als ouder: '{last}')"
        elif not ok_t: msg = f"titel ≠ LEGI '{last}'"
        else: msg = ''
        if out and code not in BEWUST: msg += f"  | LEGI-sectie loopt verder: {out[0]}…{out[-1]} ({len(out)})"
        if msg: fouten += 1; print(f"{code:18} {titel[:60]:60} {r}\n{'':18} {msg}")
        if i == j:  # één artikel: de LEGI-prefix tot en met de kop met deze titel
            k = next((k for k, x in enumerate(off) if norm(x) == norm(naam)), len(off) - 1)
            off = off[:k + 1]
        seen.add(off)
        walk(kids, off)
walk(CC, ())
# officiële koppen tot titre-niveau die we niet hebben
offs = set()
for p in paths:
    for k in range(1, min(len(p),2)+1): offs.add(p[:k])
for o in sorted(offs, key=lambda o: min(i for i,p in enumerate(paths) if p[:len(o)]==o)):
    if o not in seen: fouten += 1; print("ONTBREEKT", ' › '.join(o))
print("fouten:", fouten)
sys.exit(1 if fouten else 0)

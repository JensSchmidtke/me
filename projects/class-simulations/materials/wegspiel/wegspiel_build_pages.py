"""Step 3: check every route by walking it, then write wegspiel_schueler.html and wegspiel_lehrer.html (to the folder given as argument, default: this folder)."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
import json, random, math
from wegspiel_layout import *
LY=json.load(open(os.path.join(HERE,'wegspiel_layout.json')))
E2=[E(tuple(a),tuple(b)) for a,b in LY['edges']]; nb=adjacency(E2)
am={int(k):(E(tuple(v[0][0]),tuple(v[0][1])),tuple(v[1])) for k,v in LY['am'].items()}
words={(a,b):route(nb,am[a][0],am[a][1],am[b][0]) for a,b in legs}
def walk(a,ws):
    e0,f=am[a]; p,q=e0
    d={'rechts':(-f[1],f[0]),'links':(f[1],-f[0])}[ws[0]]
    if sub(q,p)==d: u,v=p,q
    elif sub(p,q)==d: u,v=q,p
    else: return None
    for w in ws[1:]:
        h=sub(v,u); d={'geradeaus':h,'rechts':(-h[1],h[0]),'links':(h[1],-h[0])}[w]
        n=(v[0]+d[0],v[1]+d[1])
        if n not in nb[v]: return None
        u,v=v,n
    return E(u,v)
bad=[(a,b) for (a,b),ws in words.items() if ws is None or walk(a,ws)!=am[b][0]]
print("failed:",bad)
def red(N):
    m=99
    for i in range(N):
        for a,b in zip(S[i],S[i][1:]):
            m=min(m,sum(1 for j in range(N) if j!=i and a in L[j] and b in L[j]))
    return m
print([red(N) for N in range(5,13)])
print("bridges used by places:",[p for p,(e,f) in am.items() if e in BRIDGES])

def runs():
    out=[]
    es=set(E2)
    for y in range(H):
        cur=[]
        for x in range(W-1):
            e=E((x,y),(x+1,y))
            if e in es: cur.append(e)
            else:
                if cur: out.append(cur)
                cur=[]
        if cur: out.append(cur)
    for x in range(W):
        cur=[]
        for y in range(H-1):
            e=E((x,y),(x,y+1))
            if e in es: cur.append(e)
            else:
                if cur: out.append(cur)
                cur=[]
        if cur: out.append(cur)
    return [r for r in out if len(r)>=3]
LONG=runs()
NAMES=["Hauptstraße","Gartenstraße","Lindenstraße","Goethestraße","Schillerstraße","Bahnhofstraße","Parkstraße"]
STREETNAME={}
for k,r in enumerate(LONG):
    for e in r: STREETNAME[e]=NAMES[k]
print("long streets:",[(NAMES[k],len(r)) for k,r in enumerate(LONG)])

rj=random.Random(2); JIT={j:(rj.uniform(-8,8),rj.uniform(-8,8)) for j in J}
def P(j): x,y=pxy(j); return (x+JIT[j][0],y+JIT[j][1])
BNAMES=['Bahnhof','Rathaus','Museum','Park','Hotel','Café','Restaurant','Kino','Theater','Schule','Universität','Post','Markt','Stadion','Schwimmbad','Kirche','Hafen']
def svg(lab,names=None,nonum=False):
    xs=[P(j)[0]+12 for j in J]; ys=[P(j)[1]+12 for j in J]; x0s=[P(j)[0]-12 for j in J]; y0s=[P(j)[1]-12 for j in J]
    for p,(e,f) in am.items():
        (xa,ya),(xb,yb)=P(e[0]),P(e[1]); off=HW/2+14 if f[0]!=0 else HH/2+14
        cx,cy=(xa+xb)/2-f[0]*off,(ya+yb)/2-f[1]*off; xs.append(cx+HW/2+10); ys.append(cy+HH/2+10); x0s.append(cx-HW/2-10); y0s.append(cy-HH/2-10)
    X0=min(x0s)-4; Y0=min(y0s)-4; w=max(xs)+4-X0; h=max(ys)+4-Y0
    o=[f'<svg viewBox="{X0:.1f} {Y0:.1f} {w:.1f} {h:.1f}" xmlns="http://www.w3.org/2000/svg"><rect x="{X0:.1f}" y="{Y0:.1f}" width="{w:.1f}" height="{h:.1f}" fill="#f4f0e6"/>']
    x0,y0,x1,y1=PARK
    o.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" rx="14" fill="#a9d18e" stroke="#6c9a4f" stroke-width="2"/>')
    for (tx,ty) in [(0.5,0.3),(1.2,0.6),(1.9,0.3),(2.0,0.7),(0.9,0.25),(1.5,0.45)]:
        o.append(f'<circle cx="{PAD+tx*SPX*0.95}" cy="{PAD+ty*SPY}" r="9" fill="#6c9a4f"/>')
    xc=PAD+2.5*SPX; pl=[];pr=[]
    for k in range(0,41):
        y=Y0-10+k*(h+20)/40; dx=14*math.sin(k/3.2); pl.append((xc+dx-19,y)); pr.append((xc+dx+19,y))
    d='M'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pl)+' L'+' L'.join(f'{x:.1f},{y:.1f}' for x,y in pr[::-1])+' Z'
    o.append(f'<path d="{d}" fill="#9ccbe8" stroke="#6aa5c9" stroke-width="2"/>')
    for a,b in E2:
        (xa,ya),(xb,yb)=P(a),P(b); wd=21 if E(a,b) in STREETNAME else 13
        o.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#555" stroke-width="{wd}" stroke-linecap="round"/>')
    for a,b in E2:
        (xa,ya),(xb,yb)=P(a),P(b); wd=17 if E(a,b) in STREETNAME else 8
        o.append(f'<line x1="{xa:.1f}" y1="{ya:.1f}" x2="{xb:.1f}" y2="{yb:.1f}" stroke="#fff" stroke-width="{wd}" stroke-linecap="round"/>')
    for k,r in enumerate(LONG):
        e=r[len(r)//2]; (xa,ya),(xb,yb)=P(e[0]),P(e[1]); mx,my=(xa+xb)/2,(ya+yb)/2
        if e[0][1]==e[1][1]: o.append(f'<text x="{mx:.1f}" y="{my+4:.1f}" text-anchor="middle" font-size="12" font-family="Helvetica,Arial" fill="#222">{NAMES[k]}</text>')
        else: o.append(f'<text transform="translate({mx:.1f},{my:.1f}) rotate(-90)" y="4" text-anchor="middle" font-size="12" font-family="Helvetica,Arial" fill="#222">{NAMES[k]}</text>')
    for j in J:
        x,y=P(j); o.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="5" fill="#555"/>')
    for p,(e,f) in am.items():
        (xa,ya),(xb,yb)=P(e[0]),P(e[1]); off=HW/2+14 if f[0]!=0 else HH/2+14
        cx,cy=(xa+xb)/2-f[0]*off,(ya+yb)/2-f[1]*off
        o.append(f'<rect x="{cx-HW/2:.1f}" y="{cy-HH/2:.1f}" width="{HW}" height="{HH}" fill="#fff" stroke="#222" stroke-width="3"/>')
        dx,dy=cx+f[0]*HW/2,cy+f[1]*HH/2
        if f[0]==0: o.append(f'<rect x="{dx-9:.1f}" y="{dy-3:.1f}" width="18" height="6" fill="#222"/>')
        else: o.append(f'<rect x="{dx-3:.1f}" y="{dy-9:.1f}" width="6" height="18" fill="#222"/>')
        if names and nonum:
            o.append(f'<text x="{cx:.1f}" y="{cy+5:.1f}" text-anchor="middle" font-size="{12 if len(names[p])>9 else 14}" font-family="Helvetica,Arial" font-weight="bold">{names[p]}</text>')
        elif names:
            o.append(f'<text x="{cx:.1f}" y="{cy-3:.1f}" text-anchor="middle" font-size="14" font-family="Helvetica,Arial" font-weight="bold">{p+1}</text><text x="{cx:.1f}" y="{cy+11:.1f}" text-anchor="middle" font-size="13" font-family="Helvetica,Arial">{names[p]}</text>')
        elif p in lab: o.append(f'<text x="{cx:.1f}" y="{cy+5:.1f}" text-anchor="middle" font-size="13" font-family="Helvetica,Arial" font-weight="bold">{BNAMES[p]}</text>')
    o.append('</svg>'); return ''.join(o)
css="""<meta charset=utf-8><style>@page{size:A4 landscape;margin:8mm}body{font-family:Helvetica,Arial,sans-serif;margin:0}
.p{page-break-after:always;padding:2mm}h1{font-size:18pt;margin:0 0 2mm;display:inline}.q{font-size:15pt;margin:0 0 1mm}.n{font-size:12pt;color:#333}
svg{width:225mm;display:block;margin:2mm auto}table{border-collapse:collapse;font-size:10pt}td,th{border:1px solid #999;padding:2px 6px}</style>"""
base=(sys.argv[1] if len(sys.argv)>1 else HERE)+'/'
GEN={'Bahnhof':'m','Rathaus':'n','Museum':'n','Park':'m','Hotel':'n','Café':'n','Restaurant':'n','Kino':'n','Theater':'n','Schule':'f','Universität':'f','Post':'f','Markt':'m','Stadion':'n','Schwimmbad':'n','Kirche':'f','Hafen':'m'}
def von(n): return ('von der ' if GEN[n]=='f' else 'vom ')+n
def zu(n): return ('zur ' if GEN[n]=='f' else 'zum ')+n
css2="""<meta charset=utf-8><style>@page{size:A4 portrait;margin:6mm}body{font-family:Helvetica,Arial,sans-serif;margin:0}
.sheet{page-break-after:always}.half{height:141mm;overflow:hidden;border-bottom:1px dashed #aaa}.half:last-child{border-bottom:none}
.hd{display:flex;gap:5mm;align-items:center;margin:1mm 0 0 0}.who{width:44mm}h1{font-size:14pt;margin:0}.legs{display:grid;grid-template-columns:1fr 1fr;gap:0 4mm;font-size:11pt;flex:1}.legs span{white-space:nowrap}
.fr{font-size:10pt;color:#444}svg{width:182mm;display:block;margin:1mm auto}</style>"""
pg=[css2]
halves=[]
for i in range(12):
    s=S[i]; nm=[BNAMES[x] for x in s]
    legs_html=''.join(f'<span>{k+1}) {von(nm[k])} &rarr; {zu(nm[k+1])}</span>' for k in range(4))
    halves.append(f'<div class=half><div class=hd><div class=who><h1>Teilnehmer/in {i+1}</h1><div class=fr>Wie komme ich …?</div></div><div class=legs>{legs_html}</div></div>{svg(set(L[i]))}</div>')
for k in range(0,12,2): pg.append('<div class=sheet>'+''.join(halves[k:k+2])+'</div>')
open(base+'wegspiel_schueler.html','w').write(''.join(pg))
t=[css,'<div class=p><h1>Lehrer: alle Orte</h1>',svg(set(range(17)),BNAMES),'<div class=n>Orte 13–17 sind Füller (nie beschriftet, nie ein Ziel).</div></div>']
t.append('<div class=p><h1>Wege (ein Beispiel pro Strecke)</h1><div class=n>1. Wort: von der Tür aus links/rechts die Straße entlang. Dann ein Wort pro Kreuzung. Das letzte Wort führt in die Straße, in der das Ziel liegt.</div><table><tr><th>von</th><th>nach</th><th>Weg</th></tr>')
for (a,b),ws in sorted(words.items()): t.append(f'<tr><td>{a+1}</td><td>{b+1}</td><td>{", ".join(ws)}</td></tr>')
t.append('</table></div><div class=p><h1>Wer kennt was</h1><table><tr><th>Teilnehmer/in</th><th>Reihenfolge</th><th>Karte zeigt</th></tr>')
for i in range(12): t.append(f'<tr><td>{i+1}</td><td>{" – ".join(str(x+1) for x in S[i])}</td><td>{", ".join(str(x+1) for x in sorted(L[i]))}</td></tr>')
t.append('</table><br><table><tr><th>Teilnehmer</th>'+''.join(f'<th>{n}</th>' for n in range(5,13))+'</tr><tr><td>min. Helfer pro Schritt</td>'+''.join(f'<td>{red(n)}</td>' for n in range(5,13))+'</tr></table></div>')
open(base+'wegspiel_lehrer.html','w').write(''.join(t)); print("written")

# Practice map: same streets, river and park, the 17 house names shuffled so that no name stays where it is on the game maps.
_rng=random.Random(4)
while True:
    _perm=list(range(17)); _rng.shuffle(_perm)
    if all(_perm[i]!=i for i in range(17)): break
_names=[BNAMES[_perm[i]] for i in range(17)]
_css3="""<meta charset=utf-8><style>@page{size:A4 landscape;margin:8mm}body{font-family:Helvetica,Arial,sans-serif;margin:0}h1{font-size:16pt;margin:0 0 2mm}svg{width:270mm;display:block;margin:0 auto}</style>"""
open(base+'wegspiel_uebungskarte.html','w').write(_css3+'<h1>Übungskarte</h1>'+svg(set(range(17)),_names,True))
print("practice map written; moved names:",sum(1 for i in range(17) if _names[i]!=BNAMES[i]),"of 17")
# Empty map: same streets/river/park/houses, no names
open(base+'wegspiel_leerekarte.html','w').write(_css3+'<h1>Leere Karte</h1>'+svg(set()))

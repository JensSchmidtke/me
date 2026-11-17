"""Step 2: street layout + house positions. Reads wegspiel_design.json, writes wegspiel_layout.json (or the path given as argument)."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
import json, random, math
from collections import deque, Counter
D=json.load(open(os.path.join(HERE,'wegspiel_design.json'))); S=D['S']; L=D['L']
legs=sorted({(a,b) for s in S for a,b in zip(s,s[1:])})
W,H=5,4
J=[(x,y) for y in range(H) for x in range(W)]
def E(a,b): return tuple(sorted((a,b)))
ALL=[E((x,y),(x+1,y)) for y in range(H) for x in range(W-1)]+[E((x,y),(x,y+1)) for y in range(H-1) for x in range(W)]
def sub(p,q): return (p[0]-q[0],p[1]-q[1])
def rel(h,d):
    if d==h: return 'geradeaus'
    if d==(-h[1],h[0]): return 'rechts'
    if d==(h[1],-h[0]): return 'links'
# fixed features
RIVER_COL=2   # river between column 2 and 3
BRIDGES={E((2,1),(3,1)),E((2,3),(3,3))}
RIVER_CROSS={E((2,y),(3,y)) for y in range(H)}
PARK_CELLS=[(0,0),(1,0)]            # cells = (x,y) top-left junction; park covers x 0..2, y 0..1
PARK_INNER=E((1,0),(1,1))
def adjacency(edges):
    nb={j:[] for j in J}
    for a,b in edges: nb[a].append(b); nb[b].append(a)
    return nb
def connected(edges):
    nb=adjacency(edges); seen={J[0]}; q=[J[0]]
    for x in q:
        for y in nb[x]:
            if y not in seen: seen.add(y); q.append(y)
    return len(seen)==len(J)
def route(nb,e0,f,e1):
    a,b=e0; q=deque(); seen={}
    for i,j in ((a,b),(b,a)):
        w=rel(f,sub(j,i)); seen[(i,j)]=[w]; q.append((i,j))
    while q:
        u,v=q.popleft(); ws=seen[(u,v)]
        if E(u,v)==e1: return ws
        h=sub(v,u)
        for w in nb[v]:
            if w==u: continue
            if (v,w) not in seen: seen[(v,w)]=ws+[rel(h,sub(w,v))]; q.append((v,w))
    return None
# geometry for banning faces (unjittered)
SPX=130; SPY=105; PAD=80; HW=80; HH=34
def pxy(j): return (PAD+j[0]*SPX, PAD+j[1]*SPY)
PARK=(PAD+8, PAD+8, PAD+2*SPX-8, PAD+1*SPY-8)   # x0,y0,x1,y1
RIV=(PAD+2.5*SPX-20, PAD+2.5*SPX+20)
def building_center(e,f):
    (x1,y1),(x2,y2)=pxy(e[0]),pxy(e[1]); off=HW/2+14 if f[0]!=0 else HH/2+14
    return ((x1+x2)/2-f[0]*off,(y1+y2)/2-f[1]*off)
def rect(e,f):
    cx,cy=building_center(e,f); return (cx-HW/2,cy-HH/2,cx+HW/2,cy+HH/2)
def overlap(r1,r2,m=6): return r1[0]-m<r2[2] and r2[0]-m<r1[2] and r1[1]-m<r2[3] and r2[1]-m<r1[3]
def face_ok(e,f):
    r=rect(e,f)
    if overlap(r,PARK,3): return False
    if overlap(r,(RIV[0]-14,-1e9,RIV[1]+14,1e9),3): return False
    if r[0]<12 or r[1]<12: return False
    return True
def faces(e): 
    fs=[(0,1),(0,-1)] if e[0][1]==e[1][1] else [(1,0),(-1,0)]
    return [f for f in fs if face_ok(e,f)]
def make_edges(rng):
    while True:
        E_=[e for e in ALL if e not in RIVER_CROSS and e!=PARK_INNER]+list(BRIDGES)
        extra=rng.sample([e for e in E_ if e not in BRIDGES],4)
        E2=[e for e in E_ if e not in extra]
        nb=adjacency(E2)
        if not connected(E2): continue
        deg=[len(nb[j]) for j in J]
        if min(deg)<1 or sum(1 for d in deg if d==1)>2: continue
        slots=[e for e in E2 if e not in BRIDGES and faces(e)]
        if len(slots)>=19: return E2,nb,slots
def solve(rng):
    E2,nb,slots=make_edges(rng)
    M={}
    for e0 in slots:
        for f in faces(e0):
            for e1 in slots:
                if e1!=e0: M[(e0,f,e1)]=route(nb,e0,f,e1)
    def quad(e):
        (x1,y1),(x2,y2)=pxy(e[0]),pxy(e[1]); mx,my=(x1+x2)/2,(y1+y2)/2
        return (mx>PAD+2.5*SPX, my>PAD+1.5*SPY)
    def cost(am):
        c=0
        rs=[rect(am[i][0],am[i][1]) for i in range(17)]
        c+=1000*sum(1 for i in range(17) for j in range(i+1,17) if overlap(rs[i],rs[j]))
        cr=Counter(quad(am[i][0]) for i in range(12)); cf=Counter(quad(am[i][0]) for i in range(12,17))
        for q in [(False,False),(True,False),(False,True),(True,True)]:
            c+=50*(max(0,2-cr[q])+max(0,cr[q]-4)+max(0,1-cf[q])+max(0,cf[q]-2))
        for a,b in legs:
            e0,f=am[a]; r=M[(e0,f,am[b][0])]
            if r is None: return 10**6
            c+=len(r)+(10 if len(r)>4 else 0)
        return c
    es=rng.sample(slots,17); am={i:(es[i],rng.choice(faces(es[i]))) for i in range(17)}
    c=cost(am)
    for it in range(5000):
        i=rng.randrange(17); old=am[i]; r=rng.random()
        if r<0.35:
            free=[e for e in slots if e not in [v[0] for v in am.values()]]
            if not free: continue
            e=rng.choice(free); am[i]=(e,rng.choice(faces(e)))
            c2=cost(am)
            if c2<=c: c=c2
            else: am[i]=old
        elif r<0.55:
            am[i]=(old[0],rng.choice(faces(old[0]))); c2=cost(am)
            if c2<=c: c=c2
            else: am[i]=old
        else:
            j=rng.randrange(17)
            if j==i: continue
            oj=am[j]
            fi=old[1] if old[1] in faces(oj[0]) else faces(oj[0])[0]
            fj=oj[1] if oj[1] in faces(old[0]) else faces(old[0])[0]
            am[i],am[j]=(oj[0],fi),(old[0],fj); c2=cost(am)
            if c2<=c: c=c2
            else: am[i],am[j]=old,oj
    return c,am,E2,nb,M
if __name__=='__main__':
    rng=random.Random(11); best=None
    for t in range(30):
        r=solve(rng)
        if best is None or r[0]<best[0]: best=r; print(t,r[0],flush=True)
    c,am,E2,nb,M=best
    words={(a,b):M[(am[a][0],am[a][1],am[b][0])] for a,b in legs}
    lens=[len(v) for v in words.values()]
    print("max",max(lens),"avg",round(sum(lens)/len(lens),2),sorted(Counter(lens).items()),"edges",len(E2))
    json.dump({'edges':[list(map(list,e)) for e in E2],'am':{str(k):[list(map(list,v[0])),list(v[1])] for k,v in am.items()}},open(sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'wegspiel_layout.json'),'w'))

"""Step 1: choose each participant's route (start + 3 stops + final) and which places each map labels,
so that every step of every route can be answered by (at least) one other participant for every class size 5-12.
Writes wegspiel_design.json (or the path given as argument). Seeded, so it reproduces the same result."""
import os, sys, random, json
from multiprocessing import Pool
HERE=os.path.dirname(os.path.abspath(__file__))
M=12                      # real places (numbered 0..11); participant i starts at place i
W={5:6,6:3,7:2}           # extra weight for small classes (5,6,7 participants)
def build(k,rng):
    while True:
        fin=rng.sample(range(M),12)
        if all(fin[i]!=i for i in range(12)): break
    S=[]
    for i in range(12):
        pool=[x for x in range(M) if x not in (i,fin[i])]
        S.append(tuple([i]+rng.sample(pool,3)+[fin[i]]))
    L=[]
    for i in range(12):
        pool=[x for x in range(M) if x not in S[i]]
        L.append({i}|set(rng.sample(pool,k)))      # own start + k other labelled places
    return S,L
def ev(S,L):
    zero=0; excess=0
    for N in range(5,13):
        w=W.get(N,1)
        for i in range(N):
            for a,b in zip(S[i],S[i][1:]):
                h=sum(1 for j in range(N) if j!=i and a in L[j] and b in L[j])   # who can answer step a->b
                if h==0: zero+=1
                else: excess+=w*(h-1)
    return zero*1000+excess
def search(k,iters,seed):
    rng=random.Random(seed); S,L=build(k,rng); c=ev(S,L); best=(c,S[:],[set(x) for x in L])
    for _ in range(iters):
        S2=S[:];L2=[set(x) for x in L]; i=rng.randrange(12)
        if rng.random()<0.5:
            pool=[x for x in range(M) if x not in (S2[i][0],S2[i][4])]
            S2[i]=(S2[i][0],*rng.sample(pool,3),S2[i][4])
        pool=[x for x in range(M) if x not in S2[i]]
        L2[i]={S2[i][0]}|set(rng.sample(pool,k))
        c2=ev(S2,L2)
        if c2<=c or rng.random()<0.002: S,L,c=S2,L2,c2
        if c<best[0]: best=(c,S[:],[set(x) for x in L])
    return best
def job(a):
    k,seed=a; b=search(k,20000,seed); return (k,b[0],[list(s) for s in b[1]],[sorted(x) for x in b[2]])
if __name__=='__main__':
    jobs=[(k,s) for k in (4,5,6) for s in range(3)]
    with Pool(9) as p: res=p.map(job,jobs)
    best=min(res,key=lambda x:x[1])
    out=sys.argv[1] if len(sys.argv)>1 else os.path.join(HERE,'wegspiel_design.json')
    json.dump({'S':best[2],'L':best[3]},open(out,'w'))
    print("best: labelled places per map besides own start =",best[0],"cost",best[1])

"""Step 4: estimate how long the activity takes with 5 students (assumed durations)."""
import os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
import json, random, statistics as st, heapq
D=json.load(open(os.path.join(HERE,'wegspiel_design.json'))); S=D['S']; L=[set(x) for x in D['L']]
def run(N,rng,tf,ts,gap):
    free=[0.0]*N; prog=[0]*N; tried=[set() for _ in range(N)]; t=0.0
    while any(p<4 for p in prog):
        # next student to act: the one free earliest among unfinished
        cand=[i for i in range(N) if prog[i]<4]; i=min(cand,key=lambda x:(free[x],rng.random()))
        a,b=S[i][prog[i]],S[i][prog[i]+1]
        others=[j for j in range(N) if j!=i and j not in tried[i]] or [j for j in range(N) if j!=i]
        if not [j for j in range(N) if j!=i and j not in tried[i]]: tried[i]=set()
        j=rng.choice([j for j in range(N) if j!=i and j not in tried[i]])
        start=max(free[i],free[j]); ok=(a in L[j] and b in L[j]); d=ts if ok else tf
        free[i]=free[j]=start+d+gap
        if ok: prog[i]+=1; tried[i]=set()
        else: tried[i].add(j)
    return max(free)
for tf,ts in [(6,20),(8,25),(10,30)]:
    rs=[run(5,random.Random(s),tf,ts,3) for s in range(3000)]
    print(f"failed ask {tf}s, successful {ts}s, +3s change: 5 students finish after avg {st.mean(rs)/60:.1f} min (range {min(rs)/60:.1f}-{max(rs)/60:.1f})")

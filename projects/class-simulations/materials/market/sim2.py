import random,itertools
R={'sk':{'strawberry':2,'kiwi':2,'mango':1},'sm':{'strawberry':2,'banana':2,'orange':2,'apple':2},'fs':{'apple':2,'banana':2,'orange':2,'pear':2,'plum':4},
'ex':{'mango':1,'kiwi':2,'melon':1},'ts':{'tomato':2,'potato':3,'onion':2,'carrot':2},'ps':{'potato':6,'onion':2,'egg':3,'carrot':2,'apple':1}}
ST={'kiwi':[2,5],'mango':[1,7],'melon':[5,6],'tomato':[3,8],'strawberry':[4,8],'potato':[1,2],'onion':[1,3,4],'carrot':[1,6],'apple':[3,5,6],'banana':[2,5,7],'orange':[4,6,7],'pear':[2,3],'plum':[7,8],'egg':[4,8]}
RARE=['kiwi','mango','melon','tomato','strawberry']
SC={'plenty':{},'some':{p:'medium' for p in RARE},'limited':dict(kiwi='scarce',mango='scarce'),'scarce':dict(kiwi='scarce',mango='scarce',melon='scarce',tomato='scarce',strawberry='medium')}
def run(C,sc,visits=15,mem=0.5,giveup=1):
    one={}
    for c in C:
        for k in c:
            for p,n in R[k].items(): one[p]=max(one.get(p,0),n)
    lv=SC[sc];stock={p:(10**9 if lv.get(p,'unlimited')=='unlimited' else one[p]*(2 if lv[p]=='medium' else 1)) for p in one}
    cooks=[{'inv':{},'v':0,'know':{},'recs':[{'k':k,'st':'w','sold':0} for k in c]} for c in C]
    def missing(c,k): return [p for p,n in R[k].items() if c['inv'].get(p,0)<n]
    def choose(c):
        best=None;bm=99
        for r in c['recs']:
            if r['st']!='w':continue
            n=len(missing(c,r['k']))
            if n<bm or (n==bm and random.random()<.5):bm=n;best=r
        return best
    def learn(c,s,p,kind):
        if random.random()<mem:c['know'][(s,p)]=kind
    def ask(c,s,r,p):
        if p not in stock: return 'no'
        if s not in ST[p]:learn(c,s,p,'no');return 'no'
        if stock[p]<=0:
            r['sold']+=1
            if r['sold']>=giveup:r['st']='g'
            learn(c,s,p,'out');return 'no'
        need=R[r['k']][p]-c['inv'].get(p,0);take=min(need,stock[p]);c['inv'][p]=c['inv'].get(p,0)+take;stock[p]-=take
        learn(c,s,p,'sells')
        for o in c['recs']:
            if o['st']=='w' and not missing(c,o['k']):
                for q,n in R[o['k']].items():c['inv'][q]-=n
                o['st']='d'
        return 'yes'
    def active(c): return c['v']<visits and any(r['st']=='w' for r in c['recs'])
    while True:
        act=[c for c in cooks if active(c)]
        if not act:break
        random.shuffle(act)
        for c in act:
            if not active(c):continue
            r=choose(c);miss=missing(c,r['k']);p=random.choice(miss)
            good=[s for s in range(1,9) if c['know'].get((s,p))=='sells'];unk=[s for s in range(1,9) if (s,p) not in c['know']]
            s=random.choice(good) if good else random.choice(unk) if unk else random.randint(1,8)
            c['v']+=1;asked=[p];res=ask(c,s,r,p)
            while res=='no':
                r2=r if r['st']=='w' else choose(c);opts=[];r3=None
                if r2:
                    opts=[x for x in missing(c,r2['k']) if x not in asked];r3=r2
                    if not opts:
                        for o in c['recs']:
                            if o['st']=='w' and o is not r2 and not opts:
                                m=[x for x in missing(c,o['k']) if x not in asked]
                                if m:opts=m;r3=o
                if not r3 or not opts:break
                fine=[x for x in opts if c['know'].get((s,x)) in (None,'sells')]
                sure=[x for x in fine if c['know'].get((s,x))=='sells']
                if sure:fine=sure
                if not fine:break
                n=random.choice(fine);asked.append(n);res=ask(c,s,r3,n);r=r3
    return [sum(1 for r in c['recs'] if r['st']=='d') for c in cooks]
def avg(C,sc,N=1500,**kw):
    t=[0,0,0]
    for _ in range(N):
        d=run(C,sc,**kw)
        for i,x in enumerate(d):t[i]+=x
    return [round(x/N,2) for x in t]
random.seed(5)
T={'K01':['sk','sm','fs'],'K02':['ex','ts','fs'],'K04':['ex','ts','ps']}
print('current trio',{sc:avg(list(T.values()),sc) for sc in SC})
types={'A(sk,sm,fs)':['sk','sm','fs'],'B(ex,ts,fs)':['ex','ts','fs'],'C(ex,ts,ps)':['ex','ts','ps'],'D(ex,sm,fs)':['ex','sm','fs'],'E(ex,sm,ps)':['ex','sm','ps'],'F(sk,ts,fs)':['sk','ts','fs']}
res=[]
for trio in itertools.combinations(types,3):
    C=[types[t] for t in trio];spread=0;rows={}
    for sc in SC:
        a=avg(C,sc,N=600);rows[sc]=a;spread+=max(a)-min(a)
    res.append((round(spread/4,3),trio,rows))
for r in sorted(res)[:6]: print(r[0],r[1],r[2]['some'],r[2]['scarce'])

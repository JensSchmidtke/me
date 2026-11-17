import random,sys
R={'sk':{'strawberry':2,'kiwi':2,'mango':1},'sm':{'strawberry':2,'banana':2,'orange':2,'apple':2},'fs':{'apple':2,'banana':2,'orange':2,'pear':2,'plum':4},
'ex':{'mango':1,'kiwi':2,'melon':1},'ts':{'tomato':2,'potato':3,'onion':2,'carrot':2},'ps':{'potato':6,'onion':2,'egg':3,'carrot':2,'apple':1}}
C=[['sk','sm','fs'],['ex','ts','fs'],['ex','ts','ps']]
ST={'kiwi':[2,5],'mango':[1,7],'melon':[5,6],'tomato':[3,8],'strawberry':[4,8],'potato':[1,2],'onion':[1,3,4],'carrot':[1,6],'apple':[3,5,6],'banana':[2,5,7],'orange':[4,6,7],'pear':[2,3],'plum':[7,8],'egg':[4,8]}
one={}
for c in C:
    for k in c:
        for p,n in R[k].items(): one[p]=max(one.get(p,0),n)
SC={'plenty':{},'some':dict(kiwi='medium',mango='medium',melon='medium',tomato='medium',strawberry='medium'),'limited':dict(kiwi='scarce',mango='scarce'),'scarce':dict(kiwi='scarce',mango='scarce',melon='scarce',tomato='scarce',strawberry='medium')}
def run(sc,visits,second=True,giveup=1,memory=False):
    lv=SC[sc];stock={p:(10**9 if lv.get(p,'unlimited')=='unlimited' else one[p]*(2 if lv[p]=='medium' else 1)) for p in one}
    cooks=[{'inv':{},'v':0,'recs':[{'k':k,'st':'w','sold':0} for k in c],'known_no':set(),'known_yes':set()} for c in C]
    def missing(c,k): return [p for p,n in R[k].items() if c['inv'].get(p,0)<n]
    def choose(c):
        best=None;bm=99
        for r in c['recs']:
            if r['st']!='w':continue
            n=len(missing(c,r['k']))
            if n<bm or (n==bm and random.random()<.5):bm=n;best=r
        return best
    def ask(c,stall,r,p):
        if stall not in ST[p]:
            c['known_no'].add((stall,p));return 'no'
        if stock[p]<=0:
            r['sold']+=1
            if r['sold']>=giveup:r['st']='g'
            c['known_no'].add((stall,p));return 'no'
        need=R[r['k']][p]-c['inv'].get(p,0);take=min(need,stock[p]);c['inv'][p]=c['inv'].get(p,0)+take;stock[p]-=take
        if not missing(c,r['k']):
            for q,n in R[r['k']].items():c['inv'][q]-=n
            r['st']='d'
        return 'yes'
    def active(c): return c['v']<visits and any(r['st']=='w' for r in c['recs'])
    while True:
        act=[c for c in cooks if active(c)]
        if not act:break
        random.shuffle(act)
        for c in act:
            if not active(c):continue
            r=choose(c);miss=missing(c,r['k']);p=random.choice(miss)
            if memory:
                good=[s for s in range(1,9) if (s,p) not in c['known_no'] and s in ST[p]] 
                unk=[s for s in range(1,9) if (s,p) not in c['known_no']]
                stall=random.choice(unk) if unk else random.randint(1,8)
            else: stall=random.randint(1,8)
            c['v']+=1
            res=ask(c,stall,r,p)
            if res=='no' and second:
                r2=r if r['st']=='w' else choose(c)
                opts=[];r3=None
                if r2:
                    opts=[x for x in missing(c,r2['k']) if x!=p];r3=r2
                    if not opts:
                        for o in c['recs']:
                            if o['st']=='w' and o is not r2 and not opts:
                                m=[x for x in missing(c,o['k']) if x!=p]
                                if m:opts=m;r3=o
                if r3 and opts: ask(c,stall,r3,random.choice(opts))
    return [sum(1 for r in c['recs'] if r['st']=='d') for c in cooks]
def batch(sc,visits,**kw):
    N=2000;tot=[0,0,0];none=[0,0,0];a3=0
    for _ in range(N):
        d=run(sc,visits,**kw)
        for i,x in enumerate(d):tot[i]+=x;none[i]+=(x==0);a3+=(x==3)
    return [round(t/N,2) for t in tot],[round(n/N*100) for n in none],round(a3/N*100)
random.seed(1)
for sc in ['plenty','some','limited','scarce']:
    print(sc,'no memory ',batch(sc,15),'| memory ',batch(sc,15,memory=True))
print('---')
random.seed(2)
for v in (20,25):
    for sc in ['plenty','some','scarce']:
        print(v,sc,'no memory',batch(sc,v),'| memory',batch(sc,v,memory=True))

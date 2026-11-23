# engine2: 0x88 alpha-beta+QS+TT, PST eval, MVV-LVA, 40000 nodes. MIT.
import json,os
from urllib.request import*
U=os.getenv("MAKEFUN_ENV_URL")
V=(0,100,320,330,500,900,0)
KN=(14,18,31,33,-14,-18,-31,-33)
KI=(1,-1,16,-16,15,17,-15,-17)
DG=(15,17,-15,-17)
ST=(1,-1,16,-16)
QA=DG+ST
MATE=100000
BUD=40000
B=[0]*128
S=[1]
N=[0]
TT={}
class TO(Exception):pass
def setup(f):
 global B
 B=[0]*128
 p,s=f.split()[:2]
 S[0]=1 if s=="w"else 0
 q=112
 for a in p:
  if a=="/":q-=24
  elif a.isdigit():q+=int(a)
  else:
   t="pnbrqk".index(a.lower())+1;B[q]=t if a.isupper()else t+8;q+=1
def uci(m):
 a,b,c=m;g=lambda s:"abcdefgh"[s&7]+str((s>>4)+1);return g(a)+g(b)+("","","n","b","r","q")[c]
def atk(s,w):
 q=9-8*w
 for a in(s-15,s-17)if w else(s+15,s+17):
  if not a&136 and B[a]==q:return 1
 for d in KN+KI:
  a=s+d
  if not a&136 and B[a]in(q+1,q+5):return 1
 for d in QA:
  a=s+d
  while not a&136:
   v=B[a]
   if v:
    if(v<8)==w and(v&7==5 or v&7==(3 if d in DG else 4)):return 1
    break
   a+=d
 return 0
def gen(c=0):
 m=[];w=S[0]
 for f in range(128):
  if f&136:continue
  p=B[f]
  if p==0 or(p<8)!=w:continue
  t=p&7
  if t<2:
   d=16 if w else-16;r=f>>4;v=r==1+5*w;o=5 if v else 0
   if(c==0 or v)and B[f+d]==0:
    m.append((f,f+d,o))
    if r==6-5*w and B[f+2*d]==0:m.append((f,f+2*d,0))
   for u in(f+d-1,f+d+1):
    if u&136:continue
    x=B[u]
    if x and(x<8)!=w and x&7!=6:m.append((f,u,o))
  else:
   for d in((),(),KN,DG,ST,QA,KI)[t]:
    u=f+d
    while not u&136:
     o=B[u]
     if o:
      if(o<8)!=w and o&7!=6:m.append((f,u,0))
      break
     if c==0:m.append((f,u,0))
     if t<3 or t>5:break
     u+=d
 return m
def make(m):
 f,t,p=m;v=B[f];B[f]=0;B[t]=v
 if p:B[t]=p if v<8 else p+8
 S[0]=1-S[0]
def legal(c=0):
 r=[];w=S[0]
 for m in gen(c):
  X=B[:],S[0];make(m)
  if not atk(B.index(6 if w else 14),not w):r.append(m)
  B[:],S[0]=X
 return r
def E():
 s=0
 for q in range(128):
  if q&136:continue
  p=B[q]
  if p:
   t=p&7;f=q&7;r=q>>4
   v=V[t]+(0,0,10,5,3,1,0)[t]*(min(f,7-f)+min(r,7-r))
   s+=v if p<8 else-v
 return(s if S[0]else-s)+12
def order(ms):
 def sc(m):
  f,t,p=m;c=B[t]
  return(10000+10*V[c&7]-V[B[f]&7]if c else 0)+(9000+10*V[p]if p else 0)
 return sorted(ms,key=sc,reverse=True)
def C(m,F,d,a,b,pl):
 X=B[:],S[0];make(m)
 try:t=F(d,-b,-a,pl+1)
 except TO:B[:],S[0]=X;raise
 B[:],S[0]=X
 return-t
def A(d,a,b,pl):
 N[0]+=1
 if N[0]>BUD:raise TO
 if pl>60:return E()
 w=S[0];ic=atk(B.index(6 if w else 14),not w)
 if d>0 or ic:
  k=bytes(B),S[0];e=TT.get(k)
  if e and e[0]>=d and((e[2]==1 and e[1]>=b)or(e[2]==2 and e[1]<=a)):return e[1]
  ms=legal(0)
  if not ms:return-MATE if ic else 0
  bs=-MATE-1
  for m in order(ms):
   s=C(m,A,d-1,a,b,pl)
   if s>bs:bs=s
   if s>a:a=s
   if a>=b:break
  TT[k]=d,bs,1 if bs>=b else 2
  return bs
 st=E()
 if st>=b:return st
 if st>a:a=st
 for m in order(legal(1)):
  s=C(m,A,0,a,b,pl)
  if s>=b:return s
  if s>a:a=s
 return a
def choose(f,lg,hs):
 try:
  setup(f)
  ms=[m for m in legal(0)if uci(m)in lg]
  if not ms:return lg[0]
  if len(ms)==1:return uci(ms[0])
  TT.clear();N[0]=0
  bs=[0]*len(ms);best=uci(ms[0]);d=1
  try:
   while 1:
    a=-MATE-1
    for i,m in enumerate(ms):
     s=C(m,A,d-1,a,MATE+1,0)
     bs[i]=s
     if s>a:a=s;best=uci(m)
    ms=sorted(ms,key=lambda m:-bs[ms.index(m)])
    if a>90000:break
    d+=1
  except TO:pass
  return best
 except Exception:return lg[0]
def post(p,b):
 r=Request(U+p,data=json.dumps(b).encode(),headers={"content-type":"application/json"})
 with urlopen(r)as x:return json.load(x)
if U:
 while 1:
  g=post("/game",{})
  if g["status"]=="done":break
  while g["status"]=="your_move":
   g=post("/move",{"game":g["game"],"move":choose(g["fen"],g["legal_moves"],g["moves"])})

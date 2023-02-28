import sys,os


badsigs = []
for fil in os.listdir("BadSignals"):
  if(not fil.startswith("bad")):continue
  
  inF = open(os.path.join("BadSignals",fil),"r")
  for lin in inF.readlines():
    xx,aa = lin.split(",")[0], lin.split(",")[1][:-1]
    badsigs.append((xx,aa))

print(len(badsigs))
badsigs = list(set(badsigs))
print(len(badsigs))
oF = open("BadSignals/allbad.txt","w")
for (xx,aa) in badsigs:
  oF.write("{},{}\n".format(xx,aa))

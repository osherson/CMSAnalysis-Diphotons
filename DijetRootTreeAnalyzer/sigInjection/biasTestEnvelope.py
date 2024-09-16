import os
import sys
import time
from collections import OrderedDict

xmass = sys.argv[1]
cdict = {}

#wd = "tenpct_loose"
wd = "Unblind/full_envelope"

#known_xs = [300, 400, 500, 600, 750, 1000, 1500, 2000, 3000]
known_xs = [310, 400, 500, 600, 750, 1000, 1500, 2000, 2990]
known_alphas = [0.005, 0.01, 0.015, 0.02, 0.025]

card_dir = "../DoEnvelopeFits/AllAlphaCards/{}".format(wd)
print(card_dir)
for ff in os.listdir(card_dir):
  if(ff.endswith(".txt")):
    cps = ff.split("_")

    for c in cps:
      if c.startswith("X"):
        mm = c
        break
    #mm = cps[0]
    #mm should be X400A2 (or similar)

    if(mm.endswith(".txt")):
      mm = mm[0:mm.rfind(".")]

    if("X{}".format(xmass) not in mm) : continue
    xm = int(mm[1 : mm.find("A")])
    pm = float(mm[mm.find("A")+1 : ].replace("p","."))
    alpha = round(pm/xm,3)
    if(alpha not in known_alphas): continue
    cdict[alpha]=ff

ocdict = OrderedDict(sorted(cdict.items()))
print(ocdict)

for alpha, ff in ocdict.items():
    #if(alpha != 0.005): continue
    if(alpha != float(sys.argv[3])): continue
    mycommand= "python BiasTest.py {}/{} {}".format(card_dir,ff,sys.argv[2])
    print(mycommand)
    os.system(mycommand)

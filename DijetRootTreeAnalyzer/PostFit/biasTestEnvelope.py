import os
import sys
import time
from collections import OrderedDict

xmass = sys.argv[1]

cdict = {}

for ff in os.listdir("./envelopeCards/OneBigBin"):
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

    #if(an != "alpha3" or "X600" not in mm): continue
    if("X{}".format(xmass) not in mm) : continue
    xm = int(mm[1 : mm.find("A")])
    pm = float(mm[mm.find("A")+1 : ].replace("p","."))
    cdict[pm/xm]=ff

ocdict = OrderedDict(sorted(cdict.items()))
print(ocdict)

for alpha, ff in ocdict.items():
    #if(alpha != 0.005): continue
    mycommand= "python BiasTest.py envelopeCards/OneBigBin/{} ".format(ff)
    print(mycommand)
    os.system(mycommand)

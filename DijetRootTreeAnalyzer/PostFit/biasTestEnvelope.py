import os
import sys
import time
from collections import OrderedDict

xmass = sys.argv[1]

cdict = {}

for ff in os.listdir("./envelopeCards/loose2"):
  if(ff.endswith(".txt")):
    cps = ff.split("_")
    mm = cps[0]

    #if(an != "alpha3" or "X600" not in mm): continue
    if("X{}".format(xmass) not in mm) : continue
    xm = int(mm[1 : mm.find("A")])
    pm = float(mm[mm.find("A")+1 : ].replace("p","."))
    cdict[pm/xm]=ff

ocdict = OrderedDict(sorted(cdict.items()))
print(ocdict)

for alpha, ff in ocdict.items():
    mycommand= "python BiasTest.py envelopeCards/loose2/{} ".format(ff)
    print(mycommand)
    os.system(mycommand)

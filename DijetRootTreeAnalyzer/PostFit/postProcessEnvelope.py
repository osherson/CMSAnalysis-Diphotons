import os
import sys
import time


for ff in os.listdir("./envelopeCards"):
  if(ff.endswith(".txt")):
    cps = ff.split("_")
    an = cps[2]
    mm = cps[3]
    mm = mm[ :mm.find(".")]

    if(an != "alpha1" or "X600" not in mm): continue

    mycommand= "python PlotPostEnvelope.py envelopeCards/{} diphoton_envelope_{}".format(ff, an)
    print(mycommand)
    #time.sleep(3)
    os.system(mycommand)
    exit()

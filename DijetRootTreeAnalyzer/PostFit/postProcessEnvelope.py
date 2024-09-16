import os
import sys
import time


for ff in os.listdir("./envelopeCards/fb_1"):
  if(ff.endswith(".txt")):
    cps = ff.split("_")
    if("All" not in ff):
      mm = cps[2]
      an = cps[3]
      an = an[ :an.find(".")]
    else:
      mm = cps[0]
      an = "All"

    #if(an != "alpha3" or "X600" not in mm): continue
    if("X400" not in mm) : continue

    mycommand= "python PlotPostEnvelope.py envelopeCards/fb_1/{} diphoton_envelope_{}".format(ff, an)
    print(mycommand)
    exit()
    #time.sleep(3)
    os.system(mycommand)

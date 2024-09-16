import os
import sys
import time

xmass = sys.argv[1]

for ff in os.listdir("./combineCards/"):
  if(ff.endswith(".txt") and "X{}A".format(xmass) in ff):
    if("X400A4" not in ff ): continue
    #if("alpha4" not in ff ): continue

    cps = ff.split("_")
    an = cps[1]
    mm = cps[2]
    fit = cps[3]
    fit = fit[ :fit.find(".")]

    #if os.path.exists("combineOutput/{}_{}_{}".format(an,mm,fit)):
    #  print("Directory exists, signal already processed. Moving on.")
    #  continue

    print("python PlotPostFits.py combineCards/{} diphoton_{}".format(ff, fit))
    #time.sleep(3)
    os.system("python PlotPostFits.py combineCards/{} diphoton_{}".format(ff, fit))

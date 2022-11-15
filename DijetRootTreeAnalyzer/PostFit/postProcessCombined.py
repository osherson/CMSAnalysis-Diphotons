import os
import sys
import time

xmass = sys.argv[1]

for ff in os.listdir("./combineCardsFull/fb_1"):
  if(ff.endswith(".txt") and "X{}A".format(xmass) in ff):
    #if("X600A5p4" not in ff ): continue
    #if("alpha4" not in ff ): continue

    cps = ff.split("_")
    mm = cps[1]
    fit = cps[2]
    fit = fit[ :fit.find(".")]

    #if os.path.exists("combineOutput/{}_{}_{}".format(an,mm,fit)):
    #  print("Directory exists, signal already processed. Moving on.")
    #  continue

    print("python PlotPostCombined.py combineCardsFull/fb_1/{} diphoton_{}".format(ff, fit))
    exit()
    os.system("python PlotPostCombined.py combineCardsFull/fb_1/{} diphoton_{}".format(ff, fit))

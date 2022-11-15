import os
import sys

print("Removing previous plots")
os.system("rm -rf fitPlots/*")

funcs = ["dijet","atlas","moddijet","myexp","dipho"]
#funcs = ["dijet"]

for ff in funcs:
  os.system("mkdir fitPlots/{}".format(ff))

for abin in os.listdir("output"):
  if(abin.startswith("alpha")):
    adir = os.path.join("output",abin)
    anum = abin[len("alpha")+1 : ]
    for ff in funcs:
      for xa in os.listdir(adir):
        fitplot = "{}/{}/fit_mjj_Full_diphoton_{}_{}_{}.png".format(adir, xa, xa, ff, anum)
        #print(fitplot)
        if(os.path.exists(fitplot)):
          if(int(anum) < 25):
            letter = chr(ord('`')+int(anum)+1)
          else:
            letter = chr(ord('`')+int(anum)-25+1)
          print("Copying {} to fitPlots/{}/fit_{}.png".format(fitplot,ff,letter))
          os.system("cp {} fitPlots/{}/fit_{}.png".format(fitplot,ff,letter))
          break

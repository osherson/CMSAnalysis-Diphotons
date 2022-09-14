import sys
import os
import time

ts = time.time()

card_dir = "./output/combineCards/"

def MakeFolder(N):
  if not os.path.exists(N):
    os.makedirs(N)

if("clean" in sys.argv):
  os.system("rm -r combineOutput/*")

def MakeLimit(anum, sxa):

      cc = "CARD_multi_{}_alpha{}.txt".format(sxa,anum)
      print("Starting Card {}".format(os.path.join(card_dir,cc)))
      MakeFolder("combineOutput/alpha{}".format(anum))
      os.system("combine {} -M AsymptoticLimits".format(os.path.join(card_dir,cc)))
      os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/alpha{}/higgsCombine_alpha{}_{}_AsymptoticLimits_mH120_root".format(anum,anum,sxa))
      return

tf = time.time()

signal = sys.argv[1]
doAlpha = sys.argv[2]

MakeLimit(doAlpha, signal)

print("Elapsed time: {} min".format((tf-ts)/60))

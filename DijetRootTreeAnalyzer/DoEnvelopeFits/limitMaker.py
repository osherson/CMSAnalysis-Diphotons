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

doAlpha = 1

#for doAlpha in [0,1,2,3]:
#for doAlpha in [4,5,6,7,8,9]:
for doAlpha in [0]:

  for cc in os.listdir(card_dir):
    if(cc.endswith(".txt")):
      sp = cc.split("_")
      sxa = sp[2]
      salpha = sp[-1][:sp[-1].find(".txt")]

      anum = int(salpha[5:])

      if(anum != doAlpha): continue

      MakeFolder("combineOutput/alpha{}".format(anum))

      os.system("combine {} -M AsymptoticLimits".format(os.path.join(card_dir,cc)))
      os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/alpha{}/higgsCombine_alpha{}_{}_AsymptoticLimits_mH120_root".format(anum,anum,sxa))

tf = time.time()

print("Elapsed time: {} min".format((tf-ts)/60))

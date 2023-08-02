import os
import sys

folder = "saveOutput/Unblind/full_ndof/combineCards/"

def getAlphaFrac(cname):
  print(cname)
  cc = card.split("_")
  sig = cc[-2]
  ainf = cc[-1]
  abin = ainf[ainf.find(".")-1 : ainf.find(".")]

  rfname = "../inputs/Shapes_fromInterpo/alphaBinning/{}/{}/alphaFraction_alpha{}_{}.txt".format(abin,sig,abin,sig)
  with open(rfname, "r") as rfil:
    frac = float(rfil.readline().strip("\n"))

  rfname = "../inputs/Shapes_fromInterpo/alphaBinning/{}/{}/alphaFraction_alpha{}_{}_su.txt".format(abin,sig,abin,sig)
  with open(rfname, "r") as rfil:
    frac_su = float(rfil.readline().strip("\n"))
  print(frac, frac_su)
  if(frac < 0 or frac_su < 0): return True
  else: return False

bcount = 0
bfrac = 0
for card in os.listdir(folder):
  if(not card.endswith(".txt")): continue


  for line in open("{}/{}".format(folder,card),"r"):
    if("rate" in line):
      rrs = line.split("\t")
      sigrate = float(rrs[1])
      if(sigrate < 0):
        print(card)
        bcount += 1
        if(getAlphaFrac(card)): bfrac += 1
      break

print("Bad Files: {}".format(bcount))
print("Bad Fracs: {}".format(bfrac))



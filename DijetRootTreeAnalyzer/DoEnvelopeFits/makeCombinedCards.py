import os
import sys

#wd = "fb_1_INT"
wd = "Interpo/int_0p01_fb"
card_dir = "saveOutput/{}/combineCards/".format(wd)

if(not os.path.exists("AllAlphaCards/{}".format(wd))):
  os.system("mkdir AllAlphaCards/{}".format(wd))

masses = []
for ff in os.listdir(card_dir):
  if(ff.startswith("dipho_combine") and ff.endswith(".txt")):
    for vv in ff.split("_"):
      if(vv.startswith("X")):
        masses.append(vv)

masses = list(set(masses))
ct = 0
for mass in masses:
  #if(ct % 100 == 0): print("{} / {} completed".format(ct, len(masses)))
  print("combineCards.py {}/*{}_*.txt > AllAlphaCards/{}/dipho_combine_multipdf_lumi-13.700_RunII_{}_Allalpha.txt".format(card_dir, mass, wd, mass))
  os.system("combineCards.py {}/*{}_*.txt > AllAlphaCards/{}/dipho_combine_multipdf_lumi-13.700_RunII_{}_Allalpha.txt".format(card_dir, mass, wd, mass))
  ct += 1

print("Running sed")
print("sed -i \"s/saveOutput\/{}\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/{}/*.txt".format(wd.replace("/","\\/"),wd))
os.system("sed -i \"s/saveOutput\/{}\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/{}/*.txt".format(wd.replace("/","\\/"),wd))



import os
import sys

#wd = "Interpo/int_1_fb_fixalpha"
#wd = "ThreeBins/tenpct_loose"
#wd = "Unblind/full_envelope"
wd = "Unblind/full_envelope_badsystematics"
card_dir = "saveOutput/{}/combineCards/".format(wd)

if(not os.path.exists("AllAlphaCards/{}".format(wd))):
  os.system("mkdir -p AllAlphaCards/{}".format(wd))

masses = []
for ff in os.listdir(card_dir):
#for ff in os.listdir("./output/combineCards/"):
  if(ff.startswith("dipho_combine") and ff.endswith(".txt")):
    for vv in ff.split("_"):
      if(vv.startswith("X")):
        masses.append(vv)

masses = list(set(masses))
ct = 0
for mass in masses:
  #if(ct % 100 == 0): print("{} / {} completed".format(ct, len(masses)))
  print("combineCards.py {}/*{}_*.txt > AllAlphaCards/{}/dipho_combine_multipdf_lumi-137.00_RunII_{}_Allalpha.txt".format(card_dir, mass, wd, mass))
  os.system("combineCards.py {}/*{}_*.txt > AllAlphaCards/{}/dipho_combine_multipdf_lumi-137.00_RunII_{}_Allalpha.txt".format(card_dir, mass, wd, mass))
  ct += 1

print("Running sed")
print("sed -i \"s/saveOutput\/{}\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/{}/*.txt".format(wd.replace("/","\\/"),wd))
os.system("sed -i \"s/saveOutput\/{}\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/{}/*.txt".format(wd.replace("/","\\/"),wd))



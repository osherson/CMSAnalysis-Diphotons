import os
import sys

card_dir = "saveOutput/loose2/combineCards/"

masses = []
for ff in os.listdir(card_dir):
  if(ff.startswith("CARD") and ff.endswith(".txt")):
    mass = ff.split("_")[2]
    masses.append(mass)

masses = list(set(masses))
ct = 0
for mass in masses:
  if(ct % 100 == 0): print("{} / {} completed".format(ct, len(masses)))
  os.system("combineCards.py {}/*{}*.txt > AllAlphaCards/{}_alphaAll.txt".format(card_dir, mass, mass))
  ct += 1
#os.system("sed -i \"s/output\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/*.txt")

#scom = "sed -i \"s/output\/combineCards\/\/cms/\/cms/g\" AllAlphaCards/*.txt"
#print(scom)
#os.system(scom)

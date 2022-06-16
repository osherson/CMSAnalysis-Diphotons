import os 
import sys

import TreemakerGun

gg = sys.argv[1]
if(gg=="ParticleGun"):
  RunList = [
            #"aGun_flat2",
            "aGun_flat3",
            ]

if(gg=="GJets"):
  RunList = [
            "HT100To200",
            ]

for run in RunList:
  if(gg=="ParticleGun"):
    TreemakerGun.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/".format(gg,run), run)
  elif(gg=="GJets"):
    TreemakerGun.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/2016/images/{}/".format(gg,run), run)

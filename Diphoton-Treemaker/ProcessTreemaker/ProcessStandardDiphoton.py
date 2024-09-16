import os 
import sys

sys.path.append("../")
import Treemaker_GJets

dname="0p014"
RunList = [
          "M-500",
          #"M-750",
          ]


for run in RunList:
  Treemaker_GJets.Treemaker("/cms/sclark-2/RUCLU_Outputs/Diphoton/{}/{}/".format(dname,run), run, True, "2016")

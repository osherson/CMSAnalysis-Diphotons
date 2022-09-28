import os 
import sys

sys.path.append("../")
import Treemaker_GJets
#import Treemaker_debug

year = sys.argv[1]

if("18" in year):
  dname="QCD"
  RunList = [
            #"HT50to100",
            #"HT100to200",
            #"HT200to300",
            #"HT300to500",
            "HT500to700",
            #"HT700to1000",
            #"HT1000to1500",
            #"HT1500to2000",
            #"HT2000toInf",
            ]

for run in RunList:
  Treemaker_GJets.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/{}/".format(dname,year,run), run, True, year)
  #Treemaker_debug.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/{}/".format(dname,year,run), run, True, year)

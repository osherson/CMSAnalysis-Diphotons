import os 
import sys

sys.path.append("../")
import Treemaker_GJets

year = sys.argv[1]

if("16" in year):
  dname="GJets"
  RunList = [
            "HT40To100",
            "HT100To200",
            "HT200To400",
            "HT400To600",
            "HT600ToInf",
            ]

if("17" in year):
  dname="GJets"
  RunList = [
            #"HT40To100",
            #"HT100To200",
            "HT200To400",
            #"HT400To600",
            #"HT600ToInf",
            ]

if("18" in year):
  dname="GJets"
  RunList = [
            #"HT40To100",
            #"HT100To200",
            #"HT200To400",
            "HT400To600",
            "HT600ToInf",
            ]

for run in RunList:
  Treemaker_GJets.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/{}/".format(dname,year,run), run, True, year)

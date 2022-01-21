import os 
import sys

sys.path.append("../")
import Treemaker

year = sys.argv[1]

if("16" in year):
  dname="DoubleEG"
  RunList = [
            "Run_B_ver2",
            "Run_C",
            "Run_D",
            "Run_E",
            "Run_F",
            "Run_F_HIPM",
            "Run_G",
            "Run_H",
            ]

elif("17" in year):
  dname="DoubleEG"
  RunList = [
            "Run_B",
            "Run_C",
            "Run_D",
            "Run_E",
            "Run_F",
            ]

elif("18" in year):
  dname="EGamma"
  RunList = [
            "Run_A",
            "Run_B",
            "Run_C",
            "Run_D",
            ]

for run in RunList:
  Treemaker.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/{}/".format(dname,year,run), run, True, year)

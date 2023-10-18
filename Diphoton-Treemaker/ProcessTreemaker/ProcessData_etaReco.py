import os 
import sys

sys.path.append("../")
import Treemaker_etaReco
import applyJson

year = sys.argv[1]

if("16" in year):
  dname="DoubleEG"
  RunList = [
            "Run_B_ver1",
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
            #"Run_A",
            #"Run_B",
            #"Run_C",
            "Run_D",
            ]

for run in RunList:
  Treemaker_etaReco.Treemaker("/cms/sclark-2/RUCLU_Outputs/{}/{}/{}/".format(dname,year,run), run, True, year)
  os.remove("./{}_{}.root".format(run, year))

  #applyJson.ApplyJson("/cms/sclark-2/DiPhotonsTrees/etaReco/{}_{}.root".format(run,year),["pico_skim","pico_full"])
  #applyJson.ApplyJson("/cms/sclark-2/DiPhotonsTrees/etaReco/{}_{}_p1.root".format(run,year),["pico_skim","pico_full"])
  applyJson.ApplyJson("/cms/sclark-2/DiPhotonsTrees/etaReco/{}_{}_p2.root".format(run,year),["pico_skim","pico_full"])
  #applyJson.ApplyJson("/cms/sclark-2/DiPhotonsTrees/etaReco/{}_{}_p3.root".format(run,year),["pico_skim","pico_full"])

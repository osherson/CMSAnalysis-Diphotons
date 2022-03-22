import ROOT
import numpy
import os
import math
import sys
import pandas
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

#year = '2018'

year = sys.argv[1]

### PICOTREE DIRECTORIES ###
pico_dir = "/cms/xaastorage-2/DiPhotonsTrees/"
dists = {}
xmasses = []
phimasses = []

outFileName = "CutInfoFiles/cutInfo_{}cutInfo.csv".format(year)

for path, subdirs, files in os.walk(pico_dir):
  for name in files:
    File = os.path.join(path, name)
    if name[0]=="X" and year in name:
      xamass = name[:name.find("_")]
      xmass = int(xamass[1 : xamass.find("A")])
      phimass = float(xamass[xamass.find("A")+1 :].replace("p",".") )
  
      #if (xmass == 200 and File.endswith(".root") and amass/xmass < alpha_high and "v_" not in name):
      if (File.endswith(".root") and year in name and "v_" not in File):
        if(os.path.getsize(File) > 100):
            dists[xamass]=File
            xmasses.append(xmass)
            phimasses.append(phimass)

eventsCount = []
ct = 0

eventsFile = "../../../Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
edf = pandas.read_csv(eventsFile)

for xphi,F in dists.items():
  #if ct > 2: break

  this_xm = int(xphi[1:xphi.find("A")])
  this_phim = float(xphi[xphi.find("A")+1 :].replace("p","."))
  if this_phim.is_integer(): this_phim = int(this_phim)
  myalpha = float(this_phim) / float(this_xm)

  nevents_gen = edf.loc[(edf["X Mass"]==this_xm) & (edf["Phi Mass"] == this_phim)]["N Events"].tolist()

  Chain=ROOT.TChain("pico_nom")
  Chain.Add(F)

  rdf = ROOT.RDataFrame.RDataFrame(Chain)
  #oEvents = int(rdf.Count().GetValue())
  oEvents = nevents_gen[0]
  cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
  rdf = rdf.Filter(cutString, "Analysis Cuts")
  hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
  alphastd = hist.GetStdDev()
  rdf = rdf.Filter("alpha > {} && alpha < {}".format(myalpha - alphastd*3, myalpha + alphastd*3), "alpha Window")
  cEvents = int(rdf.Count().GetValue())
  rep = rdf.Report()
  rep.Print()

  eventsCount.append([this_xm, this_phim, oEvents, cEvents])

  print(xphi, this_xm, this_phim, oEvents, cEvents)

  ct += 1

df = pandas.DataFrame(eventsCount, columns=["xmass", "phimass", "oEvents", "cEvents"])
df["eff"] = df["cEvents"] / df["oEvents"]
print("Saving info in: {}".format(outFileName))
df.to_csv(outFileName)


import numpy as np
import os
import ROOT 
import pandas as pd

year = 2018

isigDirectory = "../DijetRootTreeAnalyzer/inputs/Interpolations/{}/".format(year)

mylist = []

ct = 0
for subdir, dirs, files in os.walk(isigDirectory):
  ct += 1
  #if ct > 10: break
  for dd in dirs:
    if(dd[0] != "X"): 
      print("Skipping {}".format(dd))
      continue
    thisxa = dd[ dd.rfind("/")+1 : ]
    if(len(thisxa) < 1): continue
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1 : ])
    fname = "{}/{}_nom.root".format(os.path.join(isigDirectory,dd),thisxa.replace("A","phi"))
    if(not os.path.exists(fname)): continue
    ff = ROOT.TFile(fname, "READ")

    xhist = ff.Get("{}_XM".format(thisxa.replace("A","phi")))

    try:
      xmean = xhist.GetMean()
      xrms = xhist.GetRMS()
      mylist.append( (this_x, this_phi/this_x, xmean, xrms) )
    except AttributeError:
      print("Problem with: {}".format(fname))

#gsigDirectory = "../DijetRootTreeAnalyzer/inputs/"
#for subdir, dirs, files in os.walk(gsigDirectory):
#  for dd in dirs:
#    if(dd[0] != "X"): continue
#    thisxa = dd
#    this_x = int(thisxa[1:thisxa.find("A")])
#    this_phi = float(thisxa[thisxa.find("A")+1 : ].replace("p","."))
#    if(this_phi / this_x > 0.03): continue
#    fname = "{}/Sig_nominal.root".format(os.path.join(gsigDirectory, dd))
#    if(not os.path.exists(fname)): continue
#    ff = ROOT.TFile(fname, "READ")
#
#    xhist = ff.Get("h_AveDijetMass_1GeV")
#
#    try:
#      xmean = xhist.GetMean()
#      xrms = xhist.GetRMS()
#      mylist.append( (this_x, this_phi/this_x, xmean, xrms) )
#    except AttributeError:
#      print("Problem with: {}".format(fname))

print("Got {} Good Files".format(len(mylist)))

df = pd.DataFrame(mylist, columns=["M_X","alpha","mean","rms"])
df.to_csv("means_rms_info.csv",index=False)

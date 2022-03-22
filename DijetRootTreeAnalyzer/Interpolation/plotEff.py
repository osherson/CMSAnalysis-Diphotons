#import ROOT
import numpy
import os
import math
import sys
import pandas
import matplotlib.pyplot as plt
sys.path.append("../.")

year = sys.argv[1] 

### Efficiency File ###
infoFile = "SignalEffCalc/CutInfoFiles/cutInfo_{}cutInfo.csv".format(year)
df = pandas.read_csv(infoFile,index_col=0)
dic = df.to_dict()

xmasses = sorted(set(df["xmass"].to_list()))
phimasses = sorted(set(df["phimass"].to_list()))
xmasses = [xx - 0.01 for xx in xmasses]
phimasses = [xx - 0.01 for xx in phimasses]
xmasses_b = numpy.array(xmasses, dtype='float64')
phimasses_b = numpy.array(phimasses, dtype='float64')

#myhist = ROOT.TH2F( "eff", "Signal Efficiency;DiClusterMass;Avg. Cluster Mass", len(xmasses_b)-1, xmasses_b, len(phimasses_b)-1, phimasses_b)

alphalim = 0.03
plotalpha = 0.02
plotalpha = float(sys.argv[2])

plotx = []
ploteff = []
for index, row in df.iterrows():
  if(row.phimass / row.xmass > alphalim): continue
  #myhist.Fill(row.xmass, row.phimass, row.eff)
  elif(row.phimass / row.xmass == plotalpha):
    plotx.append(row.xmass)
    ploteff.append(row.eff)

plt.figure()
plt.scatter(plotx, ploteff)
plt.title("{} Signal Efficiency for alpha = {}".format(year, plotalpha), fontsize=18)
plt.xlabel("Dicluster mass", fontsize=14)
plt.ylabel("Eff", fontsize=14)
plt.savefig("OutFiles/{}/eff_{}.png".format(year, plotalpha))
plt.show()

#c1 = ROOT.TCanvas()
#c1.cd()
#myhist.GetYaxis().SetRangeUser(1, max(xmasses)*alphalim)
#myhist.Draw("colz")


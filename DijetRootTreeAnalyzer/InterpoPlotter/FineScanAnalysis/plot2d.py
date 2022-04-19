import numpy as np
import os
import ROOT 

xs, als, mns, rms = np.loadtxt("means_rms_info.csv", delimiter=",", skiprows=1, unpack=True)

mylist = zip(xs,als,mns,rms)

xmasses = np.array( sorted(set([x for (x,a,m,r) in mylist])) )
alphas =  np.array( sorted(set([a for (x,a,m,r) in mylist])) )

xwidth = float(xmasses[1] - xmasses[0])
awidth = float(alphas[1] - alphas[0])
xbins = [x - xwidth/2. for x in xmasses]
abins = [a - awidth/2. for a in alphas]
xbins.append(xmasses[-1] + xwidth)
abins.append(alphas[-1] + awidth)

xbins = np.array(xbins)
abins = np.array(abins)

#print(xbins)
#print(abins)

mH = ROOT.TH2D("mean","(M_{X,Reco}-M_{X,True})/M_{X,True};M_{X};alpha", len(xbins)-1, xbins, len(abins)-1, abins)
rH = ROOT.TH2D("rms","RMS_{Reco}/M_{X,True};M_{X};alpha", len(xbins)-1, xbins, len(abins)-1, abins)

for (x,a,m,r) in mylist:
  #mH.Fill(x,a,m/x)
  mH.Fill(x,a,np.abs(m-x)/x)
  rH.Fill(x,a,r/x)

for hh in [mH, rH]:
  hh.SetStats(0)
  hh.GetXaxis().SetRangeUser(0, 2000)
  hh.GetYaxis().SetRangeUser(0.005, 0.03)

  hh.SetTitleSize(0.06)
  hh.GetXaxis().SetTitleSize(0.04)
  hh.GetXaxis().SetTitleOffset(1.0)
  hh.GetXaxis().SetLabelSize(0.035)
  hh.GetYaxis().SetTitleSize(0.04)
  hh.GetYaxis().SetTitleOffset(1.1)
  hh.GetYaxis().SetLabelSize(0.035)
  hh.GetZaxis().SetLabelSize(0.035)

c1 = ROOT.TCanvas("c1","c1",650,500)
c1.cd()
mH.Draw("colz")
c1.Print("Plots/means.png")

c2 = ROOT.TCanvas("c2","c2",650,500)
c2.cd()
rH.Draw("colz")
c2.Print("Plots/rms.png")

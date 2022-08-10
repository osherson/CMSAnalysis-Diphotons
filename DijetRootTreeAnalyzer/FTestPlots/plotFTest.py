from ROOT import *
import numpy as np

infile = open("FTestResults.txt")

AlphaBins = [
             0.0,
             0.00428571428571,
             0.00467532467532,
             0.00506493506494,
             0.005689655172413793,
             0.006379310344827587,
             0.00706896551724138,
             0.007758620689655172,
             0.008448275862068966,
             0.00935064935065,
             0.00974025974026,
             0.0101298701299,
             0.01120689655172414,
             0.011896551724137932,
             0.0128571428571,
             0.0139285714286,
             0.3
             ]

results = []
for line in infile.readlines():
  rl = line.split(",")
  a,f,c,n,p = int(rl[0]),rl[1],float(rl[2]),int(rl[3]),float(rl[4][:-1])
  results.append((a,f,c,n,p))

functions = set(ff for (a,ff,c,b,p) in results) 

for plotfunc in functions:
  #if(plotfunc != "dijet"): continue

  hist3 = TH1F("c21_3","%s Function;#alpha;c_{21}"%plotfunc.capitalize(),16,0,16)
  hist4 = TH1F("c21_4","%s Function;#alpha;c_{21}"%plotfunc.capitalize(),16,0,16)
  hist5 = TH1F("c21_5","%s Function;#alpha;c_{21}"%plotfunc.capitalize(),16,0,16)
  hist6 = TH1F("c21_6","%s Function;#alpha;c_{21}"%plotfunc.capitalize(),16,0,16)

  hist_p = TH1F("c21_p","%s Function;#alpha;c_{21}"%plotfunc.capitalize(),16,0,16)

  for (anum, func, c21, nb, c21_pr) in results:
    if(func != plotfunc): continue

    if(nb==3):
      hist3.SetBinContent(anum+1,c21)
    if(nb==4):
      hist4.SetBinContent(anum+1,c21)
    if(nb==5):
      hist5.SetBinContent(anum+1,c21)
    if(nb==6):
      hist6.SetBinContent(anum+1,c21)

    hist_p.SetBinContent(anum+1,c21_pr)
  
  for hh in [hist3, hist4, hist5, hist6, hist_p]:
    hh.SetBarWidth(1.);
    hh.SetBarOffset(0.);
    hh.SetStats(0);
    hh.GetXaxis().SetTitleSize(0.05)
    hh.GetYaxis().SetTitleSize(0.05)
    hh.GetXaxis().SetTitleOffset(0.75)
    hh.GetYaxis().SetTitleOffset(0.75)
    hh.GetXaxis().CenterLabels(kTRUE)
    hh.SetTitleSize(0.06)
    hh.GetYaxis().SetRangeUser(0.001,1.35)

    for ii in range(hh.GetNbinsX()+1):
      hh.GetXaxis().SetBinLabel(ii, "{:.4f}".format(AlphaBins[ii]))

  hist_p.SetMarkerColor(kBlack)
  hist_p.SetMarkerStyle(34)
  hist_p.SetMarkerSize(1.5)
  hist_p.SetFillColor(kBlack)

  hist3.SetFillColor(4);
  hist4.SetFillColor(6);
  hist5.SetFillColor(8);
  hist6.SetFillColor(2);

  leg = TLegend(0.7,0.7,0.89,0.89)
  leg.AddEntry(hist3, "3 Param Fit")
  leg.AddEntry(hist4, "4 Param Fit")
  leg.AddEntry(hist5, "5 Param Fit")
  leg.AddEntry(hist6, "6 Param Fit")
  leg.SetBorderSize(0)

  c1 = TCanvas("c","c",800,600)
  c1.cd()
  hist3.Draw("bar")
  hist4.Draw("barsame")
  hist5.Draw("barsame")
  hist6.Draw("barsame")
  #hist_p.Draw("P0same")
  leg.Draw("same")
  #c1.SetLogy()
  c1.Print("Plots/{}_c21.png".format(plotfunc))



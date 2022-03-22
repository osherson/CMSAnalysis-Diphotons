import ROOT
import numpy
import os
import math
import sys
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

year = sys.argv[1]

out_dir = "OutFiles/{}".format(year)

dists = {}
xmasses = []
phimasses = []
FileList = []

for path, subdirs, files in os.walk(out_dir):
  for name in files:
    if(name[0] != "X"): continue
    FileList.append( os.path.join(path, name) )

for name in FileList:
  if("known" in name): continue
  xamass = name[name.find("X"):name.find(".root")]
  xmass = xamass[1 : xamass.find("phi")]
  phimass = xamass[xamass.find("phi")+3 :].replace("p",".")
  if("{}/{}_known.root".format(out_dir, xamass) in FileList): 
    dists[xamass]=name
    xmasses.append(int(xmass))
    phimasses.append(float(phimass))

for xphi, fname in dists.items():
  xmass = int(xphi[1 : xphi.find("phi")])
  phimass = float(xphi[xphi.find("phi")+3 :].replace("p","."))
  if(phimass.is_integer()): phimass=int(phimass)
  outFileName = "OutFiles/{}/{}_compareplots.png".format(year, xphi)

  iFile = ROOT.TFile(fname, "read")
  ihist = iFile.Get("{}".format(xphi))
  kFile = ROOT.TFile(fname.replace(".root","_known.root"), "read")
  khist = kFile.Get("{}".format(xphi))

  ihist.Scale(1/ihist.Integral())
  khist.Scale(1/khist.Integral())

  maxy = max(ihist.GetMaximum(), khist.GetMaximum())*1.15

  c1 = ROOT.TCanvas()
  c1.cd()

  legend = ROOT.TLegend(0.70,0.6,0.90,0.87)

  ct = 0
  for hist in [khist, ihist]:
    if ct==0: known=True
    else: known=False

    hist.SetTitle("X {} #phi {} Generated vs. Interpolated Signal".format(xmass, phimass))
    hist.GetXaxis().SetRangeUser(xmass*0.75, xmass*1.25)
    hist.GetYaxis().SetRangeUser(0, maxy)
    hist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
    hist.GetYaxis().SetTitle("Entries")
    if known: 
      hist.SetLineColor(ROOT.kBlue)
      hist.SetFillColor(ROOT.kBlue)
      hist.SetFillStyle(3001)
    else: 
      hist.SetLineColor(ROOT.kRed)
      hist.SetFillColor(ROOT.kRed)
      hist.SetLineWidth(2)
      hist.SetFillStyle(0)
    hist.GetXaxis().SetLabelSize(0.145/4)
    hist.GetXaxis().SetTitleOffset(0.75)
    hist.GetYaxis().SetTitleSize(0.175/4)
    hist.GetYaxis().SetLabelSize(0.145/4)
    hist.GetYaxis().SetTitleOffset(1)
    hist.SetStats(0)

    hist.SetDirectory(ROOT.gROOT)

    if known: legend.AddEntry(hist, "Generated")
    else: legend.AddEntry(hist, "Interpolated")

    if(ct==0): hist.Draw("hist")
    else: hist.Draw("histsame")
    ct+=1

  lin = ROOT.TLine(xmass,0,xmass,maxy)
  lin.SetLineColor(ROOT.kBlack)
  lin.SetLineStyle(9)
  lin.SetLineWidth(1)
  lin.Draw("same")
  legend.SetBorderSize(0)
  legend.Draw("same")
  ROOT.gStyle.SetLegendTextSize(0.035)

  c1.Print(outFileName)
  print("Saving as {}".format(outFileName))

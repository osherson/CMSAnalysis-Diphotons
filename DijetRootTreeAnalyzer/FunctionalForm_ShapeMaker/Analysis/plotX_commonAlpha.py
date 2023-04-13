import ROOT
import numpy
import os
import math
import sys

ROOT.gROOT.SetBatch()

def MakeFolder(N):
    import os
    if not os.path.exists(N):
     os.makedirs(N)

def GetXPhiAlpha(ins):
  X = int(ins[ins.find("X")+1 : ins.find("A")])
  Phi = float(ins[ins.find("A")+1 : ].replace("p","."))
  Alpha = round(Phi/X,3)
  return X, Phi, Alpha

I_DIR = "../../inputs/Shapes_fromInterpo/unBinned"
G_DIR = "../../inputs/Shapes_fromGen/alphaBinning"

plot_alphas = [0.005, 0.006, 0.01, 0.011]

for plot_alpha in plot_alphas:
  int_files = []

  #for ii,alphaDir in enumerate([ialphaDir, galphaDir]):
  for sig in os.listdir(I_DIR):
    if(not sig.startswith("X")): continue
    xx,pp,aa = GetXPhiAlpha(sig)
    #if(xx < 297 or xx > 1600): continue
    if(xx % 50 != 0 ): continue
    if(aa == plot_alpha):
      xdir = os.path.join(I_DIR, sig)
      if(os.path.exists("{}/PLOTS.root".format(xdir))):
        int_files.append(["int", xx, pp, aa, "{}/PLOTS.root".format(xdir)])

  allFiles = int_files 

  histdic = {}
  hc = 0

  if(len(allFiles) == 0): 
    #print("No Files for alphaBin {} signal alpha {}".format(alphaBin, plot_alpha))
    continue

  maxes = []
  xmassmax = 0
  ii=0
  for src, xm, pm, alph, fil in allFiles:
    tf = ROOT.TFile(fil, "read")
    hist = tf.Get("h_AveDijetMass_1GeV")
    maxes.append(hist.GetMaximum())
    if(xm > xmassmax): xmassmax = xm
    ii += 1

  top = 0.11
  top = max(maxes)*1.15

  c1 = ROOT.TCanvas()
  c1.cd()
  for src, xm, pm, alph, fil in allFiles:
    tFile = ROOT.TFile(fil, "read")
    myhist = tFile.Get("h_AveDijetMass_1GeV")
    if(src=="int"):
      myhist.SetLineColor(ROOT.kBlue)
      myhist.SetFillColor(ROOT.kBlue)
    elif(src=="gen"):
      myhist.SetLineColor(ROOT.kRed)
      myhist.SetFillColor(ROOT.kRed)

    myhist.SetStats(0)
    #myhist.GetXaxis().SetRangeUser(0, 2200)
    myhist.GetXaxis().SetRangeUser(250, xmassmax*1.1)
    myhist.GetYaxis().SetRangeUser(0, top)
    myhist.SetTitle("Dicluster Mass, alpha = {}".format(plot_alpha))
    myhist.GetXaxis().SetTitle("Dicluster Mass")
    myhist.GetYaxis().SetTitle("Entries")
    myhist.SetFillStyle(3001)
    myhist.GetXaxis().SetTitleSize(0.175/4)
    myhist.GetXaxis().SetLabelSize(0.145/4)
    myhist.GetXaxis().SetTitleOffset(1)
    myhist.GetYaxis().SetTitleSize(0.175/4)
    myhist.GetYaxis().SetLabelSize(0.145/4)
    myhist.GetYaxis().SetTitleOffset(1)
    myhist.SetDirectory(ROOT.gROOT)

    latex = ROOT.TLatex()
    latex.SetNDC()
    latex.SetTextAngle(0)
    latex.SetTextColor(ROOT.kBlack)
    latex.SetTextAlign(31)
    latex.SetTextAlign(11)
    latex.SetTextFont(62)
    latex.SetTextSize(0.050)

    if(hc==0): myhist.Draw("hist")
    else: myhist.Draw("histsame")
    hc += 1

  c1.Print("Plots/unBinned/alpha{}.png".format(plot_alpha))



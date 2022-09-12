import ROOT
import numpy
import os
import math
import sys

#ROOT.gROOT.SetBatch()

def MakeFolder(N):
    import os
    if not os.path.exists(N):
     os.makedirs(N)

def GetXPhiAlpha(ins):
  X = int(ins[ins.find("X")+1 : ins.find("A")])
  Phi = float(ins[ins.find("A")+1 : ].replace("p","."))
  Alpha = round(Phi/X,3)
  return X, Phi, Alpha

I_DIR = "../inputs/Shapes_fromInterpo/alphaBinning"
G_DIR = "../inputs/Shapes_fromGen/alphaBinning"

GEN_ALPHAS = [0.005, 0.01, 0.015, 0.02, 0.025]

#for alphaBin in range(0,9+1):
for alphaBin in ["ALL"]:

  #if(alphaBin != 1): continue

  ialphaDir = "{}/{}".format(I_DIR,alphaBin)
  galphaDir = "{}/{}".format(G_DIR,alphaBin)
  int_files, gen_files = [],[]
  
  for plot_alpha in GEN_ALPHAS:

    for ii,alphaDir in enumerate([ialphaDir, galphaDir]):
      for si in os.listdir(alphaDir):
        xx,pp,aa = GetXPhiAlpha(si)
        if(xx < 297 or xx > 1600): continue
        if(aa == plot_alpha):
          xdir = os.path.join(alphaDir, si)
          if(alphaBin=="ALL"):
            if(os.path.exists("{}/PLOTS_0.root".format(xdir))):
              if(ii==0):int_files.append(["int", xx, pp, aa, "{}/PLOTS_0.root".format(xdir)])
              else:gen_files.append(["gen", xx, pp, aa, "{}/PLOTS_0.root".format(xdir)])
          else:
            if(os.path.exists("{}/PLOTS_{}.root".format(xdir, alphaBin))):
              if(ii==0):int_files.append(["int", xx, pp, aa, "{}/PLOTS_{}.root".format(xdir, alphaBin)])
              else:gen_files.append(["gen", xx, pp, aa, "{}/PLOTS_{}.root".format(xdir, alphaBin)])
  
    allFiles = int_files + gen_files

    histdic = {}
    hc = 0

    maxes = []
    for src, xm, pm, alph, fil in allFiles:
      if(src=="gen"):continue
      tf = ROOT.TFile(fil, "read")
      hist = tf.Get("h_AveDijetMass_1GeV")
      maxes.append(hist.GetMaximum())
  
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
      myhist.GetXaxis().SetRangeUser(0, 2200)
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


      if(hc==0): myhist.Draw("hist")
      else: myhist.Draw("histsame")
      hc += 1

    MakeFolder("Plots/alphaBin{}/".format(alphaBin))
    c1.Print("Plots/alphaBin{}/alpha{}.png".format(alphaBin,plot_alpha))



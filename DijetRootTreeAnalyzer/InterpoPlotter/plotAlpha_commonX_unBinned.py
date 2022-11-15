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

I_DIR = "../inputs/Shapes_fromInterpo/unBinned"
G_DIR = "../inputs/Shapes_fromGen/unBinned"

GEN_XS = [300,400,500,600,750,1000,1500,2000]

AlphaBins = [ 0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.01049, 0.01505, 0.03]

for plot_alpha in GEN_XS:
  int_files, gen_files = [],[]
  #if(plot_alpha != 1000): continue

  for ii,alphaDir in enumerate([I_DIR, G_DIR]):
    for si in os.listdir(alphaDir):
      xx,pp,aa = GetXPhiAlpha(si)
      if(xx < 297 or xx > 2000): continue
      if(aa > 0.026): continue
      if(aa not in [0.005,0.007,0.01]): continue
      if(xx == plot_alpha):
        xdir = os.path.join(alphaDir, si)
        if(os.path.exists("{}/Sig_nominal.root".format(xdir))):
          if(ii==0):int_files.append(["int", xx, pp, aa, "{}/Sig_nominal.root".format(xdir)])
          else:gen_files.append(["gen", xx, pp, aa, "{}/Sig_nominal.root".format(xdir)])

  allFiles = int_files + gen_files

  histdic = {}
  hc = 0

  if(len(int_files) == 0): 
    print("No Interpolated Files ")
    continue
  if(len(allFiles) == 0): 
    print("No Files ")
    continue

  maxes = []
  xmassmax = 0
  ii=0
  for src, xm, pm, alph, fil in allFiles:
    tf = ROOT.TFile(fil, "read")
    hist = tf.Get("h_alpha_fine")
    try:
      #hist = hist.Rebin(len(AlphaBins)-1,hist.GetName()+"_rebin",numpy.array(AlphaBins))
      #hist.Scale(1, "width")
      #hist.Scale(1/hist.Integral())
      maxes.append(hist.GetMaximum())
    except AttributeError: continue
    if(xm > xmassmax): xmassmax = xm
    ii += 1

  top = 0.11
  top = max(maxes)*1.15
  print(top)

  c1 = ROOT.TCanvas()
  c1.cd()
  for src, xm, pm, alph, fil in allFiles:
    tFile = ROOT.TFile(fil, "read")
    myhist = tFile.Get("h_alpha_fine")
    try:
      if(src=="int"):
        myhist.SetLineColor(ROOT.kBlue)
        myhist.SetFillColor(ROOT.kBlue)
      elif(src=="gen"):
        myhist.SetLineColor(ROOT.kRed)
        myhist.SetFillColor(ROOT.kRed)
    except AttributeError: 
      print("Problem with {}".format(fil))
      continue

    #myhist = myhist.Rebin(len(AlphaBins)-1,myhist.GetName()+"_rebin",numpy.array(AlphaBins))
    #myhist.Scale(1, "width")
    #myhist.Scale(1/myhist.Integral())
    print(myhist.Integral())
    myhist.SetStats(0)
    #myhist.GetXaxis().SetRangeUser(0, 2200)
    myhist.GetXaxis().SetRangeUser(0,0.035)
    myhist.GetYaxis().SetRangeUser(0, top)
    myhist.Smooth() #
    myhist.SetTitle("#alpha Shape, X = {} GeV".format(plot_alpha))
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
    latex.DrawLatex(0.55,0.85,"No #alpha slicing")

    if(hc==0): myhist.Draw("hist")
    else: myhist.Draw("histsame")
    hc += 1

  MakeFolder("Plots/unBinned/")
  c1.Print("Plots/unBinned/X{}.png".format(plot_alpha))



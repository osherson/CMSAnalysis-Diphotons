import numpy as np
import ROOT
from ROOT import *
from array import array
import os,sys

#gROOT.SetBatch()

g_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned/"

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

alphamin, alphamax = 0.005, 0.03
nalphas = int((alphamax - alphamin)//0.001 + 2)
alphalist = np.linspace(alphamin, alphamax, nalphas)

xmin, xmax = 300, 3010
nxs = int((xmax-xmin)//10 + 1)
xlist = np.linspace(xmin, xmax, nxs)

for want_alpha in gen_phis:
  effs = []
  aranges = {}

  try:
    for gf in os.listdir(os.path.join(g_dir)):
      xmass = int(gf[1 : gf.find("A")])
      amass = float(gf[gf.find("A")+1 :].replace("p","."))
      phi = amass / xmass
      if(phi != want_alpha): continue
      eff_file = open("{}/{}/{}.txt".format(g_dir, gf, gf))
      eff = float(eff_file.readline().rstrip())
      eff_file.close()
      effs.append((xmass, phi, eff))
  except FileNotFoundError:
    continue

  pxs = array('d')
  peffs = array('d')
  n = 0

  effs.sort(key=lambda row: (row[0]), reverse=False)

  for (mm, aa, ee) in effs:
      print(mm, aa, ee)
      if(mm in pxs): print("woah")
      pxs.append(mm)
      peffs.append(ee)
      n += 1
  
  c1 = TCanvas()
  c1.cd()
  gr = TGraph(len(pxs), pxs, peffs)
  gr.SetLineColor( 2 )
  gr.SetLineWidth( 4 )
  gr.SetMarkerColor( 4 )
  gr.SetMarkerStyle( 21 )
  gr.SetTitle( "Gen #alpha =%s"%(want_alpha))
  gr.GetXaxis().SetTitle( "DiCluster Mass (GeV)" )
  gr.GetYaxis().SetTitle( 'Efficiency' )
  gr.Draw( 'AP' )

  xevals = [gr.Eval(xm) for xm in xlist]
  eff_file = open("EfficiencyFiles/unBinned/alpha{}.csv".format(want_alpha),"w")
  for xm, ef in zip(xlist, xevals):
    eff_file.write("{},{}\n".format(int(xm),ef))
  eff_file.close()

  s = TSpline3("s",gr);
  s.Draw("same")
#  newd = "EffPlots/alpha{}".format(want_alpha)
#  if(not os.path.exists(newd)):
#    os.system("mkdir {}".format(newd))
  c1.Print("EffPlots/unBinned/alpha{}.png".format(want_alpha))








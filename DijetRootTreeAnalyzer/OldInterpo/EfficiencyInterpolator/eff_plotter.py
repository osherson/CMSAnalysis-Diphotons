import numpy as np
import ROOT
from ROOT import *
from array import array
import os,sys

gROOT.SetBatch()

g_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"

alphaBins = range(0,13+1)

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

#alphamin, alphamax = 0.005, 0.03
#nalphas = 25+1
#nalphas = 5+1
#lphalist = np.linspace(alphamin, alphamax, nalphas)

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

  for abin in alphaBins:
    #if(abin != 3): continue
    abin=str(abin)
    try:
      for gf in os.listdir(os.path.join(g_dir, abin)):
        xmass = int(gf[1 : gf.find("A")])
        amass = float(gf[gf.find("A")+1 :].replace("p","."))
        phi = amass / xmass
        if(phi != want_alpha): continue
        eff_file = open("{}/{}/{}/{}.txt".format(g_dir, abin, gf, gf))
        eff = float(eff_file.readline().rstrip())
        range_file = open("{}/{}/{}/arange.txt".format(g_dir, abin, gf))
        rr = range_file.readline().rstrip()
        la = float(rr.split(",")[0])
        ha = float(rr.split(",")[-1])
        eff_file.close()
        range_file.close()
        effs.append((abin, xmass, eff))
        if(abin not in aranges.keys()):
          aranges[abin] = (la, ha)
    except FileNotFoundError:
      continue

  abins = [a for (a,m,e) in effs]
  abins = list(set(abins))
  print(abins)


  for ab in abins:
    pxs = array('d')
    peffs = array('d')
    n = 0

    (la, ha) = aranges[ab]

    s_xeff = []

    for (aa, mm, ee) in effs:
      if(aa == ab):
        if(mm) in pxs: print("Woah")
        s_xeff.append((mm,ee))

    s_xeff.sort(key=lambda row: (row[0]), reverse=False)

    for (mm, ee) in s_xeff:
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
    gr.SetTitle( "Gen #alpha =%s, Alpha Bin %s, %s < #alpha < %s"%(want_alpha, ab, la, ha))
    gr.GetXaxis().SetTitle( "DiCluster Mass (GeV)" )
    gr.GetYaxis().SetTitle( 'Efficiency' )
    gr.Draw( 'AP' )

    xevals = [gr.Eval(xm) for xm in xlist]
    eff_file = open("EfficiencyFiles/alpha{}_alphaBin{}.csv".format(want_alpha, ab),"w")
    for xm, ef in zip(xlist, xevals):
      eff_file.write("{},{}\n".format(int(xm),ef))
    eff_file.close()

    s = TSpline3("s",gr);
    s.Draw("same")
#    newd = "EffPlots/alpha{}".format(want_alpha)
#    if(not os.path.exists(newd)):
#      os.system("mkdir {}".format(newd))
    c1.Print("EffPlots/alpha{}_bin{}.png".format(want_alpha, ab))








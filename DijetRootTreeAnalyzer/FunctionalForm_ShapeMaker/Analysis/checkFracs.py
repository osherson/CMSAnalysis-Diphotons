import numpy
import sys,os
from array import array
import ROOT

unb_dir = "../../inputs/Shapes_fromInterpo/unBinned/"
ab_dir = "../../inputs/Shapes_fromInterpo/alphaBinning/"
sigs = [xa for xa in os.listdir(unb_dir)]

print(len(sigs))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

quicka = 0.005
sumdic = {}
for sig in sigs:
  x,p,a = getXPhiAlpha(sig)
  if(a != quicka): continue
  sumdic[sig] = 0

alphamin, alphamax = 0.005, 0.03
nalphas = 25+1
fine_alphas = numpy.linspace(alphamin, alphamax, nalphas)

for abin in os.listdir(ab_dir):
  apath = os.path.join(ab_dir, abin)
  for thissig in os.listdir(apath):
    thisx,thisphi,thisalpha = getXPhiAlpha(thissig)
    if(thisalpha != quicka): continue
    fracfile = open("{}/{}/alphaFraction_alpha{}_{}.txt".format(apath,thissig,abin,thissig),"r")
    frac = float(fracfile.readline())
    sumdic[thissig] += frac

for alpha in fine_alphas:
  if(alpha != quicka): continue
  xplot = array("d")
  splot = array("d")
  for sig in sumdic.keys():
    xx,pp,aa = getXPhiAlpha(sig)
    if(aa != alpha): continue
    xplot.append(xx)
    splot.append(sumdic[sig])

  tg = ROOT.TGraph(len(xplot), xplot, splot)
  tg.SetMarkerStyle(20)
  tg.SetMarkerColor(ROOT.kBlack)
  tg.SetTitle("Sum of Fractions in All Alpha Bins, #alpha_true={}".format(alpha))
  tg.GetXaxis().SetTitle("X Mass ")
  tg.GetYaxis().SetTitle("Sum")
  cc = ROOT.TCanvas()
  cc.cd()
  tg.Draw("AP")
  cc.Print("Plots/Fracs/alpha{}.png".format(alpha))


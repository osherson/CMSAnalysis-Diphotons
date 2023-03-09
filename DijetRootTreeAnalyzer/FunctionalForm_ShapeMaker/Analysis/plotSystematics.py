import numpy as np
import ROOT
import sys,os

ROOT.gROOT.SetBatch()

dir_path = os.path.dirname(os.path.realpath(__file__))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

def MakeFolder(N):
   import os
   if not os.path.exists(N):
    os.makedirs(N)

int_dir = "../../inputs/Shapes_fromInterpo/unBinned"

useshapes = ["nominal","PU","PD","SU","SD"]
colors = [1,2,4,6,7]

if("clean" in sys.argv):
  print("Deleting old plots")
  os.system("rm -rf Plots/alpha*")

def makeHist(fpath, shape):
    infname = "Sig_{}".format(shape)
    if (os.path.exists("{}/{}.root".format(fpath,infname))):
      intfil = ROOT.TFile("{}/{}.root".format(intpath,infname),"read")
      inthist = intfil.Get("h_AveDijetMass_1GeV")
      #inthist = intfil.Get("{}_XM".format(xaa))
    else:
      print("BAD: ",xaa)
      return

    try:
      inthist.SetLineColor(colors[ii])
    except AttributeError:
      print("Bad mass point: {}".format(xaa))
      return

    mxx = inthist.GetMaximum()
    inthist.GetYaxis().SetRangeUser(0,mxx*1.2)
    if(shape=="X"):
      inthist.GetXaxis().SetRangeUser(xm*0.75, xm*1.25)
      inthist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
    inthist.SetTitle("{}".format(xaa))
    inthist.SetLineWidth(2)
    #inthist.SetFillStyle(3002)
    inthist.SetFillStyle(0)

    newHist = inthist.Clone()
    newHist.SetName("hist_{}".format(shape))

    tf = ROOT.TFile("temproot.root","update")
    tf.cd()
    newHist.Write()
    tf.Write()
    tf.Close()

    return  newHist.GetMaximum()

for xaa in os.listdir(int_dir):
  xm,phim,alpha = getXPhiAlpha(xaa)
  intpath = os.path.join(int_dir,xaa)
  if(alpha > 0.025): continue
  #if(alpha != 0.005): continue
  #if(xaa != "X400A2"): continue

  histlist = []
  leg = ROOT.TLegend(0.65,0.65,0.88,0.88)

  if(os.path.exists("temproot.root")): os.system("rm temproot.root")
  pmax = 0
  for (ii,shape) in enumerate(useshapes):
    tmax = makeHist("../../inputs/Shapes_fromInterpo/unBinned/{}/".format(xaa), shape)
    if(tmax > pmax): pmax = tmax

  hfile = ROOT.TFile("temproot.root")
  cc = ROOT.TCanvas()
  cc.cd()
  for (ii,shape) in enumerate(useshapes):
    thishist = hfile.Get("hist_{}".format(shape))
    try:
      thishist.SetLineColor(colors[ii])
    except AttributeError: break
    thishist.SetFillStyle(0)
    thishist.SetStats(0)
    thishist.GetXaxis().SetRangeUser(0.85*xm,1.15*xm)
    thishist.GetYaxis().SetRangeUser(0,pmax*1.02)

    leg.AddEntry(thishist, shape)
    if(ii==0): thishist.Draw("hist")
    else: thishist.Draw("hist same")

  leg.Draw("same")
  #cc.SetLogy()
  cc.Print("Plots/alpha{}/{}_allsys.png".format(alpha,xaa))



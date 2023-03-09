import numpy as np
import ROOT
import sys,os

ROOT.gROOT.SetBatch()

dir_path = os.path.dirname(os.path.realpath(__file__))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha

def MakeFolder(N):
   import os
   if not os.path.exists(N):
    os.makedirs(N)

int_dir = "../../inputs/Shapes_fromInterpo/unBinned"

#useshapes = ["X","alpha"]
#useshapes=["X"]
useshapes = ["alpha"]

if("clean" in sys.argv):
  print("Deleting old plots")
  os.system("rm -rf Plots/alpha*")

for xaa in os.listdir(int_dir):
  xm,phim,alpha = getXPhiAlpha(xaa)
  #if(alpha != 0.009):continue
  #if(alpha >= 0.006):continue
  intpath = os.path.join(int_dir,xaa)
  #if(xaa != "X1710A8p55"): continue

  for shape in useshapes:
    #if(shape=="alpha"):continue
    infname = "Sig_nominal"
    #infname = "PLOTS"
    if (os.path.exists("{}/{}.root".format(intpath,infname))):
      intfil = ROOT.TFile("{}/{}.root".format(intpath,infname),"read")
      if(shape=="X"):
        rinthist = intfil.Get("h_AveDijetMass_1GeV")
        #inthist = intfil.Get("{}_XM".format(xaa))
      elif(shape=="alpha"):
        #rinthist = intfil.Get("h_alpha_fine")
        rinthist = intfil.Get("h_alpha_fine_i")
        #genhist.Rebin(5)
        #inthist.Rebin(5)
    else:
      print("BAD: ",xaa)

    try:
      rinthist.SetLineColor(ROOT.kRed)
      rinthist.SetFillColor(ROOT.kRed)
    except AttributeError:
      print("Bad mass point: {}".format(xaa))
      continue

    #c = ROOT.TCanvas()
    #c.cd()
    #rinthist.Draw("hist")
    #c.Print("tmp.png")

    if(shape=="alpha"):
      AfineB = list(np.linspace(0.0,0.035, 1001))
      inthist = ROOT.TH1D(rinthist.GetName()+'_f','',len(AfineB)-1,np.array(AfineB))
      for i in range(1,rinthist.GetNbinsX()+1):
        inthist.Fill(rinthist.GetBinCenter(i),rinthist.GetBinContent(i))
      inthist.SetLineColor(ROOT.kRed)
      inthist.SetFillColor(ROOT.kRed)
    else: inthist = rinthist.Clone()

    #inthist.Scale(1/inthist.Integral())
    #print(inthist.Integral())


    mxx = inthist.GetMaximum()
    inthist.GetYaxis().SetRangeUser(0,mxx*1.2)
    if(shape=="X"):
      inthist.GetXaxis().SetRangeUser(xm*0.75, xm*1.25)
      inthist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
    elif(shape=="alpha"):
      inthist.GetXaxis().SetRangeUser(0.0, 0.035)
      inthist.GetXaxis().SetTitle("#alpha")
    inthist.SetTitle("{}".format(xaa))
    inthist.SetLineWidth(2)
    inthist.SetFillStyle(3002)

    cc = ROOT.TCanvas()
    cc.cd()
    inthist.Draw("hist")
    MakeFolder("Plots/alpha_i/alpha{}/{}".format(alpha,shape))
    cc.Print("Plots/alpha_i/alpha{}/{}/{}.png".format(alpha,shape,xaa))

    intfil.Close()


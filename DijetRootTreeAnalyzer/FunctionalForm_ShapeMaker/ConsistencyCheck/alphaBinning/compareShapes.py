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

gen_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"
int_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/Disco/TLinearFitterMethod/inputs/Shapes_fromInterpo/alphaBinning"

#useshapes = ["X","alpha"]
useshapes = ["X"]
#useshapes = ["alpha"]

for s in useshapes:
   os.system("rm Plots/{}/*".format(s))

for abin in os.listdir(gen_dir):
  if(abin=="save"):continue
  for xaa in os.listdir(os.path.join(gen_dir,abin)):
    xm,phim,alpha = getXPhiAlpha(xaa)
    #if(xm!=300):continue
    if(not os.path.exists(os.path.join(int_dir,abin,xaa))):
      print("No interpo dir: {}/{}".format(abin,xaa))
    if(os.path.exists(os.path.join(int_dir,abin,xaa))):
      genpath = os.path.join(gen_dir,abin,xaa)
      intpath = os.path.join(int_dir,abin,xaa)

      for shape in useshapes:
        #if(shape=="alpha"):continue
        if (os.path.exists("{}/PLOTS_{}.root".format(genpath,abin)) and os.path.exists("{}/PLOTS_{}.root".format(intpath,abin))):
          genfil = ROOT.TFile("{}/PLOTS_{}.root".format(genpath,abin),"read")
          intfil = ROOT.TFile("{}/PLOTS_{}.root".format(intpath,abin),"read")
          if(shape=="X"):
            genhist = genfil.Get("h_AveDijetMass_1GeV")
            inthist = intfil.Get("h_AveDijetMass_1GeV")
          elif(shape=="alpha"):
            genhist = genfil.Get("h_alpha_fine")
            inthist = intfil.Get("h_alpha_fine")
            #genhist.Rebin(5)
            #inthist.Rebin(5)
          elif(shape=="phi"):
            genhist = genfil.Get("h_phi_fine")
            inthist = intfil.Get("h_phi_fine")
            #genhist.Rebin(5)
            #inthist.Rebin(5)
        else:
          print("BAD: ",xaa)

        try:
          genhist.SetLineColor(ROOT.kBlue)
          genhist.SetFillColor(ROOT.kBlue)
          inthist.SetLineColor(ROOT.kRed)
          inthist.SetFillColor(ROOT.kRed)
        except AttributeError:
          print("Bad mass point: {}".format(xaa))
          continue

        leg = ROOT.TLegend(0.15,0.7,0.35,0.86)
        leg.AddEntry(genhist, "Generated")
        leg.AddEntry(inthist, "Interpolated")
        leg.SetBorderSize(0)

        mxx = max(inthist.GetMaximum(), genhist.GetMaximum())
        for hh in [genhist,inthist]:
          hh.GetYaxis().SetRangeUser(0,mxx*1.2)
          if(shape=="X"):
            hh.GetXaxis().SetRangeUser(xm*0.75, xm*1.25)
            hh.GetXaxis().SetTitle("DiCluster Mass (GeV)")
          elif(shape=="alpha"):
            hh.GetXaxis().SetRangeUser(0.0, 0.035)
            hh.GetXaxis().SetTitle("#alpha")
          hh.SetTitle("{}, alpha bin {}".format(xaa,abin))
          hh.SetLineWidth(2)
          hh.SetFillStyle(3002)

        cc = ROOT.TCanvas()
        cc.cd()
        genhist.Draw("hist")
        inthist.Draw("histsame")
        leg.Draw("same")
        cc.Print("Plots/{}/{}_alpha{}.png".format(shape,xaa,abin))

        genfil.Close()
        intfil.Close()


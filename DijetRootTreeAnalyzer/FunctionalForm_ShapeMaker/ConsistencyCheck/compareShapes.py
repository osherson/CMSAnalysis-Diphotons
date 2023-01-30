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

gen_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned/"
int_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/Disco/TLinearFitterMethod/inputs/Shapes_fromInterpo/unBinned"

#useshapes = ["X","alpha"]
#useshapes=["X"]
useshapes = ["alpha"]

for s in useshapes:
   os.system("rm Plots/{}/*".format(s))

for xaa in os.listdir(gen_dir):
  xm,phim,alpha = getXPhiAlpha(xaa)
  #if(xm!=300):continue
  if(not os.path.exists(os.path.join(int_dir,xaa))):
    print("No interpo dir: {}".format(xaa))
  if(os.path.exists(os.path.join(int_dir,xaa))):
    genpath = os.path.join(gen_dir,xaa)
    intpath = os.path.join(int_dir,xaa)

    for shape in useshapes:
      #if(shape=="alpha"):continue
      infname = "Sig_nominal"
      #infname = "PLOTS"
      if (os.path.exists("{}/{}.root".format(genpath,infname)) and os.path.exists("{}/{}.root".format(intpath,infname))):
        genfil = ROOT.TFile("{}/{}.root".format(genpath,infname),"read")
        intfil = ROOT.TFile("{}/{}.root".format(intpath,infname),"read")
        if(shape=="X"):
          genhist = genfil.Get("h_AveDijetMass_1GeV")
          inthist = intfil.Get("h_AveDijetMass_1GeV")
          #genhist = genfil.Get("{}_XM".format(xaa))
          #inthist = intfil.Get("{}_XM".format(xaa))
        elif(shape=="alpha"):
          genhist = genfil.Get("h_alpha_fine")
          rinthist = intfil.Get("h_alpha_fine")
          #genhist.Rebin(5)
          #inthist.Rebin(5)
        elif(shape=="phi"):
          genhist = genfil.Get("h_phi_fine")
          rinthist = intfil.Get("h_phi_fine")
          #genhist.Rebin(5)
          #inthist.Rebin(5)
      else:
        print("BAD: ",xaa)

      try:
        genhist.SetLineColor(ROOT.kBlue)
        genhist.SetFillColor(ROOT.kBlue)
        rinthist.SetLineColor(ROOT.kRed)
        rinthist.SetFillColor(ROOT.kRed)
      except AttributeError:
        print("Bad mass point: {}".format(xaa))
        continue


      if(shape=="alpha"):
        AfineB = list(np.linspace(0.0,0.035, 1001))
        inthist = ROOT.TH1D(rinthist.GetName()+'_f','',len(AfineB)-1,np.array(AfineB))
        for i in range(1,rinthist.GetNbinsX()+1):
          inthist.Fill(rinthist.GetBinCenter(i),rinthist.GetBinContent(i))
        inthist.SetLineColor(ROOT.kRed)
        inthist.SetFillColor(ROOT.kRed)
      else: inthist = rinthist.Clone()

      #genhist.Scale(1/genhist.Integral())
      #inthist.Scale(1/inthist.Integral())
      #inthist.Scale(genhist.Integral()/inthist.Integral())
      print(genhist.Integral())
      print(inthist.Integral())

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
        elif(shape=="phi"):
          hh.GetXaxis().SetRangeUser(phim*0.5, phim*1.5)
          hh.GetXaxis().SetTitle("Avg. Cluster Mass")
        hh.SetTitle("{}".format(xaa))
        hh.SetLineWidth(2)
        hh.SetFillStyle(3002)

      cc = ROOT.TCanvas()
      cc.cd()
      genhist.Draw("hist")
      inthist.Draw("histsame")
      leg.Draw("same")
      cc.Print("Plots/{}/{}.png".format(shape,xaa))

      genfil.Close()
      intfil.Close()


import sys,os
import numpy as np
import ROOT

ROOT.gROOT.SetBatch()

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

def DSCB(x, par):
  a1 = par[0]
  a2 = par[1]
  n1 = par[2]
  n2 = par[3]
  mean = par[4]
  sigma = par[5]
  N = par[6]

  t = (x[0]-mean)/sigma
  
  fact1TLessMinosAlphaL = a1/n1
  fact2TLessMinosAlphaL = (n1/a1) - a1 -t
  fact1THihgerAlphaH = a2/n2
  fact2THigherAlphaH = (n2/a2) - a2 +t

  if (-a1 <= t and a2 >= t):
      result = np.exp(-0.5*t*t)
  elif (t < -a1):
      result = np.exp(-0.5*a1*a1)*np.power(fact1TLessMinosAlphaL*fact2TLessMinosAlphaL, -n1)
  
  elif (t > a2):
      result = np.exp(-0.5*a2*a2)*np.power(fact1THihgerAlphaH*fact2THigherAlphaH, -n2)
  else: 
    return 0
  
  return N*result


def do_fit(signal, sysname, draw):
  ROOT.gStyle.SetOptStat(1111);
  func = ROOT.TF1('func', DSCB, -10., 10., 7)
  sig_file_name = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned/{}/Sig_{}.root".format(signal,sysname)
  sig_file = ROOT.TFile(sig_file_name, "read")

  xmass,phimass,alpha = getXPhiAlpha(signal)

  fmin, fmax = xmass*0.8, xmass*1.3
  hmass = sig_file.Get("h_AveDijetMass_1GeV")
  func = ROOT.TF1("func", DSCB, fmin, fmax, 7);
  func.SetParNames("a1","a2","n1","n2","mean","sigma", "N");
  func.SetParameters(1., 2, 1, 2, xmass, 4, hmass.GetMaximum());
  func.SetParLimits(0, 1e-2, 1.)
  func.SetParLimits(1, 1e-2, 3.)
  func.SetParLimits(2, 0.01, 10.)
  func.SetParLimits(3, 0.1, 20.)
  func.SetParLimits(4, fmin, fmax)

  hmass.GetXaxis().SetTitle("Di-Cluster Mass (GeV)")
  hmass.SetTitle("{} Signal X Mass Fit".format(signal))

  hmass.Fit("func","EM0");
  fa1,fa2=func.GetParameter(0),func.GetParameter(1)
  fn1,fn2=func.GetParameter(2),func.GetParameter(3)
  fmean=func.GetParameter(4)
  fsigma=func.GetParameter(5)
  fN=func.GetParameter(6)
  chi2 = func.GetChisquare()
  ndf = func.GetNDF()

  ofile=open("SystematicFitParams/{}/fitparams.csv".format(sysname),"a")
  ofile.write("{},{},{},{},{},{},{},{},{}\n".format(xmass,alpha,fa1,fa2,fn1,fn2,fmean,fsigma,fN))
  ofile.close()

  if(draw):
    cc = ROOT.TCanvas()
    cc.cd()

    hmass.GetXaxis().SetRangeUser(fmin,fmax);
    hmass.GetXaxis().SetTitle("");
    hmass.SetMarkerStyle(20);
    hmass.SetMarkerSize(1.0);
    hmass.SetMarkerColor(ROOT.kBlack);
    hmass.SetLineColor(ROOT.kBlack);
    hmass.SetLineWidth(2);

    func.SetLineColor(ROOT.kRed);

    hmass.Draw("PE0");
    func.Draw("same");

    l = ROOT.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetTextFont(42)
    l.SetNDC()
    #l.DrawLatex(0.7,0.96,"%i pb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
    l.DrawLatex(0.1,0.86,"#\chi^{2}/ndf=%.1f / %i = %.2f"%(round(chi2,1), ndf, chi2/ndf))

    if(not os.path.exists("FitPlots/Systematics")):
      os.system("mkdir FitPlots/Systematics")
    cc.Print("FitPlots/Systematics/{}/{}.png".format(sysname,signal))

  return

sig_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned/"

syslist = ["PU","PD","SU","SD"]
#syslist = ["PU"]

for sname in syslist:
    if(os.path.exists("SystematicFitParams/{}/fitparams.csv".format(sname))):
      os.system("rm SystematicFitParams/{}/fitparams.csv".format(sname))
      os.system("touch fitparams_X.csv")

for xx in os.listdir(sig_dir):
  x,p,a = getXPhiAlpha(xx)
  if(x == 200): continue
  if(a > 0.025): continue
  #if(x != 1000): continue
  #if(p != 3): continue

  print("Doing Signal {}".format(xx))

  for sname in syslist:
    do_fit(xx, sname, False)

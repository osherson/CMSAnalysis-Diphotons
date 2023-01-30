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


def do_fit(signal, shape):
  ROOT.gStyle.SetOptStat(1111);
  func = ROOT.TF1('func', DSCB, -10., 10., 7)
  sig_file_name = "../inputs/Shapes_fromGen/unBinned/{}/Sig_nominal.root".format(signal)
  sig_file = ROOT.TFile(sig_file_name, "read")

  xmass,phimass,alpha = getXPhiAlpha(signal)

  if(shape=="X"):
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

  elif(shape=="alpha"):
    fmin, fmax = alpha*0.25, alpha*1.5
    hmass = sig_file.Get("h_alpha_fine")
    hmass.Rebin(5)
    func = ROOT.TF1("func", DSCB, fmin, fmax, 7);
    func.SetParNames("a1","a2","n1","n2","mean","sigma", "N");
    func.SetParameters(0.1, 0.1, 100., 100., alpha, 1e-4, hmass.GetMaximum());
    func.SetParLimits(0, 1e-3, 2.)
    func.SetParLimits(1, 1e-3, 3.)
    func.SetParLimits(2, 0.1, 1e7)
    func.SetParLimits(3, 0.1, 1e7)
    func.SetParLimits(4, fmin, fmax)

    hmass.GetXaxis().SetTitle("#alpha")
    hmass.SetTitle("{} Signal #alpha Fit".format(signal))

  elif(shape=="phi"):
    fmin, fmax = (alpha*xmass)*0.25, (alpha*xmass)*1.5
    hmass = sig_file.Get("h_phi_fine")
    #hmass.Rebin(5)
    func = ROOT.TF1("func", DSCB, fmin, fmax, 7);
    func.SetParNames("a1","a2","n1","n2","mean","sigma", "N");
    func.SetParameters(0.1, 0.1, 100., 100., alpha*xmass, 1e-4, hmass.GetMaximum());
    func.SetParLimits(0, 1e-3, 2.)
    func.SetParLimits(1, 1e-3, 3.)
    func.SetParLimits(2, 0.1, 1e7)
    func.SetParLimits(3, 0.1, 1e7)
    func.SetParLimits(4, fmin, fmax)

    hmass.GetXaxis().SetTitle("Phi Mass")
    hmass.SetTitle("{} Signal #phi Fit".format(signal))


  hmass.Fit("func","EM0");
  fa1,fa2=func.GetParameter(0),func.GetParameter(1)
  fn1,fn2=func.GetParameter(2),func.GetParameter(3)
  fmean=func.GetParameter(4)
  fsigma=func.GetParameter(5)
  fN=func.GetParameter(6)
  chi2 = func.GetChisquare()
  ndf = func.GetNDF()

  ofile=open("fitparams_{}.csv".format(shape),"a")
  ofile.write("{},{},{},{},{},{},{},{},{}\n".format(xmass,alpha,fa1,fa2,fn1,fn2,fmean,fsigma,fN))
  ofile.close()

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

  cc.Print("FitPlots/{}_{}.png".format(signal,shape))

  return 

sig_dir = "../inputs/Shapes_fromGen/unBinned/"

#if(os.path.exists("fitparams_X.txt")):
#  os.system("rm fitparams_X.txt")
#  os.system("touch fitparams_X.txt")
if(os.path.exists("fitparams_alpha.txt")):
  os.system("rm fitparams_alpha.txt")
  os.system("touch fitparams_alpha.txt")
#if(os.path.exists("fitparams_phi.txt")):
#  os.system("rm fitparams_phi.txt")
#  os.system("touch fitparams_phi.txt")

for xx in os.listdir(sig_dir):
  x,p,a = getXPhiAlpha(xx)
  if(x == 200): continue
  if(a > 0.025): continue
  #if(x != 500): continue
  #if(a != 0.01): continue
  #if(p != 3): continue

  print("Doing Signal {}".format(xx))

  do_fit(xx, "X")
  do_fit(xx, "alpha")
  #do_fit(xx,"phi")

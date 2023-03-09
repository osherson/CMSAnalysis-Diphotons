import ROOT
import numpy as np
import sys,os

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha


int_dir = "../inputs/Shapes_fromInterpo/unBinned/"
smear_SF = 1 + 0.0078

total = 0
for sig in os.listdir(int_dir):
  total += 1

print("Need {}".format(total))

count = 0
for sig in os.listdir(int_dir):
  count += 1
  #if(sig != "X600A3") : continue
  xm,phi,alpha = getXPhiAlpha(sig)
  if(count % 100 == 0): 
    print("{}/{} ({:.2f})%".format(count,total,float(count)/float(total)*100))
  hfname = int_dir + "/" + sig + "/Sig_nominal.root"
  if(not os.path.exists(hfname)): 
    print("Trouble Getting: {}".format(hfname))
    continue
  hfile = ROOT.TFile(hfname, "update")
  ahist = hfile.Get("h_alpha_fine_i").Clone()
  nbins = ahist.GetNbinsX()
  hsmear = ROOT.TH1D("h_alpha_su","Smeared alpha;alpha;entries",nbins,0,0.03)

  pfile = open("{}/{}/params_alpha_i.txt".format(int_dir,sig))
  sigma = float(pfile.readline().split(",")[-2])
  pfile.close()

  for ii in range(1, nbins+1):
    bin_content = ahist.GetBinContent(ii)
    bin_center = ahist.GetBinCenter(ii)
    hsmear.SetBinContent(ii, ROOT.gRandom.Gaus(bin_content ,sigma*smear_SF))

  hfile.cd()
  hsmear.Write()
#  print("Orig  Mean: {}".format(ahist.GetMean()))
#  print("Smear Mean: {}".format(hsmear.GetMean()))
#  print("Orig  RMS: {}".format(ahist.GetRMS()))
#  print("Smear RMS: {}".format(hsmear.GetRMS()))
#  c1 = ROOT.TCanvas()
#  c1.cd()
#  ahist.SetLineColor(ROOT.kBlue)
#  ahist.Draw("hist")
#  hsmear.SetLineStyle(ROOT.kDashed)
#  hsmear.SetLineColor(ROOT.kRed)
#  hsmear.Draw("histsame")
#  c1.Draw()
#  c1.Print("temp.png")

  hfile.Close()


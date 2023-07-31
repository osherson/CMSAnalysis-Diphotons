import ROOT
import numpy as np
import sys,os

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha

anoms = []
anfile = "fix0p01/CorrectedParams/a1.txt"
for lin in open(anfile,"read").readlines():
    v = lin.strip().split(",")
    anoms.append((int(v[0]), float(v[1])))


int_dir = "../inputs/Shapes_fromInterpo/unBinned/"
smear_SF = 1 + 0.23

total = 0
for sig in os.listdir(int_dir):
  total += 1

print("Need {}".format(total))

count = 0
for sig in os.listdir(int_dir):
  count += 1
  #if(sig != "X990A9p9") : continue
  #if(count < 4000): continue
  xm,phi,alpha = getXPhiAlpha(sig)

  #if((xm,alpha) not in anoms):continue
  #else: 
  #  print(xm,alpha)

  if(xm==300):continue
  if(xm==3000):continue
  if(count % 100 == 0): 
    print("{}/{} ({:.2f})%".format(count,total,float(count)/float(total)*100))
  hfname = int_dir + "/" + sig + "/Sig_nominal.root"
  if(not os.path.exists(hfname)): 
    print("Trouble Getting: {}".format(hfname))
    continue

  hfile = ROOT.TFile(hfname, "update")
  names = [kk.GetName() for kk in hfile.GetListOfKeys()]
  if("h_alpha_fine_i" in names):
    ahist = hfile.Get("h_alpha_fine_i").Clone()
    pfile = open("{}/{}/params_alpha_i.txt".format(int_dir,sig),"r")
    sigma = float(pfile.readline().split(",")[-2])
    pfile.close()
  elif("h_alpha_fine" not in names):
    print("Problem with {}".format(sig))
    continue
  else:
    ahist = hfile.Get("h_alpha_fine").Clone()
    pfile = open("{}/{}/params_alpha.txt".format(int_dir,sig),"r")
    sigma = float(pfile.readline().split(",")[-2])
    pfile.close()
  nbins = ahist.GetNbinsX()
  hsmear = ROOT.TH1D("h_alpha_su","Smeared alpha;alpha;entries",nbins,0,0.03)

  for ii in range(1, nbins+1):
    bin_content = ahist.GetBinContent(ii)
    bin_center = ahist.GetBinCenter(ii)
    newContent = ROOT.gRandom.Gaus(bin_content, sigma*smear_SF)
    #newContent = ROOT.gRandom.Gaus(bin_content, smear_SF)
    #newContent = max(0.0, newContent) #Hardcode to 0 if negative
    hsmear.SetBinContent(ii, newContent)

  #hsmear.Scale(1/hsmear.Integral())
  
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


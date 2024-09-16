import os,sys
import numpy
import ROOT
from ROOT import *

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha

def WriteAlphaEff(signal, anum, eff, sdir):
  oFile = open("{}/alphaFraction_alpha{}_{}.txt".format(sdir,anum,sig), "w")
  #print(anum, eff)
  oFile.write(str(eff))
  oFile.close()
  return

def WriteAlphaEff_su(signal, anum, eff, sdir):
  oFile = open("{}/alphaFraction_alpha{}_{}_su.txt".format(sdir,anum,sig), "w")
  #print(anum, eff)
  oFile.write(str(eff))
  oFile.close()
  return

def WriteTotalEff(signal, anum, aeff, sdir):
  ceff_file = open("../inputs/Shapes_fromInterpo/unBinned/{}/{}.txt".format(sig,sig),"r")
  ceff = float(ceff_file.readlines()[0])
  teff = ceff * aeff

  oFile = open("{}/{}.txt".format(sdir,signal),"w")
  oFile.write(str(teff))
  oFile.close()
  return

def WriteTotalEff_su(signal, anum, aeff, sdir):
  ceff_file = open("../inputs/Shapes_fromInterpo/unBinned/{}/{}.txt".format(sig,sig),"r")
  ceff = float(ceff_file.readlines()[0])
  teff = ceff * aeff

  oFile = open("{}/{}_su.txt".format(sdir,signal),"w")
  oFile.write(str(teff))
  oFile.close()
  return

def WriteAlphaRange(signal, la,ha, sdir):
  oFile = open("{}/arange.txt".format(sdir),"w")
  oFile.write("{},{}".format(la,ha))
  oFile.close()
  return

def MakeFolder(N):
  if not os.path.exists(N):
    os.makedirs(N)

anoms = []
anfile = "fix0p01/CorrectedParams/a1.txt"
for lin in open(anfile,"read").readlines():
    v = lin.strip().split(",")
    anoms.append((int(v[0]), float(v[1])))


#10% Comb bins
#AlphaBins = [ 0.003, 0.00347, 0.00395,   0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.0093, 0.01049, 0.03]

#Full NDoF Comb Bins
AlphaBins = [
               0.003,
               0.00347, 
               0.00395,   
               0.00444, 
               0.00494, 
               0.00545, 
               0.00597, 
               #0.0065, 
               0.00704, 
               #0.00759, 
               0.00815, 
               0.03]

#All Reso Bins
#AlphaBins = [ 0.003, 0.00347, 0.00395,   0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.00989, 0.01049, 0.0111, 0.01173, 0.01237, 0.01302, 0.01368, 0.01436, 0.01505, 0.01575, 0.01647, 0.0172, 0.01794, 0.0187, 0.01947, 0.02026, 0.02106, 0.02188, 0.02271, 0.02356, 0.02443, 0.02531, 0.02621, 0.02713, 0.02806, 0.02901, 0.03]

int_dir = "../inputs/Shapes_fromInterpo/unBinned/"
#thresh = 0.05
thresh = 0.001

save_dir = "../inputs/Shapes_fromInterpo/alphaBinning/"
#save_dir = "../inputs/Shapes_fromInterpo/alphaBinning_allBins/"

nfiles = len([name for name in os.listdir(int_dir)])

oF = open("AlphaFracs/fracs.csv","w")

count=0
ccount=0
allfracs = []
for sig in os.listdir(int_dir):
  x,phi,alpha = getXPhiAlpha(sig)
  if(x == 300): continue
  #if(count % 100 == 0): print("{}/{} Files Completed {:.1f}%".format(count, nfiles, pdone))
  #if(alpha != 0.005): continue
  #if(x < 400 or x > 410): continue
  #if(x != 1000 ): continue
  #if(sig != "X2880A17p28"): continue
  #if((x,alpha) not in anoms): continue
  #else:
  #  print(x,alpha)
  print(sig)
  count += 1
  #if(count > 20): break
  #print(sig)
  #if(x != 600): continue

  #print("-----")
  #print(sig)

  nomfile = os.path.join(int_dir,sig,"Sig_nominal.root")
  nF = TFile(nomfile,"read")

  names = [kk.GetName() for kk in nF.GetListOfKeys()]

  if("h_alpha_fine_i" in names):
    ahist = nF.Get("h_alpha_fine_i")
    ahist_su = nF.Get("h_alpha_su")
    ccount += 1
  else:
    print("BAD: {}".format(sig))
    continue

  try:
    tI = ahist.Integral()
    tI_su = ahist_su.Integral()
  except AttributeError:
    print("Bad Point: {}".format(nomfile))
    print(nomfile)
    continue

  if(not os.path.exists("../inputs/Shapes_fromInterpo/unBinned/{}/{}.txt".format(sig,sig))):
    print("bad: {}".format(sig)) 
    continue

  fraclist = []
  qfraclist = []
  for abin in range(len(AlphaBins)-1):
    lA, hA = AlphaBins[abin], AlphaBins[abin+1]
    lAb = ahist.FindBin(lA)
    hAb = ahist.FindBin(hA)
    aI = ahist.Integral(lAb,hAb)
    frac = aI / tI
    fraclist.append(frac)
    allfracs.append(frac)
    #print(abin, lA, hA)
    #print(frac)
    if(frac < thresh): 
      frac = 1e-6
      continue
    #print(abin, frac)
    if(frac < 1e-7): frac = 1e-7
    qfraclist.append(frac)

    ahist_su.Smooth()
    lAb_su = ahist_su.FindBin(lA)
    hAb_su = ahist_su.FindBin(hA)
    aI_su = ahist_su.Integral(lAb_su,hAb_su)
    aI_su = max(0.0, aI_su)
    #c1 = ROOT.TCanvas()
    #c1.cd()
    #ahist_su.GetXaxis().SetRangeUser(lA,hA)
    #ahist_su.Draw()
    #c1.Print("temp.png")
    #print(ahist_su.Integral())
    #print(lAb_su,hAb_su)
    #print(aI_su, tI_su)
    frac_su = aI_su / tI_su

    print("{}, {:4f}, {:.4f}, {:.4f}".format(abin, frac*100, frac_su*100, abs(frac_su - frac)/frac * 100))

    MakeFolder("{}{}".format(save_dir,abin))
    thisdir = "{}{}/{}".format(save_dir,abin,sig)
    MakeFolder(thisdir)


    WriteAlphaEff_su(sig,abin,frac_su,thisdir)
    WriteTotalEff_su(sig,abin,frac_su,thisdir)
    WriteAlphaRange(sig,lA,hA,thisdir)
    #continue
    #os.system("cp {}/{}/Sig*.root {}/.".format(int_dir,sig,thisdir))

    unb_plots = TFile("{}/{}/PLOTS.root".format(int_dir,sig), "read")
    S1 = unb_plots.Get("h_AveDijetMass_1GeV")
    S1r = unb_plots.Get("{}_XM".format(sig))

    #dfile = TFile("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/alphaBinning/{}/DATA.root".format(abin), "read")
    dfile = TFile("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/Unblinding/full_tight_ndofBins//{}/DATA.root".format(abin),"read")

    D1 = dfile.Get("data_XM1")
    D1r = dfile.Get("data_XM")

    n_plots = TFile("{}/PLOTS_{}.root".format(thisdir,abin),"recreate")
    n_plots.cd()
    S1.Write()
    S1r.Write()
    D1.Write()
    D1r.Write()
    n_plots.Close()
    dfile.Close()
    unb_plots.Close()
    os.system("cp /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/alphaBinning/{}/DATA.root {}/.".format(abin,thisdir))

  print(sum(fraclist))
  print(sum(qfraclist))

oF.close()
print("Corrected files: {}".format(ccount))


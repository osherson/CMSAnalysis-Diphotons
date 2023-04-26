import ROOT
import numpy as np
import os,sys
import itertools

def getNgen(signal):
  ys = [2016,2017,2018]
  ngs = []
  xmass = signal[1:signal.find("A")]
  amass = signal[signal.find("A")+1:].replace("p",".")

  for yy in ys:
     fname = "../../Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(yy)
     myFile = open(fname, "r")
     Lines = myFile.readlines()
     nevt = 0
     for line in Lines:
       s=line.split(",")
       if(s[0]==xmass and s[1]==amass):
         nevt = int(s[2])
     
     ngs.append(nevt)

  return sum(ngs)

#deta_cuts = [0.5, 1.5, 2.5, 3.5]

masym_cuts = [0.1, 0.25, 0.35, 0.5]
#deta_cuts = [0.5, 1.5, 2.5, 3.5]
deta_cuts = [0.5, 1.0, 1.5]
dipho_cuts = [0, 0.5, 0.75, 0.9]
iso_cuts = [0,0.1, 0.5, 0.8, 0.9]
combinations = itertools.product(masym_cuts, deta_cuts, dipho_cuts, iso_cuts)

#ncomb=0
#for (num,cc) in enumerate(combinations):
#  ncomb += 1
#print("N Combinations: {}".format(ncomb))
#exit()

cut_combos = {}
for (num,cc) in enumerate(combinations):
  #if(num > 4): break
  #if(num >= 100): continue
  #if(num < 100 or num >= 200): continue
  #if(num < 200 ): continue
  if(num != int(sys.argv[1])):continue
  #if(os.path.exists("CutOutFiles/cut{}_out.csv".format(num))):
  #  print("We already did this")
  #  exit()
  cut_combos[num]=cc
RDF = ROOT.RDataFrame.RDataFrame
#print(cut_combos)

def GetXPhiAlpha(ins):
  X = int(ins[ins.find("X")+1 : ins.find("A")])
  Phi = float(ins[ins.find("A")+1 : ].replace("p","."))
  Alpha = round(Phi/X,3)
  return X, Phi, Alpha

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

dchain = ROOT.TChain("pico_skim")
sigdict = {}

LUMI = 136.1 / 10

XS = { 300: 3746.96,
       400: 1017.87,
       500: 353.898,
       600: 158.506,
       750: 45.9397,
       1000: 9.59447,
       1500: 0.847454,
       2000: 0.122826 ,
       3000: 0.00531361,
      }


for fil in os.listdir(xaastorage):
  if(fil.startswith("Run") and fil.endswith(".root")):
    if(fil != "Run_C_2017.root"): continue #Testing only
    print("data file: {}".format(fil))
    dchain.Add(os.path.join(xaastorage,fil))
  elif(fil.startswith("X") and fil.endswith(".root")):
    stem=fil.replace(".root","")
    stem = stem.replace("_201","")
    stem=stem[:-1]

    xm,phim,alpha = GetXPhiAlpha(stem)
    if(alpha > 0.025): continue
    if(xm < 300): continue

    if(stem in sigdict.keys()):
      sigdict[stem].append(os.path.join(xaastorage,fil))
    else:
      sigdict[stem]=[os.path.join(xaastorage,fil)]
      oF = open("outFiles/{}_out.csv".format(stem),"w")
      oF.write("masym,deta,dipho,iso,s,b,srootb,signal\n")
      oF.close()

ddf = RDF(dchain)

print("Applying trigger, pt cuts")
ddf = ddf.Filter("HLT_DoublePhoton >= 1", "Trigger")
ddf = ddf.Filter("clu1_pt > 90 && clu2_pt > 90", "pt cut")
di = ddf.Count().GetValue()

#cut_combos = { 1:(0.1,  3.5, 0.9,  0.8),
#               2:(0.1,  2.5, 0.9,  0.8),
#               3:(0.25, 3.5, 0.9,  0.8),
#               4:(0.25, 1.5, 0.9,  0.8),
#               5:(0.25, 2.5, 0.9,  0.8),
#               6:(0.1,  3.5, 0.75, 0.8),
#               7:(0.1,  2.5, 0.75, 0.8),
#               8:(0.1,  1.5, 0.75, 0.8),
#               9:(0.1,  3.5, 0.5,  0.8),
#              }

srdic = {}

for (comb_num,cuts) in cut_combos.items():
  print("Trying Combination: {}". format(cuts))
  #if(comb_num > 2): break

  ddf = ddf.Filter("masym < {} && deta < {} && clu1_dipho > {} && clu2_dipho > {} && clu1_iso > {} && clu2_iso > {}".format(cuts[0],cuts[1],cuts[2],cuts[2],cuts[3],cuts[3]))
  #bkg=ddf.Count().GetValue()
  #print("Background Value: {}".format(bkg))

  cfile = open("CutOutFiles/cut{}_out.csv".format(comb_num), "w")
  cfile.write("masym,deta,dipho,iso,s,b,srootb,signal\n")

  sct = 0
  for (sig, flist) in sigdict.items():
    if(sct > 3): break #testing
    print("Starting Signal: {}".format(sig))
    sct += 1
    schain = ROOT.TChain("pico_nom")
    for ff in flist: 
      schain.Add(ff)
    sdf = RDF(schain)
    sdf = sdf.Filter("HLT_DoublePhoton >= 1", "Trigger")
    sdf = sdf.Filter("clu1_pt > 90 && clu2_pt > 90", "pt cut")
    sdf = sdf.Filter("masym < {} && deta < {} && clu1_dipho > {} && clu2_dipho > {} && clu1_iso > {} && clu2_iso > {}".format(cuts[0],cuts[1],cuts[2],cuts[2],cuts[3],cuts[3]))

    smass = sdf.Histo1D(("xm_{}".format(sig),"X Mass", 5000,0,5000),"XM")
    smh = smass.GetValue().Clone()
    print(sig)
    sigmean = smh.GetMean()
    sigstd = smh.GetStdDev()
    print(sigmean, sigstd)

    myngen = getNgen(sig)
    myxs = XS[int(sig[1:sig.find("A")])]
    print("NGen", myngen)
    print("XSec: ", myxs)

    #Apply mass window
    #xlow = sigmean - 2*sigstd
    #xhigh = sigmean + 2*sigstd
    #dmass = ddf.Filter("XM > {} && XM < {}".format(xlow, xhigh), "Mass window")
    #sdf = sdf.Filter("XM > {} && XM < {}".format(xlow, xhigh), "Mass window")
    #bkg=dmass.Count().GetValue()

    bkg=ddf.Count().GetValue()

    scalefactor = (myxs / myngen) * LUMI
    sval = sdf.Count().GetValue() * scalefactor
    print("Background Value: {}".format(bkg))
    print("Signal Value: {}".format(sval))
    print(bkg,sval)
    srootb = sval/np.sqrt(bkg+sval)
    
    oF = open("outFiles/{}_out.csv".format(sig),"a")
    oF.write("{},{},{},{},{},{},{},{}\n".format(cuts[0],cuts[1],cuts[2],cuts[3],sval,bkg,srootb,sig))
    cfile.write("{},{},{},{},{},{},{},{}\n".format(cuts[0],cuts[1],cuts[2],cuts[3],sval,bkg,srootb,sig))
    oF.close()

    if(comb_num in srdic.keys()): srdic[comb_num].append((srootb,sig)) 
    else: srdic[comb_num] = [(srootb,sig)]

  cfile.close()

#for (comb, v) in srdic.items():
#  print(comb, v)



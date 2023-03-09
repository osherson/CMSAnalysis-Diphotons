import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
from ROOT import *
import numpy
import sys,os
import math
import scipy
from array import array
import csv
import time

#ROOT.gRandom.SetSeed(0)

dir_path = os.path.dirname(os.path.realpath(__file__))


DATA_DIR = "{}/../inputs/Shapes_DATA/alphaBinning/ALL/".format(dir_path)

doOne=False
if("one" in sys.argv or "quick" in sys.argv):
  doOne=True

if(not doOne):
  ROOT.gROOT.SetBatch(ROOT.kTRUE) #Use this line to not show plots

def MakeFolder(N):
  if not os.path.exists(N):
     os.makedirs(N)

def Make1BinsFromMinToMax(Min,Max):
    BINS = []
    for i in range(int(Max-Min)+1):
        BINS.append(Min+i)
    return numpy.array(BINS)

def convertToMjjHist(hist_th1x,xbins):

    hist = TH1D(hist_th1x.GetName()+'_mjj',hist_th1x.GetName()+'_mjj',len(xbins)-1,numpy.array(xbins))
    for i in range(1,hist_th1x.GetNbinsX()+1):
        #hist.SetBinContent(i,hist_th1x.GetBinContent(i)/(xbins[i]-xbins[i-1]))
        #hist.SetBinError(i,hist_th1x.GetBinError(i)/(xbins[i]-xbins[i-1]))
        hist.Fill(hist_th1x.GetBinCenter(i), hist_th1x.GetBinContent(i))

    return hist

X1B = Make1BinsFromMinToMax(200., 3110.)
XB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]
#AfineB = list(numpy.linspace(0.0,0.03, 5001))
AfineB = list(numpy.linspace(0.0,0.03, 10000))
AlphaBins = [ 0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.01049, 0.01505, 0.03]
for aa in AlphaBins:
  if(aa not in AfineB): AfineB.append(aa)
AfineB = sorted(AfineB)

#AfineB = list(numpy.linspace(0.0,0.035, 1001))


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
      result = numpy.exp(-0.5*t*t)
  elif (t < -a1):
      result = numpy.exp(-0.5*a1*a1)*numpy.power(fact1TLessMinosAlphaL*fact2TLessMinosAlphaL, -n1)

  elif (t > a2):
      result = numpy.exp(-0.5*a2*a2)*numpy.power(fact1THihgerAlphaH*fact2THigherAlphaH, -n2)
  else:
    return 0

  return N*result


def Mean(list):
	if len(list) > 0:
		return float(sum(list))/len(list)
	else:
		return 0.
		
def std(list):
	if len(list) > 0:
		m = Mean(list)
		difs2 = 0.
		for i in list:
				difs2 += (i - m)**2
		return math.sqrt(difs2/len(list))
	else:
		return 0.
		
def StandardizeArray(A):
	m = Mean(A)
	s = std(A)
	B = []
	for i in A:
		B.append((i-m)/s)
	def cF(x): return (x - m)/s
	return [B, cF, m, s]
	
def MixArray(A):
	n = len(A[0])
	out = []
	for i in range(0,n):
		for J in A:
			out.append(J[i])
	return out

def FIND(V, X, A, a):
  sV = StandardizeArray(V)
  sX = StandardizeArray(X)
  sA = StandardizeArray(A)
  sa = StandardizeArray(a)
  data = MixArray([X,A,a])
  string_form = "1"
  for i in range(4):
			string_form += "++x["+str(i)+"]"
  LINF = TLinearFitter(3, string_form)
  LINF.AssignData(len(X), 3, scipy.array(data), scipy.array(V))
  done = False
  while not done:
		good = 1. - LINF.Eval()
		if good == 1. : done = True
  for i in range(3): print LINF.GetParameter(i)
  print good
  return LINF, sV, sX, sA, sa

def MakePredictor(F, cV, cX, cA, ca):
  def P(X,A):
    o = 0.
    o += F.GetParameter(0)
    o += F.GetParameter(1)*X
    o += F.GetParameter(2)*A
    o += F.GetParameter(3)*A/X
    return o
	
  return P

def MakeFunc(tn, shape, inx, inalpha, odir):
  print "Reading in params"
  if(tn=="nominal"):
    fname = "{}/fitparams_{}.csv".format(dir_path,shape)
  else:
    fname = "{}/SystematicFitParams/{}/fitparams.csv".format(dir_path,tn)

  with open(fname, 'r') as csvf: 
    X = []
    a = []
    A = []
    a1 = [] 
    a2 = [] 
    n1 = [] 
    n2 = [] 
    mn = []
    sig = []
    N = []
    csvr = csv.reader(csvf)
    row = list(csvr)
    for r in row:
      thisx, thisalpha = float(r[0]), float(r[1])
      thisphi = thisx*thisalpha
      if(shape == "alpha" and inalpha==0.005 and thisalpha > 0.02): continue
      #if(shape == "alpha" and inalpha==0.01 and thisalpha > 0.025): continue
      #if(shape == "alpha" and inalpha==0.01 and thisalpha > 0.02): continue
      #if(shape == "alpha" and inx<=400 and thisx > 2000): continue
      if(shape == "alpha" and inx==2000 and thisx < 400): continue
      #if(shape == "alpha" and inx>=2000 and thisx < 600): continue
      #if(shape == "alpha" and inalpha==0.01 and thisalpha >= 0.02): continue
      X.append(thisx)
      a.append(thisalpha)
      A.append(thisphi)
      a1.append(float(r[2]))
      a2.append(float(r[3]))
      n1.append(float(r[4]))
      n2.append(float(r[5]))
      mn.append(float(r[6]))
      sig.append(float(r[7]))
      N.append(float(r[8]))
    Predictors = []
    for P in [a1,a2,n1,n2,mn,sig,N]:
      linf, cV, cX, cA, ca = FIND(P, X, A, a)
      p = MakePredictor(linf, cV, cX, cA, ca)
      Predictors.append(p)
    def CustDSCB(X,a,name):
      G = TF1(name, DSCB, 0, 3500, 7 );
      G.SetParNames("a1","a2","n1","n2","mean","sigma", "N");
      G.SetParameter("a1", Predictors[0](X,a))
      G.SetParameter("a2", Predictors[1](X,a))
      G.SetParameter("n1", Predictors[2](X,a))
      G.SetParameter("n2", Predictors[3](X,a))
      G.SetParameter("mean", Predictors[4](X,a))
      G.SetParameter("sigma", Predictors[5](X,a))
      G.SetParameter("N", Predictors[6](X,a))

      pfile = open("{}/params_{}.txt".format(odir,shape),"w")
      print("a1: {}".format(Predictors[0](X,a)))
      print("a2: {}".format(Predictors[1](X,a)))
      pfile.write("{},{},{},{},{},{},{}".format(Predictors[0](X,a),Predictors[1](X,a),Predictors[2](X,a),Predictors[3](X,a),Predictors[4](X,a),Predictors[5](X,a),Predictors[6](X,a)))
      pfile.close()

      return G
    return CustDSCB

def WriteEff(wx, wa, frac, odir):

   fullEffFile=open("{}/EffStuff/FULL.csv".format(dir_path),"r")
   for lin in fullEffFile.readlines():
     sl = lin.split(",")
     fx = int(sl[0])
     falpha = float(sl[1])
     fa = round(fx * falpha,4)
     if(fx==int(wx) and fa==float(wa.replace("p","."))):
       thisEff = float(sl[2][:-1])
       break

   eff = frac*thisEff
   effName = "{}/X{}A{}.txt".format(odir,wx,wa)
   effName = effName.replace("p0.txt",".txt")
   effFile= open(effName,"w")
   effFile.write(str(eff))
   effFile.close()
   return

def getNearestZero(hist, startbin):
  for bb in range(startbin, hist.GetNbinsX()):
    if(hist.GetBinContent(bb)==0):
      return (bb-startbin)
  return -999

known_xs = [300,400,500,600,750,1000,1500,2000,3000]
known_alphas = [0.005, 0.01, 0.015, 0.02, 0.025]
#known_alphas = [0.005, 0.01]

def getNearestX(inx):
  inx = int(inx)
  if(inx in known_xs): loop_xs = [xx for xx in known_xs if xx != inx]
  else: loop_xs = known_xs

  for ii in range(0,len(loop_xs)-1):
    if(loop_xs[ii] <= inx and loop_xs[ii+1] > inx):
      return loop_xs[ii], loop_xs[ii+1]

def readParams(inx, alpha):
  print(inx,alpha)
  pfile = open("fitparams_alpha.csv")
  for lin in pfile.readlines():
    sl = lin.split(",")
    fx = int(sl[0])
    if(fx == inx):
      fa = float(sl[1])
      if(fa == alpha):
        return float(sl[4])

TREES = [
	"nominal" ,
  "PU",
  "PD",
  "SU",
  "SD"
	]



#xmin, xmax = 320, 3000
xmin, xmax = 320, 400
xstep = 10
fine_xs = [xx for xx in range(xmin, xmax+xstep, xstep)]

alphamin, alphamax = 0.005, 0.03
nalphas = 25+1
fine_alphas = numpy.linspace(alphamin, alphamax, nalphas)


if(doOne): useShapes = ["alpha"]
else: useShapes = ["X","alpha"]
#else: useShapes = ["alpha"]

def MakeShape(x, alpha):
  for shape in useShapes:
    for tname in TREES:
      if(shape=="alpha" and tname !="nominal"): continue
      #if(tname !="nominal"):continue
      a = int(x)*alpha
      x=str(x)
      a=str(round(a,4)).replace(".","p")
      newFolder = "{}/../inputs/Shapes_fromInterpo/unBinned/X{}A{}".format(dir_path,x,a)
      #newFolder = "{}/inputs/Shapes_fromInterpo/unBinned/X{}A{}".format(dir_path,x,a)
      if(newFolder.endswith("p0")): newFolder = newFolder[:-2]
      MakeFolder(newFolder)

      if(shape=="X"):
        oF = TFile("{}/Sig_{}.root".format(newFolder,tname), "recreate")
        s1int = 0.0
        lc = 0
        while(s1int <= 0.0):
          lc += 1
          print("Starting Loop {} ".format(lc))
          F = MakeFunc(tname, shape, x, alpha, newFolder)
          P = F(float(x), float(a.replace("p",".")), "test"+x+a)
          S1 = TH1F("h_AveDijetMass_1GeV_raw", ";Dicluster Mass (GeV)", len(X1B)-1, numpy.array(X1B))
          S1.FillRandom("test"+x+a, 10000)
          s1int = S1.Integral()
          if(lc >=100):

            print("Too many loops. Giving Up")
            break
        print "--- - ", tname
        print x,a

        oF.cd()
        s1 = S1.Clone("h_AveDijetMass_1GeV")
        sR = convertToMjjHist(S1, XB)
        srname = "X{}A{}_XM".format(x,a)
        srname=srname.replace("p0_","_")
        sR.SetName(srname)
        #s.Scale(N/S.Integral())
        s1.Scale(1/s1.Integral())
        sR.Scale(1/sR.Integral())
        s1.Write()
        #f.Write()
        oF.Write()

        
        if(tname=="nominal"):
          dataFile = ROOT.TFile("{}/DATA.root".format(DATA_DIR), "read")
          os.system("cp {}/DATA.root {}/DATA.root".format(DATA_DIR, newFolder))
          dX = dataFile.Get("data_XM")
          dX1 = dataFile.Get("data_XM1")
          dXvA = dataFile.Get("data_XvA")

          plotsF = ROOT.TFile(newFolder+"/PLOTS.root", "recreate")
          sR.Write()
          s1.Write()
          dX.Write()
          dX1.Write()
          
          plotsF.Close()
          dataFile.Close()

          WriteEff(x, a, 1, newFolder)

      elif(shape=="alpha"):
        oF = TFile("{}/Sig_{}.root".format(newFolder,tname), "update")
        s1int = 0.0
        lc = 0
        isBadDown = False
        isBadUp = False
        isOutOfRange = False
        isNan = False

        xdown,xup = getNearestX(x)

        while(s1int <= 0.0 or isBadDown==True or isBadUp==True):
        #while(s1int <= 0.0 or isBadDown==True or isBadUp==True or isOutOfRange==True or isNan==True):
          print("Starting Loop {}".format(lc))
          isBadDown = False
          isBadUp = False
          lc += 1
          F = MakeFunc(tname, shape, x, alpha, newFolder)
          P = F(float(x), float(a.replace("p",".")), "test"+x+a)
          S1 = TH1F("h_alpha_fine", ";#alpha", len(AfineB)-1, numpy.array(AfineB))
          S1.FillRandom("test"+x+a, 10000)
          s1int = S1.Integral()

#          pfile = open("{}/params_alpha.txt".format(newFolder),"r")
#          lin = pfile.readlines()[0]
#          lin = lin.split(",")
#          if("nan" in lin or "-nan" in lin): 
#            isnan = True
#            continue
#          a1=lin[1]
#          if(a1 !="nan"): a1 = float(a1)
#          pxlow,pxhigh = readParams(xdown, alpha), readParams(xup, alpha)
#
#          if(a1 < pxlow or a1 > pxhigh):
#            print("Params not in range: {} , {} , {}".format(pxlow,a1,pxhigh))
#            isOutOfRange = True
#            continue

          if(s1int > 0):
            ti = S1.Integral()
            cbin = S1.FindBin(alpha)
            li = S1.Integral(0,cbin)
            hi = S1.Integral(cbin, S1.GetNbinsX())
            min_center = min(li,hi)
            if(min_center <=0.0): 
              isBadDown=True
              continue
            else: 
              nzero = getNearestZero(S1, S1.GetMaximumBin())
              if(nzero < 50):
                isBadUp=True
                continue

          if(doOne):
            print("Before Alpha Integral: {}".format(S1.Integral(0,S1.FindBin(alpha))))
            print("After Alpha Integral: {}".format(S1.Integral(S1.FindBin(alpha),S1.GetNbinsX())))
            print("Width: {}".format(S1.GetRMS()))
          if(lc >100):
            print("Too many loops. Giving Up")
            break
        print "--- - ", shape, tname
        print x,a
        s1 = S1.Clone("h_alpha_fine")
        if(s1.Integral()==0):continue
        s1.Scale(1/s1.Integral())
        oF.cd()
        s1.Write()

        #if(doOne):
          #cc=TCanvas()
          #cc.cd()
          #s1.Draw("hist")
          #cc.Print("tmp.png")


      oF.Save()
      oF.Close()
      print "++++++=========+++++++"
      print tname
      print "++++++=========+++++++"
		
inX, inAlpha = int(sys.argv[1]), float(sys.argv[2])
MakeShape(inX, inAlpha)


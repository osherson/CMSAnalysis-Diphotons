from ROOT import *
from array import *
import numpy as np
import os
import sys

outdir = "../DoAlphaFits/saveOutput"
function = sys.argv[1]
gROOT.SetBatch()

use_XA = {0: "X600A3",
          1: "X600A3",
          2: "X600A3",
          3: "X600A3",
          4: "X600A3",
          5: "X600A3",
          12: "X600A6",
          13: "X600A9",
          14: "X600A12",
          }

npd = {3:"ThreeParams/", 4:"FourParams/", 5:"FiveParams", 6:"SixParams"}

#alphaBins = range(0,9+1)
alphaBins = use_XA.keys()

if("noshow" in sys.argv):
  gROOT.SetBatch()

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

outFolder="NParamPlots/{}/".format(function)
MakeFolder(outFolder)

dirs = []

for anum in alphaBins:
  thisD = "{}/ThreeParams/alpha_{}".format(outdir,anum)
  found = False
  for xa in os.listdir(os.path.join(thisD)):
    file3 = "{}/{}/DijetFitResults_diphoton_{}_{}_alpha{}.root".format(thisD, xa, xa, function, anum)
    file4 = file3.replace("Three","Four")
    file5 = file3.replace("Three","Five")
    file6 = file3.replace("Three","Six")
    if(function != "moddijet" and os.path.exists(file3) and os.path.exists(file4) and os.path.exists(file5) and os.path.exists(file6)):
      rfile = open("../inputs/Shapes_fromGen/alphaBinning/{}/{}/arange.txt".format(anum,xa))
      rr = rfile.readline().rstrip()
      lA =float(rr.split(",")[0])
      hA =float(rr.split(",")[-1])

      dirs.append((anum, lA, hA, [file3,file4,file5,file6]))
      found=True
    elif(function == "moddijet" and os.path.exists(file3) and os.path.exists(file4) and os.path.exists(file5)):
      rfile = open("../inputs/Shapes_fromGen/alphaBinning/{}/{}/arange.txt".format(anum,xa))
      rr = rfile.readline().rstrip()
      lA =float(rr.split(",")[0])
      hA =float(rr.split(",")[-1])

      dirs.append((anum, lA, hA, [file3,file4,file5]))
      found=True
    if found==True: break


lumi = 13.7 ##Check this
sqrts=np.sqrt(13000)

signal_mjj = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

x = array('d', signal_mjj) # mjj binning

def convertToMjjHist(hist_th1x):
    global x

    hist = TH1D(hist_th1x.GetName()+'_mjj',hist_th1x.GetName()+'_mjj',len(x)-1,x)
    for i in range(1,hist_th1x.GetNbinsX()+1):
        hist.SetBinContent(i,hist_th1x.GetBinContent(i)/(x[i]-x[i-1]))
        hist.SetBinError(i,hist_th1x.GetBinError(i)/(x[i]-x[i-1]))

    return hist

def convertToTh1xHist(hist):

    hist_th1x = TH1D(hist.GetName()+'_th1x',hist.GetName()+'_th1x',hist.GetNbinsX(),0,hist.GetNbinsX())
    for i in range(1,hist.GetNbinsX()+1):
        hist_th1x.SetBinContent(i,hist.GetBinContent(i))
        hist_th1x.SetBinError(i,hist.GetBinError(i))

    return hist_th1x


def getHistFromWorkspace(thisFName,ff,inh,dataHist,ph):
  global x

  thisFile = TFile(thisFName,"READ")
  w = thisFile.Get("wdiphoton_{}".format(ff))
  #w.Print()

  try:
    th1x = w.var('th1x')
  except AttributeError:
    print("Problem with {}, likely doesn't exits".format(thisFName))
    return 0
  nBins = (len(x)-1)
  th1x.setBins(nBins)

  thisPdf = w.pdf("extDijetPdf") #Name of pdf in workspace
  asimov = thisPdf.generateBinned(RooArgSet(th1x),RooFit.Name('central'),RooFit.Asimov())
  h_th1x = asimov.createHistogram('h_th1x',th1x)

  h_background = convertToMjjHist(h_th1x.Clone())

  #c1 = TCanvas()
  #c1.cd()
  #h_background.Draw("hist")

  for ii in range(h_background.GetNbinsX()):
    inh.SetBinContent(ii,h_background.GetBinContent(ii))
  inh.SetName("{}".format(ff))

  pullplot = dataHist.Clone()
  pullplot.Add(h_background, -1)
 
  for i in range(pullplot.GetNbinsX()):
    if not dataHist.GetBinContent(i+1) == 0:
      pullplot.SetBinContent(i+1, pullplot.GetBinContent(i+1)/dataHist.GetBinError(i+1))
      pullplot.SetBinError(i+1, 1)
    #else:  #Leave this commented out to include 0 bins in pull plot calculation
    #  print(dataHist.GetBinContent(i+1), h_background.GetBinContent(i+1), pullplot.GetBinContent(i+1))
    #  pullplot.SetBinContent(i+1, 0)
    #  pullplot.SetBinError(i+1, 0)

  for ii in range(pullplot.GetNbinsX()):
    ph.SetBinContent(ii,pullplot.GetBinContent(ii))
  ph.SetName("{}_pull".format(ff))

  thisFile.Close()

  return 

def getXA(fl):
  f1 = fl[0]
  for ff in f1.split("/"):
    if (ff[0]=="X" and "A" in ff):
      xa = ff
      break
  return xa

####

def makePlotTogether(flist, anum, function, lA, hA):
  colors = [1,2,3,4,6,7,8]
  canv = TCanvas("c","c",600,700)
  canv.Divide(1,2,0,0,0)

  pad_1 = canv.GetPad(1)
  #PAS
  #pad_1.SetPad(0.01,0.36,0.99,0.98)
  #paper 
  pad_1.SetPad(0.01,0.37,0.99,0.98)
  pad_1.SetLogy()
  pad_1.SetLogx(1)
  pad_1.SetRightMargin(0.05)
  pad_1.SetTopMargin(0.05)
  pad_1.SetLeftMargin(0.175)
  pad_1.SetFillColor(0)
  pad_1.SetBorderMode(0)
  pad_1.SetFrameFillStyle(0)
  pad_1.SetFrameBorderMode(0)

  pad_2 = canv.GetPad(2)
  pad_2.SetLeftMargin(0.175)#0.175
  pad_2.SetPad(0.01,0.02,0.99,0.37)#0.37
  pad_2.SetBottomMargin(0.35)
  pad_2.SetRightMargin(0.05)
  pad_2.SetGridx()
  pad_2.SetGridy()
  pad_2.SetLogx()

  pad_1.cd()
  pad_1.Update()

  leg = TLegend(0.7,0.5,0.94,0.94)
  leg.SetTextFont(42)
  leg.SetFillColor(kWhite)
  leg.SetFillStyle(0)
  leg.SetLineWidth(0)
  leg.SetLineColor(kWhite)

  #####################################################################################
  xa = getXA(flist)

  bkgDir = "../inputs/Shapes_fromGen/alphaBinning/{}/{}/".format(anum,xa)
  #thisFile = os.path.join(bkgDir)+"PLOTS_{}.root".format(anum)
  #if(os.path.exists(thisFile)):
  #  bkgFile = TFile(thisFile)
  #else:
  bkgDir = "../inputs/Shapes_fromGen/alphaBinning/{}/".format(anum)
  for xx in os.listdir(bkgDir):
    nd = os.path.join(bkgDir, xx)
    if(os.path.exists("{}/PLOTS_{}.root".format(nd, anum))):
      bkgFile = TFile("{}/PLOTS_{}.root".format(nd, anum))
      break
  try:
    print(bkgFile)
  except UnboundLocalError:
    print("No background files in alpha slice {}".format(anum))
    return

  #myTH1=bkgFile.Get("data_XM1")
  myTH1=bkgFile.Get("data_XM")
  #myTH1.Rebin(len(x)-1,'data_obs_rebin',x)

  #myRebinnedTH1 = gDirectory.Get('data_obs_rebin')
  myRebinnedTH1 = myTH1.Clone()
  myRebinnedTH1.Scale(1,"width")
  myRebinnedTH1.SetDirectory(0)
  myRealTH1 = convertToTh1xHist(myRebinnedTH1)

  myRebinnedTH1.SetStats(0)
  myRebinnedTH1.SetMarkerStyle(20)
  myRebinnedTH1.SetMarkerSize(0.9)
  myRebinnedTH1.SetLineColor(kBlack)
  myRebinnedTH1_clone = myRebinnedTH1.Clone('myRebinnedTH1_clone')
  myRebinnedTH1_clone.SetMarkerSize(0)
  myRebinnedTH1.GetYaxis().SetTitle('d#sigma/dm_{4#gamma} [pb/TeV]')
  myRebinnedTH1.GetYaxis().SetTitleOffset(1)
  myRebinnedTH1.GetYaxis().SetTitleSize(0.07)
  myRebinnedTH1.GetYaxis().SetLabelSize(0.05)
  myRebinnedTH1.GetXaxis().SetLabelOffset(1000)

  leg.AddEntry(myRebinnedTH1, "Data")

  myRebinnedTH1.Draw("e0")

  l = TLatex()
  l.SetTextAlign(11)
  l.SetTextSize(0.045)
  l.SetTextFont(42)
  l.SetNDC()
  l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi,sqrts/1000.))
  l.SetTextFont(62)
  l.SetTextSize(0.065)
  l.DrawLatex(0.22,0.89,"CMS")
  l.SetTextFont(52)
  l.SetTextSize(0.045)
  l.DrawLatex(0.32,0.89,"Preliminary")

  l.SetTextFont(52)
  l.SetTextSize(0.045)
  l.SetTextColor(kBlue)
  l.DrawLatex(0.22,0.96,"{:.3E} < #alpha < {:.3E}".format(lA,hA))

  l.SetTextFont(52)
  l.SetTextSize(0.065)
  l.SetTextColor(kRed)
  l.DrawLatex(0.32,0.82,"{} Fit".format(function.capitalize()))

  #####################################################################################

  histlist = []
  pulllist = []
  for fil in flist:
    if("Three" in fil): np=3
    elif("Four" in fil): np=4
    elif("Five" in fil): np=5
    elif("Six" in fil): np=6
    th = TH1D("{}".format(np),"{}".format(np),len(x)-1, x)
    ph = TH1D("{}_pull".format(np),"{}_pull".format(np),len(x)-1, x)
    #a=getHistFromWorkspace(hdir,np,th, myRealTH1, ph)
    a=getHistFromWorkspace(fil, function, th, myRebinnedTH1, ph)
    th.SetName(str(np))
    if(a==0): 
      print("Bad fit at {}, skipping".format(np))
      return
    histlist.append(th)
    pulllist.append(ph)

  for (ii,hh) in enumerate(histlist):

    hh.SetStats(0)
    hh.SetLineColor(colors[ii])
    hh.SetLineWidth(2)
    hh.GetYaxis().SetRangeUser(5e-4,20)
  
    leg.AddEntry(hh,"{}".format(hh.GetName()))

    hh.Draw("L histsame")

  leg.Draw("same")

  pad_1.Update()

  #########################
  pad_2.cd()
  for (ii,pp) in enumerate(pulllist):
    pp.SetStats(0)
    pp.SetTitle("")
    pp.SetTitleSize(0)
    pp.GetYaxis().SetRangeUser(-3.5,3.5)
    pp.GetYaxis().SetNdivisions(210,True)
    pp.SetLineWidth(1)
    pp.SetFillColor(colors[ii])
    pp.SetLineColor(colors[ii])
  
    pp.GetYaxis().SetTitleSize(2*0.06)
    pp.GetYaxis().SetLabelSize(2*0.05)
    pp.GetYaxis().SetTitleOffset(0.6)
    pp.GetYaxis().SetTitle('#frac{(Data-Fit)}{Uncertainty}')
  
    pp.GetXaxis().SetTitleSize(2*0.06)
    pp.GetXaxis().SetLabelSize(2*0.05)
    pp.GetXaxis().SetTitle('Average diphoton mass [TeV]')
  
    if(ii==0): 
      pp.SetFillStyle(3001)
      pp.Draw("hist")
    elif(ii==len(pulllist)-1): 
      pp.SetFillStyle(0)
      pp.Draw("histsame")
    else: 
      pp.SetFillStyle(3001+ii)
      pp.Draw("histsame")

  canv.Print("{}fitTogether_alpha{}_{}.png".format(outFolder,anum,function))

for (anum, lA, hA, flist) in dirs:
  makePlotTogether(flist, anum, function, lA, hA)


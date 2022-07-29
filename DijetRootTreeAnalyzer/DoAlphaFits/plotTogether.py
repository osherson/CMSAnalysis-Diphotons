from ROOT import *
from array import *
import numpy as np
import os
import sys

outdir = "./output"
functions = []

dirs = []

if("noshow" in sys.argv):
  gROOT.SetBatch()

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)


for dd in os.listdir(outdir):
  if("alpha" in dd):
    myd = os.path.join(outdir,dd)

    anum = int(myd[myd.rfind("_")+1:])

    rfile=open(os.path.join(myd,"arange.txt"))
    rr = rfile.readline().rstrip()
    lA =float(rr.split(",")[0])
    hA =float(rr.split(",")[-1])

    dirs.append((myd,anum,lA,hA))

    for ff in os.listdir(os.path.join(outdir,dd)):
      if(ff.endswith(".png")):
        fitfunc = ff[ff.find("diphoton_")+9 : ff.find("_2018")]
        if fitfunc not in functions: functions.append(fitfunc)

functions = [functions[0]]
#functions = functions[0:4]
#functions = ["myexp"]

lumi = 13.7 ##Check this
sqrts=np.sqrt(13000)

signal_mjj = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0,515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0,1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0,1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0]

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


def getHistFromWorkspace(thisDir,ff,inh,dataHist,ph):
  global x
  print("{}/DijetFitResults_diphoton_{}_2018.root".format(thisDir,ff))
  thisFile = TFile("{}/DijetFitResults_diphoton_{}_2018.root".format(thisDir,ff))
  w = thisFile.Get("wdiphoton_{}".format(ff))
  #w.Print()

  try:
    th1x = w.var('th1x')
  except AttributeError:
    print("Problem with {}, likely doesn't exits".format(thisDir))
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

  return 

####

def makePlotTogether(hdir, anum, functions, lA, hA):
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
  bkgFile = TFile("../inputs/Shapes_fromGen/alphaBinning/{}/PLOTS_{}.root".format(anum,anum))

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

  #####################################################################################

  histlist = []
  pulllist = []
  for (ii,fit) in enumerate(functions):
    th = TH1D("{}".format(fit),"{}".format(fit),len(x)-1, x)
    ph = TH1D("{}_pull".format(fit),"{}_pull".format(fit),len(x)-1, x)
    #a=getHistFromWorkspace(hdir,fit,th, myRealTH1, ph)
    a=getHistFromWorkspace(hdir,fit,th, myRebinnedTH1, ph)
    if(a==0): return
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
  
    if(ii==0): pp.Draw("hist")
    else: pp.Draw("histsame")

  canv.Print("Plots/fitTogether_{}.png".format(anum,anum))

for (dd,anum,lA,hA) in dirs:
  if(anum != 0): continue
  #if("alpha_2" not in dd): continue
  makePlotTogether(dd,anum,functions,lA,hA)

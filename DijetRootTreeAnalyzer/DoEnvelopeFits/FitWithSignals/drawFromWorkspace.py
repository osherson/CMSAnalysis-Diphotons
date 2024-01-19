import ROOT
import sys,os
import numpy
from array import array
from HelperFuncs import convertToMjjHist, calculateChi2AndFillResiduals, convertToTh1xHist, GetSignalHist

#ROOT.gROOT.SetBatch()
if('q' in sys.argv):
  ROOT.gROOT.SetBatch()

lumi = 138000

signal_mjj = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]
signal_th1x = range(0,115+1)

abin_edges = [0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.00704, 0.00815, 0.03]

signalCoupling = 9
abin = int(sys.argv[1])
sigHistLow = ROOT.TH1D("sigHistLow","sigHistLow;;",len(signal_mjj)-1,array("d",signal_mjj))
sigLow=GetSignalHist(sigHistLow, abin, lumi, signalCoupling,"low")
sigHistLow.SetName(sigLow)

sigHistHigh = ROOT.TH1D("sigHistHigh","sigHistHigh;;",len(signal_mjj)-1,array("d",signal_mjj))
sigHigh=GetSignalHist(sigHistHigh, abin, lumi, signalCoupling,"high")
sigHistHigh.SetName(sigHigh)

fhists = {}

for func in ['dijet','atlas','dipho','moddijet','myexp']:
  tfname = "output/alpha{}/DijetFitResults_diphoton_{}_alpha{}.root".format(abin,func,abin)
  if(not os.path.exists(tfname)): continue
  fil = ROOT.TFile(tfname,"r")
  w = fil.Get("wdiphoton_{}".format(func))

  x = array('d', signal_mjj)
  th1x = w.var('th1x')
  nBins = (len(x)-1)
  th1x.setBins(nBins)

  extDijetPdf = w.pdf("extDijetPdf")
  asimov = extDijetPdf.generateBinned(ROOT.RooArgSet(th1x),ROOT.RooFit.Name('central'),ROOT.RooFit.Asimov())
  h_th1x = asimov.createHistogram('h_th1x_{}'.format(func),th1x)

  h_th1x.Scale(1.0/lumi)
  h_background = convertToMjjHist(h_th1x,x)
  h_background.SetDirectory(0)
  hh = h_background.Clone(func)
  hh.SetDirectory(0)
  
  fhists[func] = hh

bestFuncs = {
  0:"dijet",
  1:"dijet",
  2:"dijet",
  3:"dipho",
  4:"dijet",
  5:"dijet",
  6:"dipho",
  7:"moddijet",
  8:"dijet"
}
bestfunc = bestFuncs[abin]

fil = ROOT.TFile("output/alpha{}/DijetFitResults_diphoton_{}_alpha{}.root".format(abin,bestfunc,abin),"r")
w = fil.Get("wdiphoton_{}".format(bestfunc))
#w.Print()
alphaLowEdge, alphaHiEdge = abin_edges[abin],abin_edges[abin+1]

x = array('d', signal_mjj)
th1x = w.var('th1x')
nBins = (len(x)-1)
th1x.setBins(nBins)

dataHist = w.data("data_obs")
#dataHist.Print('v')

extDijetPdf = w.pdf("extDijetPdf")
asimov = extDijetPdf.generateBinned(ROOT.RooArgSet(th1x),ROOT.RooFit.Name('central'),ROOT.RooFit.Asimov())
h_th1x = asimov.createHistogram('h_th1x',th1x)
h_data_th1x = dataHist.createHistogram('h_data_th1x',th1x)
#c1 = ROOT.TCanvas()
#c1.cd()
#h_data_th1x.Draw("hist")
#c1.Print("tmp.png")

hFile = ROOT.TFile("../../inputs/Shapes_DATA/alphaBinning/{}/DATA.root".format(abin),"r")
myTH1=hFile.Get("data_XM1")
myTH1.Rebin(len(x)-1,'data_obs_rebin',x)
myRebinnedTH1 = ROOT.gDirectory.Get('data_obs_rebin')
myRebinnedTH1.SetDirectory(0)
myRealTH1 = convertToTh1xHist(myRebinnedTH1)

g_data = ROOT.TGraphAsymmErrors(myRebinnedTH1)
alpha = 1-0.6827
for i in range(0,g_data.GetN()):
    N = g_data.GetY()[i]
    binWidth = g_data.GetEXlow()[i] + g_data.GetEXhigh()[i]
    L = 0
    if N!=0:
        L = ROOT.Math.gamma_quantile(alpha/2,N,1.)
    U = ROOT.Math.gamma_quantile_c(alpha/2,N+1,1)

    g_data.SetPointEYlow(i, (N-L)/(binWidth * lumi))
    g_data.SetPointEYhigh(i, (U-N)/(binWidth * lumi))
    g_data.SetPoint(i, g_data.GetX()[i], N/(binWidth * lumi))

h_th1x.Scale(1.0/lumi)
h_background = convertToMjjHist(h_th1x,x)
h_fit_residual_vs_mass = ROOT.TH1D("h_fit_residual_vs_mass","h_fit_residual_vs_mass",len(x)-1,x)
list_chi2AndNdf_background = calculateChi2AndFillResiduals(g_data,h_background,h_fit_residual_vs_mass,bestfunc,lumi,abin)

resids = {}
for ff,fh in fhists.items():
  hfr = ROOT.TH1D("h_fit_residual_vs_mass_{}".format(ff),"h_fit_residual_vs_mass",len(x)-1,x)
  lchi2 = calculateChi2AndFillResiduals(g_data,fh,hfr,ff,lumi,abin)
  resids[ff] = (lchi2,hfr)

canv = ROOT.TCanvas('c','c',600,700)
ROOT.gPad.SetTicky()
canv.Divide(1,2,0,0,0)

pad_1 = canv.GetPad(1)
pad_1.SetPad(0.01,0.30,0.99,0.98)
pad_1.SetTickx()
pad_1.SetTicky()

pad_1.SetRightMargin(0.05)
pad_1.SetTopMargin(0.05)
pad_1.SetLeftMargin(0.175)
pad_1.SetFillColor(0)
pad_1.SetBorderMode(0)
pad_1.SetFrameFillStyle(0)
pad_1.SetFrameBorderMode(0)

pad_2 = canv.GetPad(2)
pad_2.SetLeftMargin(0.175)#0.175
pad_2.SetPad(0.01,0.02,0.99,0.30)#0.37
pad_2.SetTickx()
pad_2.SetTicky()
pad_2.SetBottomMargin(0.35)
pad_2.SetRightMargin(0.05)

pad_1.SetLogx(1)
pad_2.SetLogx(1)

pad_1.cd()
myRebinnedDensityTH1 = myRebinnedTH1.Clone('data_obs_density')
for i in range(1,nBins+1):
    myRebinnedDensityTH1.SetBinContent(i, myRebinnedTH1.GetBinContent(i)/ myRebinnedTH1.GetBinWidth(i))
    myRebinnedDensityTH1.SetBinError(i, myRebinnedTH1.GetBinError(i)/ myRebinnedTH1.GetBinWidth(i))

xRangeMax = w.var('mjj').getMax()
myRebinnedDensityTH1.GetXaxis().SetRangeUser(w.var('mjj').getMin(),xRangeMax)
# paper:
myRebinnedDensityTH1.GetYaxis().SetTitle('d#sigma/dm_{#Gamma#Gamma} [pb/GeV]')
# PAS:
#myRebinnedDensityTH1.GetYaxis().SetTitle('d#sigma / dm_{jj} [pb / GeV]')
myRebinnedDensityTH1.GetYaxis().SetTitleOffset(1)
myRebinnedDensityTH1.GetYaxis().SetTitleSize(0.07)
myRebinnedDensityTH1.GetYaxis().SetLabelSize(0.050)
myRebinnedDensityTH1.GetXaxis().SetLabelOffset(1000)
myRebinnedDensityTH1.SetStats(0)
myRebinnedDensityTH1.Scale(0)
myRebinnedDensityTH1.SetLineColor(ROOT.kWhite)
myRebinnedDensityTH1.SetMarkerColor(ROOT.kWhite)
myRebinnedDensityTH1.SetLineWidth(0)

g_data.SetMarkerStyle(20)
g_data.SetMarkerSize(0.9)
g_data.SetLineColor(ROOT.kBlack)
g_data_clone = g_data.Clone('g_data_clone')
g_data_clone.SetMarkerSize(0)

#linear
#FIXME: Make this smarter
if(abin == 8):
  myRebinnedDensityTH1.SetMaximum(1e-5)
elif(abin == 6):
  myRebinnedDensityTH1.SetMaximum(9e-6)
else:
  myRebinnedDensityTH1.SetMaximum(8.5e-6)

#Looks prettier:
myRebinnedDensityTH1.SetMinimum(1e-7)#2e-8
#Shows errors in empty bins:
#myRebinnedDensityTH1.SetMinimum(0)#2e-8

#ROOT.gPad.SetLogy() 
myRebinnedDensityTH1.Draw("axis")

l = ROOT.TLatex()
l.SetTextAlign(11)
l.SetTextSize(0.045)
l.SetTextFont(42)
l.SetNDC()
#l.DrawLatex(0.7,0.96,"%i pb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
l.DrawLatex(0.70,0.96,"138 fb^{-1} (%i TeV)"%(w.var('sqrts').getVal()/1000.))
#l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
# paper
l.SetTextFont(62)
l.SetTextSize(0.065)
l.DrawLatex(0.22,0.88,"CMS")
l.SetTextFont(52)
l.SetTextSize(0.045)
#l.DrawLatex(0.31,0.89,"Preliminary")

l.SetTextFont(42)
l.SetTextSize(0.055)
l.SetTextColor(14)
#l.DrawLatex(0.19,0.84,"%s#leq #alpha^{reco}<%s"%(alphaLowEdge, alphaHiEdge)) #Upper left
l.SetTextColor(ROOT.kBlack)
alpct = '{:.2f}'.format(alphaLowEdge*100)
ahpct = '{:.2f}%'.format(alphaHiEdge*100)
l.DrawLatex(0.55,0.88,"%s < #alpha^{reco} < %s"%(alpct,ahpct)) #Upper right

leg_x1 = 0.31
leg_y1 = 0.5
leg_height =  0.34
#leg = ROOT.TLegend(leg_x1,leg_y1,0.5,leg_y1+leg_height) #Big legend, all functions
leg = ROOT.TLegend(leg_x1,0.69,0.5,0.85) #Big legend, all functions
leg.SetTextFont(42)
leg.SetFillColor(ROOT.kWhite)
leg.SetFillStyle(0)
leg.SetLineWidth(0)
leg.SetTextSize(0.050)
leg.SetLineColor(ROOT.kWhite)
leg.AddEntry(g_data,"Data","pe")
#leg.AddEntry(background,"{} Fit".format(fitfunc),"l")
leg.Draw("F")

lsig = ROOT.TLatex()
lsig.SetTextAlign(11)
lsig.SetTextSize(0.050)
lsig.SetTextFont(42)
lsig.SetNDC()
lsig.DrawLatex(0.62,0.80,"X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)")
lsig.DrawLatex(0.65,0.75,"(m_{X}N)/f = 1/%i"%signalCoupling)

leg2 = ROOT.TLegend(0.58,0.56,0.91,0.71)
leg2.SetTextSize(0.050)
leg2.SetTextFont(42)
leg2.SetFillColor(ROOT.kWhite)
leg2.SetFillStyle(0)
leg2.SetLineWidth(0)
leg2.SetLineColor(ROOT.kWhite)
leg2.Draw()

leg3 = ROOT.TLegend(0.58,0.41,0.91,0.55)
leg3.SetTextSize(0.045)
leg3.SetTextFont(42)
leg3.SetFillColor(ROOT.kWhite)
leg3.SetFillStyle(0)
leg3.SetLineWidth(0)
leg3.SetLineColor(ROOT.kWhite)
leg3.Draw()

pave_param = ROOT.TPaveText(0.55,0.03,0.9,0.25,"NDC")
pave_param.SetTextFont(42)
pave_param.SetFillColor(0)
pave_param.SetBorderSize(0)
pave_param.SetFillStyle(0)
pave_param.SetTextAlign(11)
pave_param.SetTextSize(0.045)


lstyles={
  "dijet":2,
  "atlas":4,
  "moddijet":7,
  "dipho":9,
  "myexp":10}

lcolors={
  "dijet":2,
  "atlas":4,
  "moddijet":6,
  "dipho":8,
  "myexp":30}

ltitles={
  "dijet":"Dijet Fit",
  "atlas":"PowExp Fit",
  "moddijet":"ModDijet Fit",
  "dipho":"Diphoton Fit",
  "myexp":"Power-Law Fit"}

drawO = ['dijet','atlas','moddijet','dipho','myexp']
drawOrder = [bestfunc]
#for do in drawO:
#  if(do) not in drawOrder: drawOrder.append(do)

blank1 = ROOT.TH1D("b1","",1,0,1)
blank1.SetLineColor(ROOT.kWhite)
blank1.SetLineWidth(0)
blank1.SetMarkerSize(0)
blank1.SetMarkerColor(ROOT.kWhite)
#leg.AddEntry(blank1, "")

ll = ROOT.TLatex()
ll.SetTextAlign(11)
ll.SetTextSize(0.045)
ll.SetTextFont(42)
ll.SetNDC()
#ll.SetTextSize(leg.GetTextSize())
#l.SetTextColor(12)
#ll.DrawLatex(leg_x1 + 0.01, 0.755,"Functional Fit: ")

for ff in drawOrder:
  if(ff not in fhists.keys()): continue
  fhist = fhists[ff]

  fhist.SetLineStyle(lstyles[ff])
  if(ff == bestfunc):
    fhist.SetLineStyle(1)
  else:
    fhist.SetLineStyle(lstyles[ff])
  fhist.SetLineColor(ROOT.kRed)

  leg.AddEntry(fhist, ltitles[ff])

  fhist.Draw("histsame")

#Drawing this for power function
g_data_clone.Draw("zpsame")
g_data.Draw("zpsame")

phimLow = {
   0:"2",
   1:"2",
   2:"2",
   3:"2",
   4:"2",
   5:"2",
   6:"2.4",
   7:"2.8",
   8:"10",
}

phimHigh = {
   0:"6",
   1:"6",
   2:"6",
   3:"6",
   4:"6",
   5:"6",
   6:"8.4",
   7:"8.4",
   8:"30",
}
divisorsLow = {
   0:20,
   1:40,
   2:40,
   3:100,
   4:150,
   5:100,
   6:250,
   7:300,
   8:400,
}
divisorsHigh = {
   0:2, ########Special this is * 2
   1:1,
   2:1,
   3:2,
   4:5,
   5:2,
   6:5,
   7:5,
   8:5,
}

leg2.AddEntry(sigHistLow, "m_{X} = 400 GeV","f")
#leg2.AddEntry(blank1, "m_{X} = 400 GeV")
leg2.AddEntry(blank1,"m_{\phi} = %s GeV"%(phimLow[abin]))
#leg2.AddEntry(blank1,"(m_{X}N)/f = 1/ %i"%signalCoupling)
leg2.AddEntry(blank1,"#sigma = #sigma_{theory} / %i"%(divisorsLow[abin]))

#leg3.AddEntry(sigHistHigh,"X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)")
leg3.AddEntry(sigHistHigh, "m_{X} = 1200 GeV","f")
leg3.AddEntry(blank1,"m_{\phi} = %s GeV"%(phimHigh[abin]))
#leg3.AddEntry(blank1,"(m_{X}N)/f = 1/ %i"%signalCoupling)
#leg3.AddEntry(blank1,"#sigma = 0.05 fb")
#leg3.AddEntry(blank1,"#sigma = #sigma_{theory}")
if(abin==0):
  leg3.AddEntry(blank1,"#sigma = #sigma_{theory} #times %i"%(divisorsHigh[abin]))
if(divisorsHigh[abin]==1 and abin != 0):
  leg3.AddEntry(blank1,"#sigma = #sigma_{theory}")
elif(abin != 0):
  leg3.AddEntry(blank1,"#sigma = #sigma_{theory} / %i"%(divisorsHigh[abin]))

#Scale up low mass signals
if(abin==0):
  sigHistLow.Scale(1e9*sigHistLow.Integral())
  sigHistHigh.Scale(1e9*sigHistHigh.Integral())
elif(abin==1):
  sigHistLow.Scale(5e7*sigHistLow.Integral())
  sigHistHigh.Scale(5e7*sigHistHigh.Integral())
sigHistLow.Draw("histsame")
sigHistHigh.Draw("histsame")

zeroline = ROOT.TLine(0,0,signal_mjj[-1],0)
zeroline.SetLineColor(ROOT.kBlack)
zeroline.Draw("same")

pad_1.Update()

pad_2.cd()

for (ff,(lr,resid)) in resids.items():
  if(ff != bestfunc): continue

  resid.GetXaxis().SetRangeUser(w.var('mjj').getMin(),xRangeMax)
  #resid.GetYaxis().SetRangeUser(-3.5,3.5)
  pullrange = 2.75
  resid.GetYaxis().SetRangeUser(-1*pullrange,pullrange)
  resid.GetYaxis().SetNdivisions(210,True)
  resid.SetLineWidth(1)
  #resid.SetFillColor(lcolors[ff])
  #resid.SetFillColorAlpha(lcolors[ff],0.6)
  #resid.SetFillStyle(3001)
  resid.SetFillColor(ROOT.kRed)

  resid.SetLineColor(ROOT.kBlack)

  resid.GetYaxis().SetTitleSize(2*0.065)
  resid.GetYaxis().SetLabelSize(2*0.06)
  # paper
  resid.GetYaxis().SetTitleOffset(0.6)
  resid.GetYaxis().SetTitle('#frac{(Data-Fit)}{Uncertainty}')

  resid.GetXaxis().SetTitleSize(2*0.08)
  resid.GetXaxis().SetLabelSize(2*0.05)
  # paper
  resid.GetXaxis().SetTitle('m_{#Gamma#Gamma} [GeV]')
  resid.SetTitle("")
  resid.SetStats(0)

  resid.Draw("histsame")

  resid.GetXaxis().SetLabelOffset(1000)
  resid.GetXaxis().SetNoExponent()
  resid.GetXaxis().SetMoreLogLabels()  
  resid.GetXaxis().SetNdivisions(510)

def getSigPull(hist, dgraph):
  phist = hist.Clone()

  for bb in range(1,phist.GetNbinsX()):
    bdata = signal_mjj.index(phist.GetBinLowEdge(bb))
    value_data = dgraph.GetY()[bdata]
    err_low_data = dgraph.GetEYlow()[bdata]
    err_high_data = dgraph.GetEYhigh()[bdata]
    value_sig = phist.GetBinContent(bb)
    
    ## Fit residuals
    err_tot_data = 0
    if (value_sig > value_data):
        err_tot_data = err_high_data
    else:
        err_tot_data = err_low_data
    ###
    if err_tot_data==0:
      err_tot_data = 0.0000001 

    newC = value_sig/err_tot_data
    #print(bdata, signal_mjj[bdata], phist.GetBinLowEdge(bb), err_tot_data, value_sig, newC)
    phist.SetBinContent(bb,newC)

  phist.SetBinContent(1,0)
  return phist

#Signals on pull
sigPullLow = getSigPull(sigHistLow,g_data)
sigPullHigh = getSigPull(sigHistHigh,g_data)
sigPullLow.Draw("histsame")
sigPullHigh.Draw("histsame")

zeroline.Draw("same")

xLab = ROOT.TLatex()
xLab.SetTextAlign(22)
xLab.SetTextFont(42)
xLab.SetTextSize(2*0.057)

xLab.DrawLatex(300, -1*pullrange*1.2, "300")
xLab.DrawLatex(400, -1*pullrange*1.2, "400")
xLab.DrawLatex(600, -1*pullrange*1.2, "600")
xLab.DrawLatex(1000, -1*pullrange*1.2, "1000")
#xLab.DrawLatex(1500, -1*pullrange*1.2, "1500")
xLab.DrawLatex(2000, -1*pullrange*1.2, "2000")
xLab.DrawLatex(3000, -1*pullrange*1.2, "3000")

f_h2_log10_x_axis = ROOT.TF1("f_h2_log10_x_axis", "log10(x)", h_fit_residual_vs_mass.GetXaxis().GetXmin(), h_fit_residual_vs_mass.GetXaxis().GetXmax())
a = ROOT.TGaxis(h_fit_residual_vs_mass.GetXaxis().GetXmin(), -pullrange,
              h_fit_residual_vs_mass.GetXaxis().GetXmax(), -pullrange, "f_h2_log10_x_axis", 509, "BS", 0.0)
a.SetTickSize(h_fit_residual_vs_mass.GetTickLength("X"))
a.SetMoreLogLabels()
a.SetLabelOffset(1000)
#a.Draw()

cl = ROOT.TLatex()
cl.SetTextFont(42)
cl.SetTextSize(0.11)
cl.SetTextAlign(11)
cl.SetNDC()
cl.DrawLatex(0.50, 0.54, "#chi^{{2}} / NDF = {0:.2f} / {1:d} = {2:.2f}".format(
                             list_chi2AndNdf_background[4], list_chi2AndNdf_background[5],
                              list_chi2AndNdf_background[4]/list_chi2AndNdf_background[5]))

ROOT.gPad.Modified()
ROOT.gPad.Update()

canv.Print("Plots/fit_abin{}.png".format(abin))
canv.Print("Plots/fit_abin{}.pdf".format(abin))
canv.Print("Plots/fit_abin{}.C".format(abin))
#canv.Print("Plots/zeroErrors/fit_abin{}.png".format(abin))
#canv.Print("Plots/zeroErrors/fit_abin{}.pdf".format(abin))
#canv.Print("Plots/zeroErrors/fit_abin{}.C".format(abin))

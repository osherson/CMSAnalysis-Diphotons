import ROOT
import os
import numpy

signal_mjj = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

def convertToMjjHist(hist_th1x,x):

    hist = ROOT.TH1D(hist_th1x.GetName()+'_mjj',hist_th1x.GetName()+'_mjj',len(x)-1,x)
    for i in range(1,hist_th1x.GetNbinsX()+1):
        hist.SetBinContent(i,hist_th1x.GetBinContent(i)/(x[i]-x[i-1]))
        hist.SetBinError(i,hist_th1x.GetBinError(i)/(x[i]-x[i-1]))

    return hist

def convertToTh1xHist(hist):

    hist_th1x = ROOT.TH1D(hist.GetName()+'_th1x',hist.GetName()+'_th1x',hist.GetNbinsX(),0,hist.GetNbinsX())
    for i in range(1,hist.GetNbinsX()+1):
        hist_th1x.SetBinContent(i,hist.GetBinContent(i))
        hist_th1x.SetBinError(i,hist.GetBinError(i))

    return hist_th1x

def calculateChi2AndFillResiduals(data_obs_TGraph_,background_hist_,hist_fit_residual_vsMass_,funcName_,lumi,abin):
    
    tfname = "output/alpha{}/DijetFitResults_diphoton_{}_alpha{}.root".format(abin,funcName_,abin)
    if(not os.path.exists(tfname)): 
      print("Bad funcName_tion: {}".format(tfname))
      return
    fil = ROOT.TFile(tfname,"r")
    workspace_ = fil.Get("wdiphoton_{}".format(funcName_))
    
    N_massBins_ = data_obs_TGraph_.GetN()
    MinNumEvents = 10
    nParFit = 3

    box = 'diphoton_%s'%(funcName_)

    if workspace_.var('meff_%s'%box).getVal()>0 and workspace_.var('seff_%s'%box).getVal()>0 :
        nParFit = 6
    if workspace_.var('p54_%s'%box) != None or workspace_.var('pm4_%s'%box) != None or workspace_.var('pa4_%s'%box) != None :
       # if workspace_.var('pm4_%s'%box) != None and workspace_.var('pm4_%s'%box).getVal()==0:
           # nParFit = 4
        if workspace_.var('pm4_%s'%box) != None and workspace_.var('pm4_%s'%box).getVal()==0 and workspace_.var('pm3_%s'%box) != None and workspace_.var('pm3_%s'%box).getVal()==0 and workspace_.var('p2_%s'%box) != None and workspace_.var('p2_%s'%box).getVal()==0:
            nParFit = 2
        elif workspace_.var('pm4_%s'%box) != None and workspace_.var('pm4_%s'%box).getVal()==0 and workspace_.var('pm3_%s'%box) != None and workspace_.var('pm3_%s'%box).getVal()==0:
            nParFit = 3
        elif workspace_.var('pm4_%s'%box) != None and workspace_.var('pm4_%s'%box).getVal()==0:
            nParFit = 4
        else:
            nParFit = 5

    chi2_FullRangeAll = 0
    chi2_PlotRangeAll = 0
    chi2_PlotRangeNonZero = 0
    chi2_PlotRangeMinNumEvents = 0 

    N_FullRangeAll = 0
    N_PlotRangeAll = 0
    N_PlotRangeNonZero = 0
    N_PlotRangeMinNumEvents = 0

    for bin in range (0,N_massBins_):
        ## Values and errors
        value_data = data_obs_TGraph_.GetY()[bin]
        err_low_data = data_obs_TGraph_.GetEYlow()[bin]
        err_high_data = data_obs_TGraph_.GetEYhigh()[bin]
        xbinCenter = data_obs_TGraph_.GetX()[bin] 
        xbinLow = data_obs_TGraph_.GetX()[bin]-data_obs_TGraph_.GetEXlow()[bin] 
        xbinHigh = data_obs_TGraph_.GetX()[bin]+data_obs_TGraph_.GetEXhigh()[bin]
        binWidth_current = xbinHigh - xbinLow
        #value_fit = background_.Integral(xbinLow , xbinHigh) / binWidth_current
        value_fit = background_hist_.GetBinContent(bin+1)
        
        ## Fit residuals
        err_tot_data = 0
        if (value_fit > value_data):
            err_tot_data = err_high_data  
        else:
            err_tot_data = err_low_data
        ###
        #These lines were commented, steven uncommented
        if err_tot_data==0:
          err_tot_data = 0.0000001	#when we have infinite denominator in pulls
          #errl = 0
          #errh = 1.8/(binWidth_current * (lumi/1000))
          #print("errh: {}".format(errh))
          #if (value_data - value_fit > 0):
          #  err_tot_data = errl
          #else:
          #  err_tot_data = errh
        ###
        plotRegion = 'Full'
        plotRegions = plotRegion.split(',')
        checkInRegions = [xbinCenter>workspace_.var('mjj').getMin(reg) and xbinCenter<workspace_.var('mjj').getMax(reg) for reg in plotRegions]
        if any(checkInRegions):
            fit_residual = (value_data - value_fit) / err_tot_data
            err_fit_residual = 1
        else:
            fit_residual = 0
            err_fit_residual = 0

        ## Fill histo with residuals

        hist_fit_residual_vsMass_.SetBinContent(bin+1,fit_residual)
        hist_fit_residual_vsMass_.SetBinError(bin+1,err_fit_residual)

        ## Chi2

        chi2_FullRangeAll += pow(fit_residual,2)
        N_FullRangeAll += 1        
        plotRegions = plotRegion.split(',')
        checkInRegions = [xbinCenter>workspace_.var('mjj').getMin(reg) and xbinCenter<workspace_.var('mjj').getMax(reg) for reg in plotRegions]
        if any(checkInRegions):
            #print '%i: obs %.0f, exp %.2f, chi2 %.2f'%(bin, value_data* binWidth_current * lumi, value_fit* binWidth_current * lumi, pow(fit_residual,2))
            chi2_PlotRangeAll += pow(fit_residual,2)
            N_PlotRangeAll += 1
            if (value_data > 0):
                chi2_PlotRangeNonZero += pow(fit_residual,2)
                N_PlotRangeNonZero += 1
                if(value_data * binWidth_current * lumi > MinNumEvents):
                    chi2_PlotRangeMinNumEvents += pow(fit_residual,2)
                    N_PlotRangeMinNumEvents += 1
    
    #==================
    # Calculate chi2/ndf
    #==================

    # ndf
    ndf_FullRangeAll = N_FullRangeAll - nParFit    
    ndf_PlotRangeAll = N_PlotRangeAll - nParFit    
    ndf_PlotRangeNonZero = N_PlotRangeNonZero - nParFit    
    ndf_PlotRangeMinNumEvents = N_PlotRangeMinNumEvents - nParFit    


    chi2_ndf_FullRangeAll = chi2_FullRangeAll / ndf_FullRangeAll
    chi2_ndf_PlotRangeAll = chi2_PlotRangeAll / ndf_PlotRangeAll
    chi2_ndf_PlotRangeNonZero = chi2_PlotRangeNonZero / ndf_PlotRangeNonZero
    try:
      chi2_ndf_PlotRangeMinNumEvents = chi2_PlotRangeMinNumEvents / ndf_PlotRangeMinNumEvents
    except ZeroDivisionError:
      print("Zero division error")
      chi2_ndf_PlotRangeMinNumEvents = 9999.

    return [chi2_FullRangeAll, ndf_FullRangeAll, chi2_PlotRangeAll, ndf_PlotRangeAll, chi2_PlotRangeNonZero, ndf_PlotRangeNonZero, chi2_PlotRangeMinNumEvents, ndf_PlotRangeMinNumEvents]

def GetTH(fN):
  TH = ROOT.TGraph()
  TH.SetPoint(TH.GetN(),100., 335515./fN/fN)
  TH.SetPoint(TH.GetN(),150., 69155./fN/fN)
  TH.SetPoint(TH.GetN(),200., 21362.1/fN/fN)
  TH.SetPoint(TH.GetN(),250., 8304.88/fN/fN)
  TH.SetPoint(TH.GetN(),300., 3746.96/fN/fN)
  TH.SetPoint(TH.GetN(),350., 1878.15/fN/fN)
  TH.SetPoint(TH.GetN(),400., 1017.87/fN/fN)
  TH.SetPoint(TH.GetN(),450., 585.983/fN/fN)
  TH.SetPoint(TH.GetN(),500., 353.898/fN/fN)
  TH.SetPoint(TH.GetN(),625., 117.508/fN/fN)
  TH.SetPoint(TH.GetN(),750., 45.9397/fN/fN)
  TH.SetPoint(TH.GetN(),875., 20.1308/fN/fN)
  TH.SetPoint(TH.GetN(),1000., 9.59447/fN/fN)
  TH.SetPoint(TH.GetN(),1125., 4.88278/fN/fN)
  TH.SetPoint(TH.GetN(),1250., 2.61745/fN/fN)
  TH.SetPoint(TH.GetN(),1375., 1.46371/fN/fN)
  TH.SetPoint(TH.GetN(),1500., 0.847454/fN/fN)
  TH.SetPoint(TH.GetN(),1625., 0.505322/fN/fN)
  TH.SetPoint(TH.GetN(),1750., 0.309008/fN/fN)
  TH.SetPoint(TH.GetN(),1875., 0.192939/fN/fN)
  TH.SetPoint(TH.GetN(),2000., 0.122826/fN/fN)
  TH.SetPoint(TH.GetN(),2125., 0.0795248/fN/fN)
  TH.SetPoint(TH.GetN(),2250., 0.0522742/fN/fN)
  TH.SetPoint(TH.GetN(),2375., 0.0348093/fN/fN)
  TH.SetPoint(TH.GetN(),2500., 0.0235639/fN/fN)
  TH.SetPoint(TH.GetN(),2625., 0.0161926/fN/fN)
  TH.SetPoint(TH.GetN(),2750., 0.0109283/fN/fN)
  TH.SetPoint(TH.GetN(),2875., 0.00759881/fN/fN)
  TH.SetPoint(TH.GetN(),3000., 0.00531361/fN/fN)
  return TH


def getScale(onesig,abin,thval,lumi,hilo):
  th9 = GetTH(thval)
  xmass = int(onesig[1:onesig.find("A")])
  txs = th9.Eval(xmass)
  if(hilo=="low"):
    if(abin ==0): txs = txs/20
    elif(abin ==1): txs = txs/40
    elif(abin ==2): txs = txs/40
    elif(abin ==3): txs = txs/100
    elif(abin ==4): txs = txs/150
    elif(abin ==5): txs = txs/100
    elif(abin ==6): txs = txs/250
    elif(abin ==7): txs = txs/300
    elif(abin ==8): txs = txs/400
  if(hilo=="high"):
    if(abin ==0): txs = txs*2
    elif(abin ==1): txs = txs/1
    elif(abin ==2): txs = txs/1
    elif(abin ==3): txs = txs/2
    elif(abin ==4): txs = txs/5
    elif(abin ==5): txs = txs/2
    elif(abin ==6): txs = txs/5
    elif(abin ==7): txs = txs/5
    elif(abin ==8): txs = txs/5

  effFile = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/{}/{}/{}.txt".format(abin,onesig,onesig)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())

  sc = txs * eff * (lumi/1000) # [=] N Events
  #print("N Events: {}".format(sc))
  sc = sc / lumi # [=] Events * pb
  #print("Events per inverse pb: {}".format(sc))
  return sc

def getScaleXS(onesig,abin,thval,lumi,hilo):
  if(hilo=="high"):
    txs = 0.05
  else:
    txs = 5

  effFile = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/{}/{}/{}.txt".format(abin,onesig,onesig)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())

  sc = txs * eff * (lumi/1000) # [=] N Events
  #print("N Events: {}".format(sc))
  sc = sc / lumi # [=] Events * pb
  #print("Events per inverse pb: {}".format(sc))
  return sc

def formatSigHist(sigHist, scale, hilo):

  aval=1.0
  if(hilo=="low"):
    sigHist.SetFillColorAlpha(4,aval)
    sigHist.SetLineColorAlpha(4,aval)
  else:
    sigHist.SetFillColorAlpha(6,aval)
    sigHist.SetLineColorAlpha(6,aval)
  sigHist.SetFillStyle(3002)
  sigHist.SetLineWidth(1)
  sigHist.Scale(1,"width")
  sigHist.Scale(scale/sigHist.Integral())

  #Truncate histogram to only include bins around the peak
  mean = sigHist.GetMean()
  for (idx,ee) in enumerate(signal_mjj):
    if(ee>mean): 
      myidx = idx
      mybin = ee

  relbins = signal_mjj[myidx-7:myidx+5]
  sigTrunc = ROOT.TH1D(sigHist.GetName()+"_t","",len(relbins)-1,numpy.array(relbins))
  for bb in range(sigTrunc.GetNbinsX()):
    bs = sigHist.FindBin(sigTrunc.GetBinLowEdge(bb))
    sigTrunc.SetBinContent(bb+1,sigHist.GetBinContent(bs))

  return sigTrunc.Clone()

def GetSignalHist(newHist, abin, lumi, coupling,hilo):
  if(hilo=="high"):
    signalDict = {
      0:"X1200A6",
      1:"X1200A6",
      2:"X1200A6",
      3:"X1200A6",
      4:"X1200A6",
      5:"X1200A6",
      6: "X1200A8p4",
      7:"X1200A8p4",
      8:"X1200A30",
    }
  else:
    signalDict = {
      0:"X400A2",
      1:"X400A2",
      2:"X400A2",
      3:"X400A2",
      4:"X400A2",
      5:"X400A2",
      6:"X400A2p4",
      7:"X400A2p8",
      8:"X400A10",
    }

  intDir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"

  sig = signalDict[abin]
  sDir = intDir + str(abin) + "/" + sig

  sFile = ROOT.TFile("{}/PLOTS_{}.root".format(sDir,abin), "READ")
  sXs = sFile.Get("{}_XM".format(sig))
  sXs.SetDirectory(0)
  scaleXs = getScale(sig,abin,coupling,lumi,hilo)

  for nx in range(sXs.GetNbinsX()):
    newHist.SetBinContent(nx, sXs.GetBinContent(nx))
  newHist = formatSigHist(newHist, scaleXs, hilo)
  
  return sig


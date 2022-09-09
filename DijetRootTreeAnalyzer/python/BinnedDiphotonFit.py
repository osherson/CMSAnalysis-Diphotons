from optparse import OptionParser
import ROOT as rt
import rootTools
from framework import Config
from array import *
from itertools import *
from operator import *
#from WriteDataCard_4J import initializeWorkspace,convertToTh1xHist,convertToMjjHist,applyTurnonFunc,applyTurnonGraph
#from WriteDataCard_photons import initializeWorkspace,convertToTh1xHist,convertToMjjHist,applyTurnonFunc,applyTurnonGraph
from WriteDataCard_photons_envelope import initializeWorkspace,convertToTh1xHist,convertToMjjHist,applyTurnonFunc,applyTurnonGraph
import os
import random
import sys
import math
import numpy
import time

densityCorr = False

def binnedFit(pdf, data, fitRange='Full', useWeight=False):

    if useWeight:
        fr = pdf.fitTo(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.SumW2Error(True),rt.RooFit.Save(),rt.RooFit.Minimizer('Minuit2','migrad'),rt.RooFit.Strategy(2))
        #fr = pdf.fitTo(data,rt.RooFit.Range('1,5'),rt.RooFit.Extended(True),rt.RooFit.SumW2Error(True),rt.RooFit.Save(),rt.RooFit.Minimizer('Minuit2','migrad'),rt.RooFit.Strategy(2))
        migrad_status = fr.status()
        hesse_status = -1
    else:
        print(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.Offset(True))
        nll = pdf.createNLL(data,rt.RooFit.Range(fitRange),rt.RooFit.Extended(True),rt.RooFit.Offset(True))
        m2 = rt.RooMinimizer(nll)
        m2.setStrategy(2)
        m2.setMaxFunctionCalls(100000)
        m2.setMaxIterations(100000)
        migrad_status = m2.minimize('Minuit2','migrad')
        improve_status = m2.minimize('Minuit2','improve')
        hesse_status = m2.minimize('Minuit2','hesse')
        minos_status = m2.minos()
        if hesse_status != 3 :
            hesse_status = m2.minimize('Minuit2','hesse')
        fr = m2.save()
    
    return fr


def MakeNBinsFromMinToMax(N,Min,Max):
    BINS = []
    for i in range(N+1):
        BINS.append(Min+(i*(Max-Min)/N))
    return numpy.array(BINS)

def convertSideband(name,w,x):
    if name=="Full":
        return "Full"
    names = name.split(',')
    nBins = (len(x)-1)
    iBinX = -1
    sidebandBins = []
    for ix in range(1,len(x)):
        iBinX+=1
        w.var('mjj').setVal((x[ix]+x[ix-1])/2.)
        inSideband = 0
        for fitname in names:
            inSideband += ( w.var('mjj').inRange(fitname) )
        if inSideband: sidebandBins.append(iBinX)

    sidebandGroups = []
    for k, g in groupby(enumerate(sidebandBins), lambda (i,x):i-x):
        consecutiveBins = map(itemgetter(1), g)
        sidebandGroups.append([consecutiveBins[0],consecutiveBins[-1]+1])
        
    newsidebands = ''
    nameNoComma = name.replace(',','')
        
    for iSideband, sidebandGroup in enumerate(sidebandGroups):
        if not w.var('th1x').hasRange('%s%i'%(nameNoComma,iSideband)):
            w.var('th1x').setRange("%s%i"%(nameNoComma,iSideband),sidebandGroup[0],sidebandGroup[1])
        newsidebands+='%s%i,'%(nameNoComma,iSideband)
    newsidebands = newsidebands[:-1]
    return newsidebands

def convertFunctionToHisto(background_,name_,N_massBins_,massBins_):

    background_hist_ = rt.TH1D(name_,name_,N_massBins_,massBins_)

    for bin in range (0,N_massBins_):
        xbinLow = massBins_[bin]
        xbinHigh = massBins_[bin+1]
        binWidth_current = xbinHigh - xbinLow
        value = background_.Integral(xbinLow , xbinHigh) / binWidth_current
        background_hist_.SetBinContent(bin+1,value)

    return background_hist_

def calculateChi2AndFillResiduals(data_obs_TGraph_,background_hist_,hist_fit_residual_vsMass_,workspace_,prinToScreen_=0,effFit_=False):
    
    N_massBins_ = data_obs_TGraph_.GetN()
    MinNumEvents = 10
    #MinNumEvents = 1
    nParFit = 4
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


    print nParFit

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
          print("Manually setting error")
          err_tot_data = 0.0000001	#when we have infinite denominator in pulls
        ###
        print 'error = ', err_tot_data     
        plotRegions = plotRegion.split(',')
        checkInRegions = [xbinCenter>workspace_.var('mjj').getMin(reg) and xbinCenter<workspace_.var('mjj').getMax(reg) for reg in plotRegions]
        if effFit_: checkInRegions = [xbinCenter>workspace_.var('mjj').getMin('Eff') and xbinCenter<workspace_.var('mjj').getMax('Eff')]
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
        if effFit_: checkInRegions = [xbinCenter>workspace_.var('mjj').getMin('Eff') and xbinCenter<workspace_.var('mjj').getMax('Eff')]
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


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-c','--config',dest="config",type="string",default="config/run2.config",
                  help="Name of the config file to use")
    parser.add_option('-d','--dir',dest="outDir",default="./",type="string",
                  help="Output directory to store cards")
    parser.add_option('-l','--lumi',dest="lumi", default=1.,type="float",
                  help="integrated luminosity in pb^-1")
    parser.add_option('-y','--year',dest="year", default=2018,type="string",
                  help="run II year")
    parser.add_option('--run-min',dest="runMin", default=0,type="int",
                  help="minimum run to consider for trigger efficiency")
    parser.add_option('--run-max',dest="runMax", default=999999,type="int",
                  help="maximum run to consider for trigger efficiency")
    parser.add_option('-b','--box',dest="box", default="CaloDijet",type="string",
                  help="box name")
    parser.add_option('--no-fit',dest="noFit",default=False,action='store_true',
                  help="Turn off fit (useful for visualizing initial parameters)")
    parser.add_option('--fit-region',dest="fitRegion",default="Full",type="string",
                  help="Fit region")
    parser.add_option('--plot-region',dest="plotRegion",default="Full",type="string",
                  help="Plot region")
    parser.add_option('-i','--input-fit-file',dest="inputFitFile", default=None,type="string",
                  help="input fit file")
    parser.add_option('-w','--weight',dest="useWeight",default=False,action='store_true',
                  help="use weight")
    parser.add_option('-s','--signal',dest="signalFileName", default=None,type="string",
                  help="input dataset file for signal pdf")
    parser.add_option('-m','--model',dest="model", default="gg",type="string",
                  help="signal model")
    parser.add_option('--mass',dest="mass", default="750",type="string",
                  help="mgluino")
    parser.add_option('--xsec',dest="xsec", default="1",type="string",
                  help="cross section in pb")
    parser.add_option('-t','--trigger',dest="triggerDataFile", default=None,type="string",
                  help="trigger data file")
    parser.add_option('--l1',dest="l1Trigger", default=False,action='store_true',
                  help="level-1 trigger")
    parser.add_option('--fit-trigger',dest="doTriggerFit", default=False,action='store_true',
                  help="fit trigger")
    parser.add_option('--fit-spectrum',dest="doSpectrumFit", default=False,action='store_true',
                  help="fit spectrum")
    parser.add_option('--sim',dest="doSimultaneousFit", default=False,action='store_true',
                  help="do simultaneous trigger fit")
    parser.add_option('--multi',dest="multi", default=True,action='store_true',
                  help="multiple background pdfs")
    parser.add_option('--write-fit', dest="doWriteFit", default=False, action='store_true',
                  help="save fit as a 1 GeV-binned histogram")
    parser.add_option('--words', dest="CUTSTRING", default=" ~~~~ ~~~~~ ", action='store_true',
                  help="what to write on canvas")
    parser.add_option('--lowA',dest="lA", default=0. ,type="float",
                  help="alphaLow")
    parser.add_option('--hiA',dest="hA", default=0.3,type="float",
                  help="alphaHigh")

    rt.RooMsgService.instance().setGlobalKillBelow(rt.RooFit.FATAL)
    rt.gStyle.SetPaintTextFormat('+.2f')

    (options,args) = parser.parse_args()

    cfg = Config.Config(options.config)
    
    box = options.box
    lumi = options.lumi
    year = options.year
    noFit = options.noFit
    fitRegion = options.fitRegion
    plotRegion = options.plotRegion
    histoName = cfg.getVariables(box, "histoName")

    fitfunc=""
    if("dijet" in options.config): fitfunc="Dijet"
    if("moddijet" in options.config): fitfunc="ModDijet"
    elif("atlas" in options.config): fitfunc="Atlas"
    elif("power" in options.config): fitfunc="Power"
    elif("power6" in options.config): fitfunc="Power6"
    elif("dipho" in options.config): fitfunc="Diphoton"

    if options.signalFileName==None:
        signalFileNames = []
        models = []
        xsecs = []
        colors = []
        styles = []
        masses = []
    else:
        signalFileNames = options.signalFileName.split(",")
        models = options.model.split("_")
        masses = options.mass.split("_")
        xsecs = options.xsec.split("_")
        colors = [rt.kBlue+1, rt.kCyan+1, rt.kViolet+1]
        styles = [2, 4, 6]

    print signalFileNames
    print models
    print masses
    print xsecs


    myTH1 = None
    for f in args:
        if f.lower().endswith('.root'):
            rootFile = rt.TFile(f)
            names = [k.GetName() for k in rootFile.GetListOfKeys()]
            print names
            if histoName in names:
                myTH1 = rootFile.Get(histoName)
    if myTH1 is None:
        print "give a root file as input"

    w = rt.RooWorkspace("w"+box)

    print("MULTI",options.multi)
    paramNames, bkgs = initializeWorkspace(w,cfg,box,multi=options.multi)
    
    x = array('d', cfg.getBinning(box)[0]) # mjj binning
    
    th1x = w.var('th1x')
    nBins = (len(x)-1)
    th1x.setBins(nBins)

    # get trigger dataset    
    triggerData = None
    # Use uncorrected mjj / pT of wide jets
    corr = '_noCorr'
    
    sideband = convertSideband(fitRegion,w,x)
    print 'sideband'
    print sideband
    print 'sideband2'
    plotband = convertSideband(plotRegion,w,x)

    w.Print()
    extDijetPdf = w.pdf('extDijetPdf')
    myf = rt.TFile("stuff.root","RECREATE") #This is necessary? 
    w.Write()
    myf.Close()

    myTH1.Rebin(len(x)-1,'data_obs_rebin',x)
    myRebinnedTH1 = rt.gDirectory.Get('data_obs_rebin')
    myRebinnedTH1.SetDirectory(0)
    
    myRealTH1 = convertToTh1xHist(myRebinnedTH1)        
    
    dataHist = rt.RooDataHist("data_obs","data_obs",rt.RooArgList(th1x), rt.RooFit.Import(myRealTH1))
    dataHist.Print('v')
    
    rootTools.Utils.importToWS(w,dataHist)

    rt.gStyle.SetOptStat(0)
    corrCanvas = rt.TCanvas('c','c',500,500)
    corrCanvas.SetRightMargin(0.15)            
    if not options.doSimultaneousFit:
        if options.doSpectrumFit:
            fr = binnedFit(extDijetPdf,dataHist,sideband,options.useWeight)
           # fr = binnedFit(extDijetPdf,dataHist,'6000,7000',options.useWeight)        
            rootTools.Utils.importToWS(w,fr)     
            fr.Print('v')
            fr.Print()
            fr.covarianceMatrix().Print('v')
            fr.correlationMatrix().Print('v')
            corrHist = fr.correlationHist('correlation_matrix')
            corrHist.Draw('colztext')
            corrCanvas.Print(options.outDir+'/corrHist.pdf')
            corrCanvas.Print(options.outDir+'/corrHist.C')
            
            ph = extDijetPdf.createHistogram("h_binned_%s" % box, w.var('mjj'), rt.RooFit.Binning(14000,0.,14000.))
            outtemp = rt.TFile("output/fitted_%s.root" % box, "recreate")
            outtemp.cd()
            ph.Write()
        else:
            fr = rt.RooFitResult()
    
    total = extDijetPdf.expectedEvents(rt.RooArgSet(th1x))
    print("TOTAL: {}".format(total))
    sbkg = extDijetPdf.createHistogram("h_binned_%s" % box, w.var('th1x'), rt.RooFit.Binning(3100,0.,3100.))
    
    # get signal histo if any
    signalHistos = []
    signalHistosOriginal = []
    signalHistosRebin = []
    signalFiles = []

    #extDijetPdf is RooAddPdf
    asimov = extDijetPdf.generateBinned(rt.RooArgSet(th1x),rt.RooFit.Name('central'),rt.RooFit.Asimov())
    #asimov is RooDataHist
        
    opt = [rt.RooFit.CutRange(myRange) for myRange in plotband.split(',')]
    asimov_reduce = asimov.reduce(opt[0])
    dataHist_reduce = dataHist.reduce(opt[0])
    for iOpt in range(1,len(opt)):
        asimov_reduce.add(asimov.reduce(opt[iOpt]))
        dataHist_reduce.add(dataHist.reduce(opt[iOpt]))
        
    rss = 0
    for i in range(0,len(x)-1):
        th1x.setVal(i+0.5)
        predYield = asimov.weight(rt.RooArgSet(th1x))
        dataYield = dataHist_reduce.weight(rt.RooArgSet(th1x))
        rss += float(predYield-dataYield) * float(predYield-dataYield)
        print "%i <= mjj < %i; prediction: %.2f; data %i"  % (x[i],x[i+1],predYield,dataYield)
    print "RSS = ", rss 
        
    rt.TH1D.SetDefaultSumw2()
    
    # start writing output
    rt.gStyle.SetOptStat(0)
    rt.gStyle.SetOptTitle(0)
    canv = rt.TCanvas('c','c',600,700)
    rootFile = rt.TFile.Open(options.outDir + '/' + 'Plots_%s'%box + '.root','recreate')
    tdirectory = rootFile.GetDirectory(options.outDir)
    if tdirectory==None:
        print "making directory"
        rootFile.mkdir(options.outDir)
        tdirectory = rootFile.GetDirectory(options.outDir)
        tdirectory.Print('v')
        
    h_th1x = asimov.createHistogram('h_th1x',th1x)
    h_data_th1x = dataHist_reduce.createHistogram('h_data_th1x',th1x)
    
    boxLabel = "%s %s Fit" % (box,fitRegion)
    plotLabel = "%s Projection" % (plotRegion)

    """
    background_pdf = w.pdf('%s_bkg_unbin'%box)
    print("background_pdf: ", background_pdf)
    print("type(background_pdf)", type(background_pdf))
    #These lines matter
    background= background_pdf.asTF(rt.RooArgList(w.var("mjj")),rt.RooArgList(w.var('p0_%s'%box)))
    rrv = w.var("mjj")
    f2 = background_pdf.asTF(rt.RooArgList(rrv), rt.RooArgList(), rt.RooArgSet(rrv) );
    print("rrv",rrv,type(rrv))
    print("f2",f2,type(f2))
    print("\n\nSTEVEN")
    print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    print(box)
    print(background)
    print(type(background))
    int_b = background.Integral(w.var("mjj").getMin(),w.var("mjj").getMax())

    print(background.Integral(0,3000))
    print(background.Integral(100,300))
    print(background.Integral(-1000,10000))
    print(background.Integral(0,1))
    
    print("=============min ",w.var('mjj').getMin())
    print("=============max ",w.var('mjj').getMax())
    print("=============intbkg ",int_b)
    p0_b = w.var('Ntot_%s_bkg'%box).getVal()
    # p0_b = w.var('Ntot_%s_bkg'%box).getVal()
    print("before division p0_b ", p0_b)
    print("int_b: {}".format(int_b))
    #print("MANUALLY SETTING int_b") #Do this for power
    #int_b = 1e-12
    #int_b =  1e-7	#
    print("lumi: {}".format(lumi))
    p0_b = w.var('Ntot_%s_bkg'%box).getVal() / (int_b * lumi)
    print("after division p0_b ", p0_b)
    # print("|===> expected bkg integral: ", w.var('Ntot_%s_bkg'%box).getVal())
    background.SetParameter(0,p0_b)
    """

   
#    if options.doWriteFit:
#        fnbin = MakeNBinsFromMinToMax(14000, 0., 14000.)
#        hb = rt.TH1F("hb_finebin", ";Average Dijet Mass [GeV];Events", len(fnbin)-1, fnbin)
#        for j in range(1, hb.GetNbinsX()+1): hb.SetBinContent(j, background.Eval(hb.GetXaxis().GetBinCenter(j)))
#        fhb = rt.TFile(options.outDir + "/unbinnedfit_%s.root"%box, "recreate")
#        fhb.cd()
#        hb.Write()
    
    g_data = rt.TGraphAsymmErrors(myRebinnedTH1)
    
    alpha = 1-0.6827
    for i in range(0,g_data.GetN()):
        N = g_data.GetY()[i]
        binWidth = g_data.GetEXlow()[i] + g_data.GetEXhigh()[i]
        L = 0
        if N!=0:
            L = rt.Math.gamma_quantile(alpha/2,N,1.)
        U = rt.Math.gamma_quantile_c(alpha/2,N+1,1)

        g_data.SetPointEYlow(i, (N-L)/(binWidth * lumi))
        g_data.SetPointEYhigh(i, (U-N)/(binWidth * lumi))
        g_data.SetPoint(i, g_data.GetX()[i], N/(binWidth * lumi))

        plotRegions = plotRegion.split(',')
        checkInRegions = [g_data.GetX()[i]>w.var('mjj').getMin(reg) and g_data.GetX()[i]<w.var('mjj').getMax(reg) for reg in plotRegions]
        if not any(checkInRegions):
            g_data.SetPointEYlow(i, 0)
            g_data.SetPointEYhigh(i, 0)
            g_data.SetPoint(i, g_data.GetX()[i], 0)
            
    #h_background = convertFunctionToHisto(background,"h_background",len(x)-1,x)
    h_th1x.Scale(1.0/lumi)
    h_background = convertToMjjHist(h_th1x,x)
    print("\n\n")
    print(h_background.Integral())
    print("\n\n")
    h_fit_residual_vs_mass = rt.TH1D("h_fit_residual_vs_mass","h_fit_residual_vs_mass",len(x)-1,x)
    list_chi2AndNdf_background = calculateChi2AndFillResiduals(g_data,h_background,h_fit_residual_vs_mass,w,0)

    g_data.SetMarkerStyle(20)
    g_data.SetMarkerSize(0.9)
    g_data.SetLineColor(rt.kBlack)
    g_data_clone = g_data.Clone('g_data_clone')
    g_data_clone.SetMarkerSize(0)

#############################################
    myleg = rt.TLegend(0.65,0.75,0.89,0.89)
    myleg.SetBorderSize(0)
    myleg.SetTextFont(42)
    myleg.SetTextSize(0.065)
    myleg.SetFillColor(rt.kWhite)
    myleg.SetFillStyle(0)
    myleg.SetLineWidth(0)
    myleg.SetLineColor(rt.kWhite)

    myRealTH1.SetTitle("{} Fit".format(fitfunc))
    h_th1x.SetTitle("{} Fit".format(fitfunc))
    myRealTH1.GetYaxis().SetTitleOffset(1)
    myRealTH1.GetYaxis().SetTitleSize(0.07)
    myRealTH1.GetYaxis().SetLabelSize(0.05)
    myRealTH1.GetXaxis().SetLabelOffset(1000)
    myRealTH1.GetXaxis().SetTitle("Diphoton Mass Bin #")
    myRealTH1.GetYaxis().SetTitle("Unscaled Entries")

    myRealTH1.SetMarkerColor(rt.kBlack)
    myRealTH1.SetMarkerStyle(8)
    myleg.AddEntry(myRealTH1, "Data")

    myRealTH1.Scale(1,"width")
    h_th1x.Scale(1,"width")

    h_th1x.SetLineColor(rt.kRed)
    h_th1x.SetLineWidth(2)
    h_th1x.Scale(lumi)
    myleg.AddEntry(h_th1x, "{} Fit".format(fitfunc))

    pullplot = myRealTH1.Clone()
    pullplot.Add(h_th1x, -1)

    for i in range(pullplot.GetNbinsX()):
      if not myRealTH1.GetBinContent(i+1) == 0:
        pullplot.SetBinContent(i+1, pullplot.GetBinContent(i+1)/myRealTH1.GetBinError(i+1))
        pullplot.SetBinError(i+1, 1)
      else:
        pullplot.SetBinContent(i+1, 0)
        pullplot.SetBinError(i+1, 0)

    ccc=rt.TCanvas("ctemp","ctemp",600,700)
    ccc.Divide(1,2,0,0,0)
    
    pd_1 = ccc.GetPad(1)
    pd_1.SetPad(0.01,0.37,0.99,0.98)
    pd_1.SetRightMargin(0.05)
    pd_1.SetTopMargin(0.05)
    pd_1.SetLeftMargin(0.175)
    pd_1.SetFillColor(0)
    pd_1.SetBorderMode(0)
    pd_1.SetFrameFillStyle(0)
    pd_1.SetFrameBorderMode(0)
    
    pd_2 = ccc.GetPad(2)
    pd_2.SetLeftMargin(0.175)#0.175
    pd_2.SetPad(0.01,0.02,0.99,0.37)#0.37
    pd_2.SetBottomMargin(0.35)
    pd_2.SetRightMargin(0.05)
    pd_2.SetGridx()
    pd_2.SetGridy()

###################################################################3
#Drawing on pad1

    pd_1.cd()
    myRealTH1.Draw("e0")
    h_th1x.Draw("L histsame")
    myleg.Draw("same")
    pd_1.SetLogy()

    l = rt.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetTextFont(42)
    l.SetNDC()
    #l.DrawLatex(0.7,0.96,"%i pb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
    #l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi/1000.,w.var('sqrts').getVal()/1000.))
    l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
    # PAS
    #l.SetTextFont(62)
    #l.SetTextSize(0.055)   
    #l.DrawLatex(0.2,0.96,"CMS")
    #l.SetTextFont(52)
    #l.SetTextSize(0.045)
    #l.DrawLatex(0.3,0.96,"Preliminary")
    # paper
    l.SetTextFont(62)
    l.SetTextSize(0.065)
    l.DrawLatex(0.22,0.89,"CMS")
    l.SetTextFont(52)
    l.SetTextSize(0.045)
    l.DrawLatex(0.32,0.89,"Preliminary")

    pave_sel = rt.TPaveText(0.58,0.53,0.75,0.73,"NDC")
    pave_sel.SetFillColor(0)
    pave_sel.SetBorderSize(0)
    pave_sel.SetFillStyle(0)
    pave_sel.SetTextFont(42)
    pave_sel.SetTextSize(0.045)
    pave_sel.SetTextAlign(11)
    pave_sel.AddText("#chi^{{2}} / ndf = {0:.2f} / {1:d} = {2:.2f}".format(
                          list_chi2AndNdf_background[4], list_chi2AndNdf_background[5],
                          list_chi2AndNdf_background[4]/list_chi2AndNdf_background[5]))
    pave_sel.AddText("Prob. = {0:.2f}".format(rt.TMath.Prob(list_chi2AndNdf_background[4], list_chi2AndNdf_background[5])))
    #pave_sel.AddText(options.CUTSTRING)
    pave_sel.Draw("SAME")
    pd_1.Update()

    
############################################################
#Drawing on pad2 (residuals)
    pd_2.cd()
    pullplot.GetYaxis().SetRangeUser(-3.5,3.5)
    pullplot.GetYaxis().SetNdivisions(210,True)
    pullplot.SetLineWidth(1)
    pullplot.SetFillColor(rt.kRed)
    pullplot.SetLineColor(rt.kBlack)
    
    pullplot.GetYaxis().SetTitleSize(2*0.06)
    pullplot.GetYaxis().SetLabelSize(2*0.05)
    # PAS
    #pullplot.GetYaxis().SetTitleOffset(0.5)
    #pullplot.GetYaxis().SetTitle('#frac{(Data-Fit)}{#sigma_{Data}}')
    # paper
    pullplot.GetYaxis().SetTitleOffset(0.6)
    pullplot.GetYaxis().SetTitle('#frac{(Data-Fit)}{Uncertainty}')
        
    pullplot.GetXaxis().SetTitleSize(2*0.06)
    pullplot.GetXaxis().SetLabelSize(2*0.05)
    pullplot.GetXaxis().SetTitle('Diphoton Mass Bin #')
    pullplot.GetXaxis().SetLabelOffset(0.03)
    pullplot.GetXaxis().SetNoExponent()
    pullplot.GetXaxis().SetMoreLogLabels()    
    #pullplot.GetXaxis().SetNdivisions(999)
    
    pullplot.Draw("histsame")

    ccc.Print("crudeFitPlot_{}.png".format(box))
#############################################
    

    # to remove dot at 0 (make it too high)
    for i in range (0,g_data.GetN()):
        if g_data.GetY()[i]==0:
            g_data.SetPoint(i,g_data.GetX()[i], 99999)
                   
    canv.Divide(1,2,0,0,0)
    
    pad_1 = canv.GetPad(1)
    #PAS
    #pad_1.SetPad(0.01,0.36,0.99,0.98)
    #paper 
    pad_1.SetPad(0.01,0.37,0.99,0.98)
   # pad_1.SetLogy()
    if 'PF' in box or w.var('mjj').getMax() > 526:
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
    if 'PF' in box or w.var('mjj').getMax() > 1246:
        pad_2.SetLogx()

    pad_1.cd()
    
    myRebinnedDensityTH1 = myRebinnedTH1.Clone('data_obs_density')
    for i in range(1,nBins+1):
        myRebinnedDensityTH1.SetBinContent(i, myRebinnedTH1.GetBinContent(i)/ myRebinnedTH1.GetBinWidth(i))
        myRebinnedDensityTH1.SetBinError(i, myRebinnedTH1.GetBinError(i)/ myRebinnedTH1.GetBinWidth(i))
        
        plotRegions = plotRegion.split(',')
        checkInRegions = [myRebinnedDensityTH1.GetXaxis().GetBinCenter(i)>w.var('mjj').getMin(reg) and myRebinnedDensityTH1.GetXaxis().GetBinCenter(i)<w.var('mjj').getMax(reg) for reg in plotRegions]      
        if not any(checkInRegions):
            myRebinnedDensityTH1.SetBinContent(i,0)
            myRebinnedDensityTH1.SetBinError(i,0)
    myRebinnedDensityTH1.GetXaxis().SetRangeUser(w.var('mjj').getMin(),w.var('mjj').getMax())
    #myRebinnedDensityTH1.GetXaxis().SetRangeUser(190.,w.var('mjj').getMax()) #edw X axis range top pad
    # paper:
    myRebinnedDensityTH1.GetYaxis().SetTitle('d#sigma/dm_{4#gamma} [pb/TeV]')
    # PAS:
    #myRebinnedDensityTH1.GetYaxis().SetTitle('d#sigma / dm_{jj} [pb / GeV]')
    myRebinnedDensityTH1.GetYaxis().SetTitleOffset(1)
    myRebinnedDensityTH1.GetYaxis().SetTitleSize(0.07)
    myRebinnedDensityTH1.GetYaxis().SetLabelSize(0.05)
    myRebinnedDensityTH1.GetXaxis().SetLabelOffset(1000)
    myRebinnedDensityTH1.Scale(0)
    myRebinnedDensityTH1.SetLineColor(rt.kWhite)
    myRebinnedDensityTH1.SetMarkerColor(rt.kWhite)
    myRebinnedDensityTH1.SetLineWidth(0)    
    #Plot mins and maxes
    myRebinnedDensityTH1.SetMaximum(20)#20
    myRebinnedDensityTH1.SetMinimum(5e-4)#2e-8
    myRebinnedDensityTH1.Draw("axis")
    
#    if options.doTriggerFit or options.doSimultaneousFit or options.doSpectrumFit or options.noFit:
#        #This is the one I'm drawing
#        background.Draw("csame")
#        #background.Draw("c")
#
#    else:
#        h_background.SetLineColor(rt.kRed) #Tried
#        h_background.SetLineWidth(2)
#        h_background.Draw("histsame")
    h_background.SetLineColor(rt.kRed) #Tried
    h_background.SetLineWidth(2)
    h_background.Draw("histsame")

    rt.gPad.SetLogy()
    
    l = rt.TLatex()
    l.SetTextAlign(11)
    l.SetTextSize(0.045)
    l.SetTextFont(42)
    l.SetNDC()
    #l.DrawLatex(0.7,0.96,"%i pb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
    #l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi/1000.,w.var('sqrts').getVal()/1000.))
    l.DrawLatex(0.72,0.96,"%.1f fb^{-1} (%i TeV)"%(lumi,w.var('sqrts').getVal()/1000.))
    # PAS
    #l.SetTextFont(62)
    #l.SetTextSize(0.055)   
    #l.DrawLatex(0.2,0.96,"CMS")
    #l.SetTextFont(52)
    #l.SetTextSize(0.045)
    #l.DrawLatex(0.3,0.96,"Preliminary")
    # paper
    l.SetTextFont(62)
    l.SetTextSize(0.065)
    l.DrawLatex(0.22,0.89,"CMS")
    l.SetTextFont(52)
    l.SetTextSize(0.045)
    l.DrawLatex(0.32,0.89,"Preliminary")

    if(options.lA is not None and options.hA is not None):
      l.SetTextFont(62)
      l.SetTextSize(0.055)
      l.DrawLatex(0.22,0.75,"{} #leq #alpha < {}".format(options.lA, options.hA))
        
    if options.signalFileName!=None:
        if 'Calo' in box:
            leg = rt.TLegend(0.58,0.58,0.89,0.94)
        else:
            leg = rt.TLegend(0.6,0.58,0.89,0.94)
    else:        
        leg = rt.TLegend(0.7,0.7,0.89,0.88)
    leg.SetTextFont(42)
    leg.SetFillColor(rt.kWhite)
    leg.SetFillStyle(0)
    leg.SetLineWidth(0)
    leg.SetLineColor(rt.kWhite)
    leg.AddEntry(g_data,"Data","pe")
    #leg.AddEntry(background,"{} Fit".format(fitfunc),"l")
    leg.Draw()
    #background.Draw("csame")
    #g_data.Draw("pezsame")

    #pave_sel = rt.TPaveText(0.2,0.03,0.5,0.25,"NDC")
    pave_sel = rt.TPaveText(0.5,0.43,0.7,0.63,"NDC")
    pave_sel.SetFillColor(0)
    pave_sel.SetBorderSize(0)
    pave_sel.SetFillStyle(0)
    pave_sel.SetTextFont(42)
    pave_sel.SetTextSize(0.045)
    pave_sel.SetTextAlign(11)
    pave_sel.AddText("#chi^{{2}} / ndf = {0:.2f} / {1:d} = {2:.2f}".format(
                          list_chi2AndNdf_background[4], list_chi2AndNdf_background[5],
                          list_chi2AndNdf_background[4]/list_chi2AndNdf_background[5]))
    pave_sel.AddText("Prob. = {0:.2f}".format(rt.TMath.Prob(list_chi2AndNdf_background[4], list_chi2AndNdf_background[5])))
    #pave_sel.AddText(options.CUTSTRING)
    pave_sel.Draw("SAME")
    
#    list_parameter = [p0_b, p0_b*(w.var('Ntot_%s_bkg'%box).getErrorHi() - w.var('Ntot_%s_bkg'%box).getErrorLo())/(2.0*w.var('Ntot_%s_bkg'%box).getVal()),                      
#                      w.var('p1_%s'%box).getVal(), (w.var('p1_%s'%box).getErrorHi() - w.var('p1_%s'%box).getErrorLo())/2.0,
#                      w.var('p2_%s'%box).getVal(), (w.var('p2_%s'%box).getErrorHi() - w.var('p2_%s'%box).getErrorLo())/2.0,
#                      #w.var('pm3_%s'%box).getVal(), (w.var('pm3_%s'%box).getErrorHi() - w.var('pm3_%s'%box).getErrorLo())/2.0,
#                      #w.var('pm4_%s'%box).getVal(), (w.var('pm4_%s'%box).getErrorHi() - w.var('pm4_%s'%box).getErrorLo())/2.0,
#                      # w.var('p5_%s'%box).getVal(), (w.var('p5_%s'%box).getErrorHi() - w.var('_%s'%box).getErrorLo())/2.0,
#                      w.var('meff_%s'%box).getVal(), (w.var('meff_%s'%box).getErrorHi() - w.var('meff_%s'%box).getErrorLo())/2.0,
#                      w.var('seff_%s'%box).getVal(), (w.var('seff_%s'%box).getErrorHi() - w.var('seff_%s'%box).getErrorLo())/2.0]
# w.var('p3_%s'%box).getVal(), (w.var('p3_%s'%box).getErrorHi() - w.var('p3_%s'%box).getErrorLo())/2.0,


    pave_param = rt.TPaveText(0.55,0.03,0.9,0.25,"NDC")
    pave_param.SetTextFont(42)
    pave_param.SetFillColor(0)
    pave_param.SetBorderSize(0)
    pave_param.SetFillStyle(0)
    pave_param.SetTextAlign(11)
    pave_param.SetTextSize(0.045)
#    pave_param.AddText("p_{0}"+" = {0:.2g} #pm {1:.2g}".format(list_parameter[0], list_parameter[1]))
#    pave_param.AddText("p_{1}"+" = {0:.2f} #pm {1:.2f}".format(list_parameter[2], list_parameter[3]))
#    pave_param.AddText("p_{2}"+" = {0:.2f} #pm {1:.2f}".format(list_parameter[4], list_parameter[5]))
#    pave_param.AddText("p_{3}"+" = {0:.2f} #pm {1:.2f}".format(list_parameter[6], list_parameter[7]))
#    if w.var('meff_%s'%box).getVal()>0 and w.var('seff_%s'%box).getVal()>0 and (options.doTriggerFit or options.doSimultaneousFit):
#        pave_param.AddText("m_{eff}"+" = {0:.2f} #pm {1:.2f}".format(list_parameter[8], list_parameter[9]))
#        pave_param.AddText("#sigma_{eff}"+" = {0:.2f} #pm {1:.2f}".format(list_parameter[10], list_parameter[11]))
#    elif w.var('eff_bin%02d'%(0)) != None:
#        effValList = []
#        effErrHiList = []
#        effErrLoList = []
#        for i in range(0,len(x)-1):
#            if not w.var('eff_bin%02d'%(i)).isConstant():
#                effValList.append(w.var('eff_bin%02d'%(i)).getVal())
#                effErrHiList.append(w.var('eff_bin%02d'%(i)).getErrorHi())
#                effErrLoList.append(w.var('eff_bin%02d'%(i)).getErrorLo())
#
#        valString = ",".join(["%.3f"%(effVal) for effVal in effValList])
#        errString = ",".join(["^{%+.1e}_{%+.1e}"%(effErrHi,effErrLo) for effErrHi,effErrLo in zip(effErrHiList,effErrLoList)])
#        pave_param.SetTextSize(0.025)
#        pave_param.AddText("#epsilon = %s"%valString)
#        pave_param.AddText("#delta#epsilon = %s"%errString)
            
    #pave_param.Draw("SAME")
    
#    if options.doTriggerFit or options.doSimultaneousFit or options.doSpectrumFit or options.noFit:
#        #Drawing this for power function
#        #background.SetLineColor(rt.kGreen)
#        print("Drawing \'background\'")
#        background.Draw("csame")
#    else:
#        print("Drawing \'h_background\'")
#        h_background.SetLineColor(rt.kRed) #Tried
#        h_background.SetLineWidth(2)
#        h_background.Draw("histsame")
    h_background.SetLineColor(rt.kRed) #Tried
    h_background.SetLineWidth(2)
    h_background.Draw("histsame")
    #Drawing this for power function
    g_data_clone.Draw("zpsame")
    g_data.Draw("zpsame")
    #h_background.SetLineColor(rt.kRed) 
    #h_background.SetLineWidth(2)
    #h_background.Draw("histsame")
        
    pad_1.Update()

    pad_2.cd()
    
    h_fit_residual_vs_mass.GetXaxis().SetRangeUser(w.var('mjj').getMin(),w.var('mjj').getMax())
    #h_fit_residual_vs_mass.GetXaxis().SetRangeUser(190.,w.var('mjj').getMax()) #edw X axis range bottom pad
    h_fit_residual_vs_mass.GetYaxis().SetRangeUser(-3.5,3.5)
    h_fit_residual_vs_mass.GetYaxis().SetNdivisions(210,True)
    h_fit_residual_vs_mass.SetLineWidth(1)
    h_fit_residual_vs_mass.SetFillColor(rt.kRed)
    h_fit_residual_vs_mass.SetLineColor(rt.kBlack)
    
    h_fit_residual_vs_mass.GetYaxis().SetTitleSize(2*0.06)
    h_fit_residual_vs_mass.GetYaxis().SetLabelSize(2*0.05)
    # PAS
    #h_fit_residual_vs_mass.GetYaxis().SetTitleOffset(0.5)
    #h_fit_residual_vs_mass.GetYaxis().SetTitle('#frac{(Data-Fit)}{#sigma_{Data}}')
    # paper
    h_fit_residual_vs_mass.GetYaxis().SetTitleOffset(0.6)
    h_fit_residual_vs_mass.GetYaxis().SetTitle('#frac{(Data-Fit)}{Uncertainty}')
        
    h_fit_residual_vs_mass.GetXaxis().SetTitleSize(2*0.06)
    h_fit_residual_vs_mass.GetXaxis().SetLabelSize(2*0.05)
    #h_fit_residual_vs_mass.GetXaxis().SetTitle('m_{jj} [GeV]')
    # PAS
    #h_fit_residual_vs_mass.GetXaxis().SetTitle('Dijet Mass [GeV]')
    # paper
    h_fit_residual_vs_mass.GetXaxis().SetTitle('Average diphoton mass [TeV]')

    
    #h_fit_residual_vs_mass.SetLineColor(rt.kGreen)
    h_fit_residual_vs_mass.Draw("histsame")
    
    if 'PF' in box or w.var('mjj').getMax() > 1246:        
        # PAS
        #h_fit_residual_vs_mass.GetXaxis().SetTitle('Dijet Mass [TeV]')
        # paper
#       h_fit_residual_vs_mass.GetXaxis().SetTitle('Dijet mass [TeV]')
	#h_fit_residual_vs_mass.GetXaxis().SetTitle('Average Dijet Mass [TeV]')
        h_fit_residual_vs_mass.GetXaxis().SetLabelOffset(1000)
        h_fit_residual_vs_mass.GetXaxis().SetNoExponent()
        h_fit_residual_vs_mass.GetXaxis().SetMoreLogLabels()    
        h_fit_residual_vs_mass.GetXaxis().SetNdivisions(999)
        xLab = rt.TLatex()
        xLab.SetTextAlign(22)
        xLab.SetTextFont(42)
        xLab.SetTextSize(2*0.05)	
        if w.var('mjj').getMin() < 1000:
            xLab.DrawLatex(600, -4, "0.6")
	    xLab.DrawLatex(800, -4, "0.8")	
            xLab.DrawLatex(1000, -4, "1")
	if w.var('mjj').getMin() < 200:
	    xLab.DrawLatex(200, -4, "0.2")
	if w.var('mjj').getMin() < 400:
	    xLab.DrawLatex(400, -4, "0.4")
	xLab.DrawLatex(1500, -4, "1.5")
        xLab.DrawLatex(2000, -4, "2")
        xLab.DrawLatex(3000, -4, "3")
        xLab.DrawLatex(4000, -4, "4")
        xLab.DrawLatex(5000, -4, "5")
        xLab.DrawLatex(6000, -4, "6")
        xLab.DrawLatex(7000, -4, "7")
        xLab.DrawLatex(8000, -4, "8")
        
        f_h2_log10_x_axis = rt.TF1("f_h2_log10_x_axis", "log10(x)", h_fit_residual_vs_mass.GetXaxis().GetXmin(), h_fit_residual_vs_mass.GetXaxis().GetXmax())
        a = rt.TGaxis(h_fit_residual_vs_mass.GetXaxis().GetXmin(), -3.5,
                      h_fit_residual_vs_mass.GetXaxis().GetXmax(), -3.5, "f_h2_log10_x_axis", 509, "BS", 0.0)
        a.SetTickSize(h_fit_residual_vs_mass.GetTickLength("X"))
        a.SetMoreLogLabels()
        a.SetLabelOffset(1000)
        a.Draw()
        
        rt.gPad.Modified()
        rt.gPad.Update()
    
    canv.Print(options.outDir+"/fit_mjj_%s_%s_%s.png"%(fitRegion.replace(',','_'),box,year))
    canv.Print(options.outDir+"/fit_mjj_%s_%s_%s.C"%(fitRegion.replace(',','_'),box,year))
    tdirectory.cd()
    canv.Write()

    outFileName = "DijetFitResults_%s_%s.root"%(box,year)
    outFile = rt.TFile(options.outDir+"/"+outFileName,'recreate')
    outFile.cd()
    w.Write()
    outFile.Close()

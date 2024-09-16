from ROOT import *
import numpy


def ReadingWorkspace():

  signal_mjj = [303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]
  nbins = len(signal_mjj)

  infile = TFile("./stuff.root")

  w = infile.Get("wdiphoton_power"); #Load workspace from file
  w.Print();
  
  Bkg_binned = w.pdf("diphoton_power_bkg");
  Bkg_unbinned = w.pdf("diphoton_power_bkg_unbin");

  th1x = w.var("th1x");
  mjj = w.var("mjj");

  th1x_frame = th1x.frame()
  mjj_frame = mjj.frame()

  Bkg_binned.plotOn(th1x_frame);
  Bkg_unbinned.plotOn(mjj_frame);

  cb = TCanvas("binned","binned",800,800)
  cb.cd()
  th1x_frame.Draw()
  cb.Print("cbcanv.png")

  cub = TCanvas("unbinned","unbinned",800,800)
  cub.cd()
  mjj_frame.Draw()
  cub.Print("cubcanv.png")

  nentries=5000000; #Don't know why
  unbinned = Bkg_unbinned.createHistogram("mjj",nentries);

  #myscale=11387 #from Ilias code
  myscale = 2000; #integral of binned histo? 
  unbinned.Scale(myscale)
  unbinned.Print()

  Bkg_fit_binned = TH1D("Bkg_fit_binned","Binned bkg-only standard fit",nbins-1,numpy.array(signal_mjj));
  Bkg_fit_unbinned = TH1D("Bkg_fit_unbinned","Unbinned bkg-only standard fit",3100,0,3100);

  for ii in range(0,unbinned.GetNbinsX()):
    val = unbinned.GetBinContent(ii);
    xval = unbinned.GetBinCenter(ii);
    Bkg_fit_unbinned.Fill(xval,val);
    Bkg_fit_binned.Fill(xval,val);
  

  fout = TFile("DiphotonFitResult_test.root","recreate");
  fout.cd();
  Bkg_fit_unbinned.Write();
  Bkg_fit_binned.Write();

ReadingWorkspace()


#include "RooGlobalFunc.h"
//#include "RooDijetBinPdf.h"
#include "RooRealVar.h"
#include "RooDataSet.h"
#include "RooGaussian.h"
#include "RooConstVar.h"
#include "RooChebychev.h"
#include "RooAddPdf.h"
#include "RooWorkspace.h"
#include "RooPlot.h"
#include "TCanvas.h"
#include "TAxis.h"
#include "TFile.h"
#include "TH1.h"

using namespace RooFit;

void ReadingWorkspace() {

  double massBoundaries[114] = {303, 310, 317, 324, 331, 338, 345, 352, 360, 368, 376, 384, 392, 400, 409, 418, 427, 436, 445, 454, 464, 474, 484, 494, 504, 515, 526, 537, 548, 560, 572, 584, 596, 609, 622, 635, 648, 662, 676, 690, 704, 719, 734, 749, 765, 781, 797, 814, 831, 848, 866, 884, 902, 921, 940, 959, 979, 999, 1020, 1041, 1063, 1085, 1107, 1130, 1153, 1177, 1201, 1226, 1251, 1277, 1303, 1330, 1357, 1385, 1413, 1442, 1472, 1502, 1533, 1564, 1596, 1629, 1662, 1696, 1731, 1766, 1802, 1839, 1877,1915, 1954, 1994, 2035, 2077, 2119, 2162, 2206, 2251, 2297, 2344, 2392, 2441, 2491, 2542, 2594, 2647, 2701, 2756, 2812, 2869, 2927, 2987, 3048, 3110};

  //Open input file with workspace
  TFile *f = new TFile("../stuff.root");

  RooWorkspace *w = (RooWorkspace*)f->Get("wdiphoton_power"); //Load workspace from file
  w->Print();
  
  RooAbsPdf* Bkg_binned = w->pdf("diphoton_power_bkg");
  RooAbsPdf* Bkg_unbinned = w->pdf("diphoton_power_bkg_unbin");

  RooRealVar* th1x = w->var("th1x");
  RooRealVar* mjj = w->var("mjj");

  RooPlot* th1x_frame = th1x->frame(Title("Binned bkg-only standard fit")) ;
  RooPlot* mjj_frame = mjj->frame(Title("Unbinned bkg-only standard fit")) ;

  Bkg_binned->plotOn(th1x_frame);
  Bkg_unbinned->plotOn(mjj_frame);

  int nentries=5000000;
  TH1 *unbinned = Bkg_unbinned->createHistogram("mjj",nentries);

  float myscale = 1000;
  unbinned->Scale(myscale);
  unbinned->Print();

  TH1D *Bkg_fit_binned = new TH1D("Bkg_fit_binned","Binned bkg-only standard fit",114,massBoundaries);
  TH1D *Bkg_fit_unbinned = new TH1D("Bkg_fit_unbinned","Unbinned bkg-only standard fit",3100,0,3100);

  for(int ii=0; ii<nentries; ii++){
    double val = unbinned->GetBinContent(ii);
    double xval = unbinned->GetBinCenter(ii);
    Bkg_fit_unbinned->Fill(xval,val);
    Bkg_fit_binned->Fill(xval,val);
  }

  TFile *fout = new TFile("DiphotonFitResult_test.root","recreate");
  fout->cd();
  Bkg_fit_unbinned->Write();
  Bkg_fit_binned->Write();

}

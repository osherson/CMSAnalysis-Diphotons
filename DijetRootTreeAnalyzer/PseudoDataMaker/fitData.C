#include "TCanvas.h"
#include "TFrame.h"
#include "TBenchmark.h"
#include "TString.h"
#include "TF1.h"
#include "TH1.h"
#include "TFile.h"
#include "TROOT.h"
#include "TError.h"
#include "TInterpreter.h"
#include "TSystem.h"
#include "TPaveText.h"
#include "TMath.h"

#include <iostream>

using namespace std;


TH1F* convertToMjjHist(TH1F* hist_th1x){
  const int xbsize = 115;
  double xbins[xbsize] = {297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0};

// hist = rt.TH1D(hist_th1x.GetName()+'_mjj',hist_th1x.GetName()+'_mjj',len(x)-1,x)
// for i in range(1,hist_th1x.GetNbinsX()+1):
//     hist.SetBinContent(i,hist_th1x.GetBinContent(i)/(x[i]-x[i-1]))
//    hist.SetBinError(i,hist_th1x.GetBinError(i)/(x[i]-x[i-1]))

// return hist
  
  const char *n =  hist_th1x->GetName();
  char nr[] = "_r";
  char * newName = new char[std::strlen(n)+std::strlen(nr)+1];
  std::strcpy(newName,n);
  std::strcat(newName,nr);
  delete [] newName;

  auto hist = new TH1F(newName, newName, xbsize-1, xbins);
  for(int ii=1; ii<hist_th1x->GetNbinsX()+1; ii++){
    hist->SetBinContent(ii,hist_th1x->GetBinContent(ii) / (xbins[ii] - xbins[ii-1]));
    hist->SetBinError(ii,hist_th1x->GetBinError(ii) / (xbins[ii] - xbins[ii-1]));
  }

  return hist;
}

double_t getLastBin(TH1F *hist){

  double_t lb = 0.;
  for (int bn=hist->GetNbinsX(); bn>0; bn -= 1){
    if(hist->GetBinContent(bn)==0){continue;}
    else{
      lb = hist->GetBinLowEdge(bn);
      break;
    }
  }

  return lb;
}

TF1* getDijet(double_t fmin, double_t fmax){
  TF1 *func = new TF1("func", "[0] * TMath::Power( (1-(x/13000) ), [1] ) / TMath::Power( (x/13000) ,[2]) ",fmin,fmax);
  func->SetParNames("p0","p1","p2");
  func->SetParameters(10,-1.,-0.1);
  func->SetParLimits(2,-1.,-0.0001);
  return func;
}

TF1* getModDijet(double_t fmin, double_t fmax){
  TF1 *func = new TF1("func", "[0] * TMath::Power( (1-TMath::Power((x/13000),1./3.)), [1] ) / TMath::Power((x/13000),[2]) ",fmin,fmax);
  func->SetParNames("p0","p1","p2");
  func->SetParameters(10,-1.,-0.1);
  func->SetParLimits(2,-1.,-0.0001);
  return func;
}

TF1* getATLAS(double_t fmin, double_t fmax){
  TF1 *func = new TF1("func", "[0] * (1 / TMath::Power((x/13000), [1] )) * TMath::Exp(-[2]*(x/13000) )",fmin,fmax);
  func->SetParNames("p0","p1","p2");
  func->SetParameters(1.,0.1,0.001);
  func->SetParLimits(2,0.00001, 0.1);
  return func;
}

TF1* getDipho(double_t fmin, double_t fmax){
  TF1 *func = new TF1("func", "[0] * TMath::Power((x/13000), [1] + [2]*TMath::Log((x/13000)) )",fmin,fmax);
  func->SetParNames("p0","p1","p2");
  func->SetParameters(1.,-10.,-1.);
  func->SetParLimits(1,-100.,-0.001);
  func->SetParLimits(2,-10.,-0.0001);
  return func;
}

//EXT PARAMETER                APPROXIMATE        STEP         FIRST   
//NO.   NAME      VALUE            ERROR          SIZE      DERIVATIVE 
//1  p0           2.02239e+02   1.61286e+02  -2.23035e-05  -5.23629e-06
//2  p1           1.00027e+00   2.20628e-04   7.35314e-11  -2.17007e+02
//3  p2          -4.30891e+01   4.25469e+01   1.75457e-08   7.04656e-01
//4  p3           2.01322e-01   1.41664e+00  -3.79630e-09  -1.60814e-07


TF1* getPower(double_t fmin, double_t fmax){
  //TF1 *func = new TF1("func", "[0] * TMath::Power([1], [2]*(x/13000) + [3]/(x/13000) )",fmin,fmax);
  //func->SetParNames("p0","p1","p2", "p3");
  //func->SetParameters(10.,1.,-23.667,0.1);
  //func->SetParLimits(1,0.001,100);
  //func->SetParLimits(2,-10000.,-1.);
  //func->SetParLimits(3,0.0001,0.1);
  TF1 *func = new TF1("func", "[0] * TMath::Power([1], [2]*(x) + [3]/(x) )",fmin,fmax);
  func->SetParNames("p0","p1","p2", "p3");
  func->SetParameters(10.,1.,-1.,0.1);
  func->SetParLimits(0,10.,1000.);
  func->SetParLimits(1,0.1,10.);
  func->SetParLimits(2,-100.,-1.);
  func->SetParLimits(3,0.001,0.1);
  return func;
}

void fitData(){

  for(int Abin=0; Abin<15; Abin++){
  //for(int Abin=14; Abin<15; Abin++){
  //for(int Abin=3; Abin<5; Abin++){

    std::string s = std::to_string(Abin);
    const char* alphabin = s.c_str();

    const char* datadir = "../inputs/Shapes_DATA/alphaBinning/cuts_masym025_deta1p5_dipho09_iso01/";
    //const char* datadir = "../inputs/Shapes_DATA/alphaBinning/ALL/";
    const char* dname = "/DATA.root";
    char dresult[100];
    strcpy(dresult,datadir);strcat(dresult,alphabin);strcat(dresult,dname);
    //strcpy(dresult,datadir);strcat(dresult,dname);
    const char* dataname = dresult;

    std::cout << "Alpha Bin " << alphabin << std::endl;

    TFile *dfile = new TFile(dataname, "read");

    //TFile *dfile = new TFile("../inputs/Shapes_DATA/alphaBinning/ALL/DATA.root");
    TH1F *dhist = (TH1F*)dfile->Get("data_XM");
    dhist->SetName("data_in");
    dhist->GetXaxis()->SetTitle("");
    dhist->SetMarkerStyle(20);
    dhist->SetMarkerSize(1.0);
    dhist->SetMarkerColor(1);
    dhist->SetLineColor(1);
    dhist->SetLineWidth(2.0);


    auto drhist = convertToMjjHist(dhist);
    drhist->Scale(1., "width");
    drhist->GetXaxis()->SetTitle("");
    drhist->SetMarkerStyle(20);
    drhist->SetMarkerSize(1.0);
    drhist->SetMarkerColor(1);
    drhist->SetLineColor(1);
    drhist->SetLineWidth(2.0);

    double_t fitmin = 297.;
    //double_t fitmax = 1.5 * getLastBin(dhist); //last bin with any data in it
    double_t fitmax = 3110.;

    int whichFunc = 4;
    // 0:dijet, 1:atlas, 2:moddijet, 3:dipho, 4:power
    const char* fnames[5] = {"dijet", "atlas", "moddijet", "dipho", "power"};
    const char* funcName = fnames[whichFunc];
    std::cout << "Function: " << funcName << std::endl;
    TF1 *func = new TF1();

    switch(whichFunc){
      case 0:
        func = getDijet(fitmin, fitmax);
        break;
      case 1:
        func = getATLAS(fitmin, fitmax);
        break;
      case 2:
        func = getModDijet(fitmin, fitmax);
        break;
      case 3:
        func = getDipho(fitmin, fitmax);
        break;
      case 4:
        func = getPower(fitmin, fitmax);
        break;
    }

    dhist->Fit(func, "EM0");
    //return 0;

    func->SetLineColor(kRed);
    gStyle->SetOptStat();

    TCanvas *c1 = new TCanvas("c1","c1", 800,600);
    c1->cd();

    const char* ofbase = "../inputs/Shapes_PseudoData/";
    char result[100];
    strcpy(result,ofbase);
    strcat(result,alphabin);

    const char* ab = "Alpha bin ";
    const char* dr = ", Function: ";
    char rt[100];
    strcpy(rt, ab);strcat(rt,alphabin);strcat(rt, dr);strcat(rt, funcName);
    char s1[100];
    strcpy(s1,result);
    strcat(s1,"_");
    strcat(s1,funcName);
    strcat(s1,"_fit.png");
    dhist->SetTitle(rt);
    dhist->Draw("PE0");
    func->Draw("same");
    c1->SetLogx();
    c1->SetLogy();
    c1->Print(s1);

    strcat(rt," Generated");
    auto h1f = new TH1F("data_XM",rt,dhist->GetNbinsX(),dhist->GetBinLowEdge(0),dhist->GetBinLowEdge(dhist->GetNbinsX()));
    char s2[100];
    strcpy(s2,result);
    strcat(s2,"_");
    strcat(s2,funcName);
    strcat(s2,"_gen.png");
    h1f->FillRandom("func",dhist->GetEntries()*10);
    h1f->Scale(1., "width");
    h1f->GetXaxis()->SetTitle("");
    h1f->SetMarkerStyle(20);
    h1f->SetMarkerSize(1.0);
    h1f->SetMarkerColor(4);
    h1f->SetLineColor(4);
    h1f->SetLineWidth(2.0);

    TCanvas *c2 = new TCanvas("c2","c2", 800,600);
    c2->cd();
    h1f->Draw("PE0");
    c2->SetLogx();
    c2->SetLogy();
    c2->Print(s2);

    const char* dd = "/DATA_";
    const char* root = ".root";
    strcat(result,dd);
    strcat(result,funcName);
    strcat(result,root);
    const char* ofname = result;
    std::cout << "Saving output in: " << ofname << std::endl;
    TFile *outfile = new TFile(ofname,"recreate");
    outfile->cd();
    h1f->Write();
    outfile->Write();
    outfile->Close();
    
  }

  return 0;
}

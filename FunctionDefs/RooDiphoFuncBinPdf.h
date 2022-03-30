//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooDiphoFuncBinPdf_h
#define HiggsAnalysis_CombinedLimit_RooDiphoFuncBinPdf_h
//---------------------------------------------------------------------------
#include "RooAbsPdf.h"
#include "RooConstVar.h"
#include "RooRealProxy.h"
//---------------------------------------------------------------------------
class RooRealVar;
class RooAbsReal;

#include "Riostream.h"
#include "TMath.h"
#include <TH1.h>
#include "Math/SpecFuncMathCore.h"
#include "Math/SpecFuncMathMore.h"
#include "Math/Functor.h"
#include "Math/WrappedFunction.h"
#include "Math/IFunction.h"
#include "Math/Integrator.h"

//---------------------------------------------------------------------------
class RooDiphoFuncBinPdf : public RooAbsPdf
{
public:
   RooDiphoFuncBinPdf() {} ;
   RooDiphoFuncBinPdf(const char *name, const char *title,
		    RooAbsReal& _th1x, RooAbsReal& _p1,
		RooAbsReal& _p2, RooAbsReal& _p3, RooAbsReal& _p4, 
		  RooAbsReal& _sqrts);
   RooDiphoFuncBinPdf(const RooDiphoFuncBinPdf& other,
      const char* name = 0);
   void setTH1Binning(TH1* _Hnominal);
   void setAbsTol(double _absTol);
   void setRelTol(double _relTol);
   virtual TObject* clone(const char* newname) const { return new RooDiphoFuncBinPdf(*this,newname); }
   inline virtual ~RooDiphoFuncBinPdf() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:   

   RooRealProxy th1x;        // dependent variable
   RooRealProxy p1;       // p1
   RooRealProxy p2;        // p2
   RooRealProxy p3;        // p3
   RooRealProxy p4;        // p4
   RooRealProxy sqrts;        // sqrts
   Int_t xBins;        // X bins
   Double_t xArray[2000]; // xArray[xBins+1]
   Double_t xMax;        // X max
   Double_t xMin;        // X min
   Double_t relTol;      //relative tolerance for numerical integration
   Double_t absTol;      //absolute tolerance for numerical integration

   Double_t evaluate() const;
private:
   ClassDef(RooDiphoFuncBinPdf,1) // RazorAtlasBinPdf function
    
};
//---------------------------------------------------------------------------
#endif

#include "Math/IFunction.h"
#include "Math/IParamFunction.h"
 
class DiphoFunction: public ROOT::Math::IParametricFunctionOneDim
{
private:
   const double *pars;
 
public:
   double DoEvalPar(double x,const double* p) const
   {
     double pdf = p[0]*pow(x, p[1] + p[2]*log(x) + p[3]*log(x)*log(x) + p[4]*log(x)*log(x)*log(x));
     return pdf;
   }
   double DoEval(double x) const
   {
     double pdf = pars[0]*pow(x, pars[1] + pars[2]*log(x) + pars[3]*log(x)*log(x) + pars[4]*log(x)*log(x)*log(x));
     return pdf;
   }
 
   ROOT::Math::IBaseFunctionOneDim* Clone() const
   {
      return new DiphoFunction();
   }
 
   const double* Parameters() const
   {
      return pars;
   }

   void SetParameters(const double* p)
   {
      pars = p;
   }
 
   unsigned int NPar() const
   {
      return 5;
   }
};

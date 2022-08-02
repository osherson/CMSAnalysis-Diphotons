//---------------------------------------------------------------------------
#ifndef HiggsAnalysis_CombinedLimit_RooModDijet3ParamBinPdf_h
#define HiggsAnalysis_CombinedLimit_RooModDijet3ParamBinPdf_h
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
class RooModDijet3ParamBinPdf : public RooAbsPdf
{
public:
   RooModDijet3ParamBinPdf() {} ;
   RooModDijet3ParamBinPdf(const char *name, const char *title,
		    RooAbsReal& _th1x, RooAbsReal& _p1,
		  RooAbsReal& _p2,
		  RooAbsReal& _sqrts, RooAbsReal& _meff, RooAbsReal& _seff);
   RooModDijet3ParamBinPdf(const char *name, const char *title,
		    RooAbsReal& _th1x, RooAbsReal& _p1,
		  RooAbsReal& _p2,
		  RooAbsReal& _sqrts);
   RooModDijet3ParamBinPdf(const RooModDijet3ParamBinPdf& other,
      const char* name = 0);
   void setTH1Binning(TH1* _Hnominal);
   void setAbsTol(double _absTol);
   void setRelTol(double _relTol);
   virtual TObject* clone(const char* newname) const { return new RooModDijet3ParamBinPdf(*this,newname); }
   inline virtual ~RooModDijet3ParamBinPdf() { }

   Int_t getAnalyticalIntegral(RooArgSet& allVars, RooArgSet& analVars, const char* rangeName=0) const;
   Double_t analyticalIntegral(Int_t code, const char* rangeName=0) const;

protected:   

   RooRealProxy th1x;        // dependent variable
   RooRealProxy p1;       // p1
   RooRealProxy p2;        // p2
   RooRealProxy sqrts;        // sqrts
   RooRealProxy meff;        // meff
   RooRealProxy seff;        // seff
   Int_t xBins;        // X bins
   Double_t xArray[2000]; // xArray[xBins+1]
   Double_t xMax;        // X max
   Double_t xMin;        // X min
   Double_t relTol;      //relative tolerance for numerical integration
   Double_t absTol;      //absolute tolerance for numerical integration

   Double_t evaluate() const;
private:
   ClassDef(RooModDijet3ParamBinPdf,1) // RazorDijet3ParamBinPdf function
    
};
//---------------------------------------------------------------------------
#endif

#include "Math/IFunction.h"
#include "Math/IParamFunction.h"
 
class ModDijet3ParamFunction: public ROOT::Math::IParametricFunctionOneDim
{
private:
   const double *pars;
 
public:
   double DoEvalPar(double x,const double* p) const
   {
     double pdf = pow(1-pow(x/p[0],1.0/3.0),p[1])/pow(x/p[0],p[2]);
     double eff = 1.;
     //if (p[6]>0) eff = 0.5 * (1.0 + TMath::Erf((x - p[5])/p[6])) ; // Error function
     if (p[4]>0) eff = 1.0/(1.0 + exp(-2.4*(x - p[3])/p[4])) ; // Sigmoid function
     return pdf*eff;
   }
   
   double DoEval(double x) const
   {
     double pdf = pow(1-pow(x/pars[0],1.0/3.0),pars[1])/pow(x/pars[0],pars[2]);
     double eff = 1.;
     //if (pars[6]>0) eff = 0.5 * (1.0 + TMath::Erf((x - pars[5])/pars[6])); // Error function     
     if (pars[4]>0) eff = 1.0/(1.0 + exp(-2.4*(x - pars[3])/pars[4])); // Sigmoid function
     return pdf*eff;
   }
 
   ROOT::Math::IBaseFunctionOneDim* Clone() const
   {
      return new ModDijet3ParamFunction();
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

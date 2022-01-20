# CMSAnalysis-Diphotons
Supports the both Asymptotic and Hybrid New CLs computations. Native to CMSSW_11_1_0_pre7 (for RDF functionality).

# Setup Scripts and Combine

cd to where you want to setup your CMSSW, then do the following

```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_11_1_0_pre7
cd CMSSW_11_1_0_pre7/src
cmsenv
git clone https://github.com/osherson/CMSAnalysis-Diphotons.git
git clone -b dijetpdf_102X https://github.com/RazorCMS/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
scramv1 b clean; scramv1 b
```

Now setup the RooParametricShapeBinPdfs needed for the analysis:

```
cd $CMSSW_BASE/src
cmsenv
cp CMSAnalysis-Diphotons/FunctionDefs/RooDijet5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src
cp CMSAnalysis-Diphotons/FunctionDefs/RooModDijet5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src

cp CMSAnalysis-Diphotons/FunctionDefs/RooDijet5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface
cp CMSAnalysis-Diphotons/FunctionDefs/RooModDijet5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface

cp CMSAnalysis-Diphotons/FunctionDefs/RooAtlas5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src
cp CMSAnalysis-Diphotons/FunctionDefs/RooAtlas5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface

cd HiggsAnalysis/CombinedLimit/src
```
In the HiggsAnalysis/CombinedLimit/src folder modify the following files:

``` classes.h ```: add the following lines:  
```
#include "HiggsAnalysis/CombinedLimit/interface/RooAtlas5ParamBinPdf.h"
#include "HiggsAnalysis/CombinedLimit/interface/RooModDijet5ParamBinPdf.h"
```

```classes_def.xml```: add the following lines:  	
```
<class name="RooAtlas5ParamBinPdf" /> 
<class name="RooModDijet5ParamBinPdf" /> 
```

Now run

```
cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit 
scramv1 b clean; scramv1 b
```

# Setup CombineHarvester (needed for Grid submissions)

To setup CombineHarvester, do:

```
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b
```

# Creating your working trees:
The "treemaker" can be found at 
```
cd $CMSSW_BASE/src/
```
and might be run (for a single dataset or signal file) like this:
```
import Treemaker
Treemaker.Treemaker("path_to_flat_trees", "name", bool-"is_this_data", "year")
```
This will automatically create 10% and Full versions of datasets, and nominal and up/down sys trees for MCs.

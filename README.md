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

To setup CombineHarvester (will only work on lxplus, so don't bother on hexfarm), do:

```
cd $CMSSW_BASE/src
git clone https://github.com/cms-analysis/CombineHarvester.git CombineHarvester
scram b
```

# Creating your working trees:

## Modifying NanoAOD Tools

First we need to change a few lines in NanoAODTools to accomodate our picoTrees. Step 1 is to checkout Nanoaod tools:
```
cd $CMSSW_BASE/src
git clone https://github.com/cms-nanoAOD/nanoAOD-tools.git PhysicsTools/NanoAODTools
cd PhysicsTools/NanoAODTools
cmsenv
scram b
```
Now open the file PhysicsTools/NanoAODTools/python/postprocessing/modules/common/puWeightProducer.py . Modify line 18 so that it now says:
```
nvtx_var="pvtx_size",
```
and modify line 81 so that it now says:
```
inputFile.Get("pico_nom").Project("autoPU",
```

Next, open PhysicsTools/NanoAODTools/python/postprocessing/framework/output.py . Modify line 144 so that it now says:
```
if kn == "Events" or kn == "pico_nom":
```
and modify line 151 so that it now says:
```
elif kn in ("LuminosityBlocks", "Runs", "pico_scale_up", "pico_scale_down"):
```

Lastly, open PhysicsTools/NanoAODTools/python/postprocessing/framework/postprocessor.py. Modify line 164 so that it now says: 
```
inTree = inFile.Get("pico_nom")
```
and modify  line 185 so that it now says:
```
inAddTree = inAddFiles[-1].Get("pico_nom")
```

## Our Treemaker

The "treemaker" can be found at 
```
cd $CMSSW_BASE/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/
```
to make pico trees for all years of data and signal:
```
cd ProcessTreemaker/
cmsenv
./MakeAllTrees.sh
```
This will automatically create 10% and Full versions of datasets, and nominal and up/down sys trees for MCs. This will start 6 condor jobs, the 3 signal jobs should finish in a matter of a few hours,
the data will take about a day.

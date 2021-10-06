# CMSAnalysis
Scripts used for the CMS EXO-21-010 analysis. Supports the both Asymptotic and Hybrid New CLs computations. Native to CMSSW_11_0_0_pre2 (for RDF functionality).


# Setup Scripts and Combine

cd to where you want to setup your CMSSW, then do the following

```
export SCRAM_ARCH=slc7_amd64_gcc700
cmsrel CMSSW_11_0_0_pre2
cd CMSSW_11_0_0_pre2/src
cmsenv
git clone https://github.com/tw-hu/CMSAnalysis CMSAnalysis
git clone -b dijetpdf_102X https://github.com/RazorCMS/HiggsAnalysis-CombinedLimit HiggsAnalysis/CombinedLimit
cd HiggsAnalysis/CombinedLimit

cd $CMSSW_BASE/src/HiggsAnalysis/CombinedLimit
scramv1 b clean; scramv1 b
```

Now setup the RooParametricShapeBinPdfs needed for the analysis:

```
cd $CMSSW_BASE/src
cmsenv
cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/cc_files/RooDijet5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src
cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/cc_files/RooModDijet5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src

cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/h_files/RooDijet5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface
cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/h_files/RooModDijet5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface

cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/cc_files/RooAtlas5ParamBinPdf.cc HiggsAnalysis/CombinedLimit/src
cp /afs/cern.ch/user/d/dntounis/public/RooParametricShapeBinPdf_classes/February_2021/classes/h_files/RooAtlas5ParamBinPdf.h HiggsAnalysis/CombinedLimit/interface

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

# Setup File Dependencies

Skip this step if the current directory is on the Rutgers Hexfarm, the Run-II signals are in the /cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/ directory, and the Run-II data are in the /cms/xaastorage-2/PicoTrees/4JETS/201*/v6/Athens/ directories (see below).

Otherwise, modify the picotree directories in the following python scripts:
```
$CMSSW_BASE/src/CMSAnalysis/DijetRootTreeAnalyzer/python/MakeSignal.py
$CMSSW_BASE/src/CMSAnalysis/DijetRootTreeAnalyzer/python/MakeBackground.py
```

After the setup, do:
```
cd $CMSSW_BASE/src/CMSAnalysis/DijetRootTreeAnalyzer/
```

# Preparing Workspaces

It is recommended that this step be done on Hexfarm where all the picotrees are located. The output ROOT files can then be scp'ed onto lxplus.

To produce RPV signals, do
```
python python/MakeSignal.py --massrange 500 3000 25 --normalize --no4J --trim
```
The command above creates an RPV signal every 25 GeV from 500 GeV to 3000 GeV, binned in 1 GeV bins, and normalized. The script uses the vertical template morphing technique inplemented by ROOT's ```RooIntegralMorph``` to create interpolated templates at masses for which a picotree is unavailable. The option ```--no4J``` refers to the newest selection criteria without the four-jet mass cut. The option ```--trim``` removes bins with one MC event before normalizing. More options can be found by running:
```
python python/MakeSignal.py -h
```

To produce QCD MC background, do
```
python python/MakeBackground.py -y II --no4J
```
Option descriptions can be found by running
```
python python/MakeBackground.py -h
```

# Fitting and Creating Datacards

To run a fit, do:

```
python python/RunFitter.py -f atlas --no4J
```
Other valid choices of parametrization are ```dijet```, ```moddijet```, and ```combine```. In particular, this should be run with the option ```-f combine``` to generate datacards for the envelope method. This step must be done prior to generating any datacard.

To create datacards for individual fits, do:
```
python python/RunDataCardMaker.py -f atlas --no4J
```

To create datacards for the envelope method, do:
```
python python/RunDataCardMakerJim.py --no4J
```
Note that the Asymptotic and Hybrid New CLs computations share the same datacards.

# Computing Asymptotic CLs

To compute Asymptotic CLs, do:

```
python python/PlotLimitsAsymptotic.py -f atlas --massrange 500 3000 25
```
Other valid choices of parametrization are ```dijet```, ```moddijet```, and ```envelope```.

# Computing HybridNew CLs

This step must be done on lxplus. It is recommended that the signals and data be generated locally on Hexfarm, then scp'ed onto lxplus. Signal/data ROOT files should be copied into the ```input/``` folder. After this is done, the fits and datacards should be re-made (see above).

Once this is done, do:
```
./run_produce_workspaces.sh
```
To run the grid submissions, do:
```
./run_grid_submissions_HybridNew_limits_v3.sh
```
To see the status of submitted jobs, do:
```
./run_status_grid_jobs_HybridNew_limits.sh
```
To resubmit jobs (if the status indicates they have failed), do:
```
./run_resubmit_grid_jobs_HybridNew_limits.sh
```
This step only resubmits failed jobs.

To kill submitted jobs, do:
```
./run_kill_grid_jobs_HybridNew.sh
```

Once all jobs are done, get output from EOS area to premade output directory and untar into ROOT files:
```
./run_getoutput_from_grid_jobs.sh
./run_untar_hadd_grid_jobs.sh
```
Calculate HybridNew Limits by running (for the 500 GeV RPV, for example):
```
./run_calculate_limits_HybridNew.sh 500
```
This step takes upwards to two hours to complete, depending on the signal mass, so it is suggested that multiple screens be used to process all the masses. Once this is done, do
```
python python/PlotLimitsHybridNew.py -f atlas --massrange 500 3000 25
```




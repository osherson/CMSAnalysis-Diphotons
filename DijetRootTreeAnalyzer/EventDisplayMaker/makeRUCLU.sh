#!/bin/bash

cd /cms/sclark/Production_Ruclu/CMSSW_10_6_14/src/ml_photons_cmssw/ml_photons/python/Clusterizer/cluster_general/
./call.sh $1 $2 $3 $4 $5
mv out.root /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/EventDisplayMaker/.
mv outflat.root /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/EventDisplayMaker/.
cd /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/EventDisplayMaker
cmsenv
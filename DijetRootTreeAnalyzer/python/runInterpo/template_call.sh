#!/bin/bash

cluster=$1
process=$2

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
export CMSSW_GIT_REFERENCE=/cvmfs/cms.cern.ch/cmssw.git
export HOME=/cms/sclark/

cd /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/python/runInterpo
eval `scramv1 runtime -sh`

while IFS= read -r line; do
  $line

done < SingleFiles/single.ext

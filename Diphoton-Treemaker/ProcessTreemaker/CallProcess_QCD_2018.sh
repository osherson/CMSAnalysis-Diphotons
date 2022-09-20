#!/bin/bash

cluster=$1
process=$2

export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch
source $VO_CMS_SW_DIR/cmsset_default.sh
export SCRAM_ARCH=slc7_amd64_gcc700
export CMSSW_GIT_REFERENCE=/cvmfs/cms.cern.ch/cmssw.git
export HOME=/cms/sclark/

myd=$CMSSW_BASE/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/ProcessTreemaker
cd $myd

eval `scramv1 runtime -sh`

python ProcessQCD.py 2018

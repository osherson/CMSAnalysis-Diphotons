## Untar and hadd root files for *final* limits with HybridNew for RPV masses of 500 GeV and above (up to 3 TeV)
## August 2021

rpv=(500 600 700 800 900 1000 1250 1500 1750 2000 2500 3000)

for element1 in "${rpv[@]}"
do
   
rpv=$element1
echo $rpv

source /cvmfs/cms.cern.ch/crab3/crab.sh 
eval `scramv1 runtime -sh` #equivalent to cmsenv

cd $CMSSW_BASE/src/CMSDIJET/DijetRootTreeAnalyzer/HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv"/results


for f in *.tar; do tar xf $f; done


hadd -f limits_3_slices_Envelope_3_func_M"$rpv"_merged.root `ls higgsCombine.Test.POINT.*.HybridNew.mH125.*`

done


## Calculate *final* limits with HybridNew for RPV masses of 500 GeV and above (up to 3 TeV)
## Argument one in command line provides the mass of the signal
## It is recommended that the user create separate screens for each mass point, since each point takes up to an hour to run
## August 2021

echo $1
  
source /cvmfs/cms.cern.ch/crab3/crab.sh 
eval `scramv1 runtime -sh` #equivalent to cmsenv

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_observed.png -n limits_M$1 --rAbsAcc 0.00001 

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_median_expected.png --expectedFromGrid 0.5 -n limits_M$1 --rAbsAcc 0.00001 

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_expected_minus_one_sigma.png --expectedFromGrid 0.16 -n limits_M$1 --rAbsAcc 0.00001 

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_expected_plus_one_sigma.png --expectedFromGrid 0.84 -n limits_M$1 --rAbsAcc 0.00001 

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_expected_minus_two_sigma.png --expectedFromGrid 0.025 -n limits_M$1 --rAbsAcc 0.00001 

combine output/Full_envelope_M$1.txt -M HybridNew --LHCmode LHC-limits --readHybridResults --grid=HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M$1/results/limits_3_slices_Envelope_3_func_M$1_merged.root -m 125 --cminDefaultMinimizerStrategy=0 --plot=limit_scan_M$1_expected_plus_two_sigma.png --expectedFromGrid 0.975 -n limits_M$1 --rAbsAcc 0.00001 


hadd -f higgsCombine_M$1.HybridNew.mH120.root higgsCombinelimits_M$1.HybridNew.mH125.quant0.025.root higgsCombinelimits_M$1.HybridNew.mH125.quant0.160.root higgsCombinelimits_M$1.HybridNew.mH125.quant0.500.root higgsCombinelimits_M$1.HybridNew.mH125.quant0.840.root higgsCombinelimits_M$1.HybridNew.mH125.quant0.975.root higgsCombinelimits_M$1.HybridNew.mH125.root
  
# done


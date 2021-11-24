## Copy files from EOS to CMSSW area for *final* limits with HybridNew for RPV masses of 500 GeV and above (up to 3 TeV)
## August 2021

#rpv=(500 600 700 800 900 1000 1250 1500 1750 2000 2500 3000)
# rpv=(500 525 550 575 600 625 650 675 700 725 750 775 800 825 850 875 900 925 950 975 1000 1025 1050 1075 1100 1125 1150 1175 1200 1225 1525 1550 1575 1600 1625 1650 1675 1700 1725 1750 1775 1800 1825 1850 1875 1900 1925 1950 1975 2000 2025 2050 2075 2100 2125 2150 2175 2200 2225 2250 2275 2300 2325 2350 2375 2400 2425 2450 2475 2500 2525 2550 2575 2600 2625 2650 2675 2700 2725 2750 2775 2800 2825 2850 2875 2900 2925 2950 2975 3000)
rpv=(500 525 550 575 600 625 650 675 700 725 750 775 800 825 850 875 900 925 950 975 1000 1050 1100 1150 1200 1250 1300 1350 1400 1450 1500 1550 1600 1650 1700 1750 1800 2000 2200 2400 2600 2800 3000)

for element1 in "${rpv[@]}"
do

rpv=$element1
echo $rpv

source /cvmfs/cms.cern.ch/crab3/crab.sh 
eval `scramv1 runtime -sh` #equivalent to cmsenv

crab getoutput HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv" --jobids 1-500 --checksum=no
crab getoutput HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv" --jobids 501-1000 --checksum=no
crab getoutput HybridNew_RPV/crab_final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv" --jobids 1001-1020 --checksum=no

done


## Grid submissions for *final* limits with HybridNew for RPV masses of 500 GeV and above (up to 3 TeV)
## August 2021

rpv=(500 600 700 800 900 1000 1250 1500 1750 2000 2500 3000)

for element1 in "${rpv[@]}"
do

rpv=$element1
echo $rpv

source /cvmfs/cms.cern.ch/crab3/crab.sh 
eval `scramv1 runtime -sh` #equivalent to cmsenv


if [ $rpv == 500 ]
then
max=6.300
elif [ $rpv == 600 ] 
then 
max=3.000
elif [ $rpv == 700 ] 
then
max=1.700
elif [ $rpv == 800 ] 
then
max=1.100
elif [ $rpv == 900 ] 
then
max=0.850
elif [ $rpv == 1000 ] 
then
max=0.750
elif [ $rpv == 1250 ] 
then
max=0.250
elif [ $rpv == 1500 ] 
then
max=0.1000
elif [ $rpv == 1750 ] 
then
max=0.050
elif [ $rpv == 2000 ] 
then
max=0.030
elif [ $rpv == 2500 ] 
then
max=0.020
else
max=0.015
fi

stepsize=$(echo "scale=7;   (0.005*$max)/1" | bc  )
rmax=$(echo "scale=3; (4*$max)/1" | bc  )

   combineTool.py -d output/workspace_combined_"$rpv".root -M HybridNew -v -1 --LHCmode LHC-limits --clsAcc 0 -T 200 -i 10 -s 10148:10152:1 --singlePoint 0.0:$max:$stepsize --rMax "$rmax" --saveToys --saveHybridResult -m 125 --job-mode crab3 --task-name final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv" --custom-crab custom_crab_final_limits.py 

   # combineTool.py -d output/workspace_combined_"$rpv".root -M HybridNew -v -1 --LHCmode LHC-limits --clsAcc 0 -T 1 -i 10 -s 10148:10152:1 --singlePoint 0.0:$max:$stepsize --rMax "$rmax" --saveToys --saveHybridResult -m 125 --job-mode crab3 --task-name final_hybridNew_limits_3_slices_Envelope_3_func_M"$rpv" --custom-crab custom_crab_final_limits.py 

unset max
unset stepsize
unset rmax

done
## Merges RooWorkspace with Datacard used in the other shell scripts for *final* limits with HybridNew for RPV masses of 500 GeV and above (up to 3 TeV)
## August 2021

rpv=(500 600 700 800 900 1000 1250 1500 1750 2000 2500 3000)

for element1 in "${rpv[@]}"
do

rpv=$element1  
echo $rpv

text2workspace.py output/Full_envelope_M"$rpv".txt -o output/workspace_combined_"$rpv".root

   
done

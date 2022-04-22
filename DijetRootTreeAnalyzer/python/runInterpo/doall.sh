echo "Deleting condor_logfiles"
rm condor_logfiles/*
echo "Deleting CallFiles"
rm CallFiles/*
echo "Making Interpo Script"
python interpSignalScriptProducer.py $1
echo "Splitting"
split -a 4 -d --lines=1 InterpoProducerScript.sh single.
echo "Making CallFiles"
python makeCalls.py
chmod +x CallFiles/*
echo "Moving Singles"
mv single* SingleFiles/.
narg="$(wc -l < InterpoProducerScript.sh)"
sed -i "s/ Queue.*/ Queue $narg/g" runCondor.jdl

echo "Deleting condor_logfiles"
rm condor_logfiles/*
echo "Deleting CallFiles"
rm CallFiles/*
echo "Deleting SingleFiles"
rm SingleFiles/*
echo "Making Interpo Script"
python interpSignalScriptProducer.py $1
echo "Splitting"
split -a 5 -d --lines=10 InterpoProducerScript.sh single.
#split -a 3 -d --lines=1 InterpoProducerScript.sh single.
echo "Making CallFiles"
python makeCalls.py
chmod +x CallFiles/*
echo "Moving Singles"
mv single* SingleFiles/.
#narg="$(wc -l < InterpoProducerScript.sh)"
narg="$(ls CallFiles/* | wc -l)"
echo $narg
sed -i "s/ Queue.*/ Queue $narg/g" runCondor.jdl

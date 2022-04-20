rm condor_logfiles/*
split -a 4 -d --lines=1 InterpoProducerScript.sh single.
python makeCalls.py
chmod +x Call*

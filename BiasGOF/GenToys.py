#
import ROOT
import sys
import os
import htcondor

C = sys.argv[1]
D = os.path.dirname(C)
N = os.path.basename(C).split(".")[0]

# N = C.split(".")[0]

os.system("combine "+C+" -M AsymptoticLimits ")
F = ROOT.TFile("higgsCombineTest.AsymptoticLimits.mH120.root")
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(3)
sig = T.limit - exp

if not os.path.exists(D + "/condor_logfiles"): os.makedirs(D + "/condor_logfiles")

combine_job = htcondor.Submit({
		"universe": "vanilla",
		"initialdir": ".",
		"executable": "Gen.sh",
					"getenv": "True",	# the program to run on the execute node
		"arguments": C +" 0 " + N + "r0",
		"output": D +"/condor_logfiles/" + N + "_G0.out",		# anything the job prints to standard output will end up in this file
		"error": D +"/condor_logfiles/" + N + "_G0.err",		# anything the job prints to standard error will end up in this file
		"log": D +"/condor_logfiles/" + N + "_G0.log",		  	# this file will contain a record of what happened to the job
		"Notification": "never"
	})
print(combine_job)	
schedd = htcondor.Schedd()		  # get the Python representation of the scheduler
with schedd.transaction() as txn:   # open a transaction, represented by `txn`
	cluster_id = combine_job.queue(txn)		
	print(cluster_id)

print "Expected Limit = " + str(exp) + ", 1sigma = " + str(sig)



for r in [1, 2, 3, 5]:
	combine_job = htcondor.Submit({
		"universe": "vanilla",
		"initialdir": ".",
		"executable": "Gen.sh",
					"getenv": "True",	# the program to run on the execute node
		"arguments": C +" "+str(exp + (r*sig))+" " + N + "re"+str(r),
		"output": D +"/condor_logfiles/" + N + "_Ge"+str(r)+".out",		# anything the job prints to standard output will end up in this file
		"error": D +"/condor_logfiles/" + N + "_Ge"+str(r)+".err",		# anything the job prints to standard error will end up in this file
		"log": D +"/condor_logfiles/" + N + "_Ge"+str(r)+".log",		  	# this file will contain a record of what happened to the job
		"Notification": "never"
	})
	print(combine_job)	
	schedd = htcondor.Schedd()		  # get the Python representation of the scheduler
	with schedd.transaction() as txn:   # open a transaction, represented by `txn`
		cluster_id = combine_job.queue(txn)		
		print(cluster_id)


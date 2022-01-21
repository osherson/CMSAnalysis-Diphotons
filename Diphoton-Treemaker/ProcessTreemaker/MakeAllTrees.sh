#!/bin/bash

thisdir=$PWD

#Delete condor logfiles
if ls $PWD/condor_logfiles/*/* 1> /dev/null 2>&1; then
  echo "Removing Condor Logfiles"
  rm $PWD/condor_logfiles/*/*.stderr
  rm $PWD/condor_logfiles/*/*.stdout
  rm $PWD/condor_logfiles/*/*.condor
fi

#Move into Output directory
cd /cms/xaastorage-2/DiPhotonsTrees/ 

#If there are already root files, move them into a folder titled c_date-time
if ls *.txt 1> /dev/null 2>&1; then
      sdate=$(cat dateMade.txt) #Read the text file, one line that contains date it was made
      mkdir v_$sdate #make a directory titled v_date , mv all files into that directory
      mv *.root v_$sdate/.
      mv dateMade.txt v_$sdate/.
      echo "Moving existing files into v_$sdate"
fi

today=`date +"%Y-%m-%d-%T"` 
echo "$today" >> dateMade.txt #Create new text file with todays date & time

#Back to this directory
cd $thisdir

#submit everything via condor
condor_submit runCondor_Signal_2016.jdl
condor_submit runCondor_Signal_2017.jdl
condor_submit runCondor_Signal_2018.jdl
condor_submit runCondor_Data_2016.jdl
condor_submit runCondor_Data_2017.jdl
condor_submit runCondor_Data_2018.jdl

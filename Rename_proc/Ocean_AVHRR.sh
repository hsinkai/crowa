#!/bin/bash
mmdd=`date +%m%d`
LOG=/home/crsadm/log/Ocean_AVHRR.${mmdd}00

echo "`date` [fork] $1" >> $LOG


/home/crsadm/bin/sat2csv/read_sst.exe $1 /home/crsadm/bin/sat2csv/sst_lookuptab.txt ./ /CRSdata/dataPool/Ocean/AVHRR_tmp/sst.txt >> /home/crsadm/log/Ocean_AVHRR_read_sst.log

echo "/home/crsadm/bin/sat2csv/read_sst.exe $1 /home/crsadm/bin/sat2csv/sst_lookuptab.txt ./ /CRSdata/dataPool/Ocean/AVHRR_tmp/sst.txt" >> $LOG

echo "`date` [finish] $1" >> $LOG


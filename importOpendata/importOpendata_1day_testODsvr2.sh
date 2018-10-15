#!/bin/bash

apikey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
#importPath="/CRSdata/dataIn/OPENDATA"
importPath="/CRSdata/dataTmp/OpenDataBackup_odsvr2"

cd $importPath


# 1 day
wget --no-proxy -O F-A0021-001.xml "http://odsvr2.cwb.gov.tw:8080/opendataapi?dataid=F-A0021-001&authorizationkey=$apikey"

check_dataid=`grep dataid /CRSdata/dataTmp/OpenDataBackup_odsvr2/F-A0021-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_A0021" ]; then
  echo "[Warning] F-A0021-001.xml get $check_dataid"
  cp $importPath/F-A0021-001.xml /CRSdata/dataTmp/OpenDataBackup_odsvr2/F-A0021-001.xml.$(date +"%Y%m%d%H%M%S")
fi


wget --no-proxy -O C-B0024-001.xml "http://odsvr2.cwb.gov.tw:8080/opendataapi?dataid=C-B0024-001&authorizationkey=$apikey"

check_dataid=`grep dataid /CRSdata/dataTmp/OpenDataBackup_odsvr2/C-B0024-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_B0024" ]; then
  echo "[Warning] C-B0024-001.xml get $check_dataid"
  cp $importPath/C-B0024-001.xml /CRSdata/dataTmp/OpenDataBackup_odsvr2/C-B0024-001.xml.$(date +"%Y%m%d%H%M%S")
fi



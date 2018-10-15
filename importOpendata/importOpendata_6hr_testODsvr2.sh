#!/bin/bash

apikey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
#importPath="/CRSdata/dataIn/OPENDATA"
importPath="/CRSdata/dataTmp/OpenDataBackup_odsvr2"

cd $importPath


# 6 hour
wget --no-proxy -O F-A0012-001.xml "http://odsvr2.cwb.gov.tw:8080/opendataapi?dataid=F-A0012-001&authorizationkey=$apikey"


check_dataid=`grep dataid /CRSdata/dataTmp/OpenDataBackup_odsvr2/F-A0012-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "A0012-001" ]; then
  echo "[Warning] F-A0012-001.xml get $check_dataid"
  cp $importPath/F-A0012-001.xml /CRSdata/dataTmp/OpenDataBackup_odsvr2/F-A0012-001.xml.$(date +"%Y%m%d%H%M%S")
fi



apikey="CWB-265F14F2-8862-4E28-B43F-73E46878F031"
importPath="/CRSdata/dataTmp/OpenDataBackup_datareco5"

cd $importPath

# 6 hour
wget --no-proxy -O F-A0012-001.xml "http://61.56.15.204:8080/OpendataWebProject2/opendataapi?dataid=F-A0012-001&authorizationkey=$apikey"

check_dataid=`grep dataid /CRSdata/dataTmp/OpenDataBackup_datareco5/F-A0012-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "A0012-001" ]; then
  echo "[Warning] F-A0012-001.xml get $check_dataid"
  cp $importPath/F-A0012-001.xml /CRSdata/dataTmp/OpenDataBackup_datareco5/F-A0012-001.xml.$(date +"%Y%m%d%H%M%S")
fi


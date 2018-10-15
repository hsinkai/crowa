#!/bin/bash

apikey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
importPath="/CRSdata/dataIn/OPENDATA"
binPath="/home/crsadm/bin/importOpendata"

cd $importPath


# 1 day
#wget --no-proxy -O F-A0021-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=F-A0021-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O F-A0021-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=F-A0021-001&Authorization=$apikey&format=XML"
#----------------------------
# V3, add etag checking
#----------------------------
/usr/bin/python $binPath/importOpendata.py --dataid=F-A0021-001 --target=$importPath --format=xml


check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/F-A0021-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_A0021" ]; then
  echo "[Warning] F-A0021-001.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/F-A0021-001.xml /CRSdata/dataTmp/OpenDataBackup/F-A0021-001.xml.$(date +"%Y%m%d%H%M%S")
fi


#wget --no-proxy -O C-B0024-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=C-B0024-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O C-B0024-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=C-B0024-001&Authorization=$apikey&format=XML"
#----------------------------
# V3, add etag checking
#----------------------------
/usr/bin/python $binPath/importOpendata.py --dataid=C-B0024-001 --target=$importPath --format=xml


check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/C-B0024-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_B0024" ]; then
  echo "[Warning] C-B0024-001.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/C-B0024-001.xml /CRSdata/dataTmp/OpenDataBackup/C-B0024-001.xml.$(date +"%Y%m%d%H%M%S")
fi



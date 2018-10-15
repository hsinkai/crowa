#!/bin/bash

apikey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
importPath="/CRSdata/dataIn/OPENDATA"
binPath="/home/crsadm/bin/importOpendata"

cd $importPath


# 10 min
#wget --no-proxy -O O-A0018-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0018-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O O-A0018-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=O-A0018-001&Authorization=$apikey&format=XML"
#----------------------------
# V3, add etag checking
#----------------------------
/usr/bin/python $binPath/importOpendata.py --dataid=O-A0018-001 --target=$importPath --format=xml


check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/O-A0018-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_A0018" ]; then
  echo "[Warning] O-A0018-001.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/O-A0018-001.xml /CRSdata/dataTmp/OpenDataBackup/O-A0018-001.xml.$(date +"%Y%m%d%H%M%S")
fi


#wget --no-proxy -O O-A0001-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0001-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O O-A0001-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=O-A0001-001&Authorization=$apikey&format=XML"
#----------------------------
# V3, add etag checking
#----------------------------
/usr/bin/python $binPath/importOpendata.py --dataid=O-A0001-001 --target=$importPath --format=xml


check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/O-A0001-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_A0001" ]; then
  echo "[Warning] O-A0001-001.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/O-A0001-001.xml /CRSdata/dataTmp/OpenDataBackup/O-A0001-001.xml.$(date +"%Y%m%d%H%M%S")
fi


#wget --no-proxy -O O-A0003-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0003-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O O-A0003-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=O-A0003-001&Authorization=$apikey&format=XML"
#----------------------------
# V3, add etag checking
#----------------------------
/usr/bin/python $binPath/importOpendata.py --dataid=O-A0003-001 --target=$importPath --format=xml

check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/O-A0003-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" != "CWB_A0003" ]; then
  echo "[Warning] O-A0003-001.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/O-A0003-001.xml /CRSdata/dataTmp/OpenDataBackup/O-A0003-001.xml.$(date +"%Y%m%d%H%M%S")
fi


#wget --no-proxy -O O-A0017-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0017-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O O-A0017-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=O-A0017-001&Authorization=$apikey&format=XML"

#check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/O-A0017-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
#echo $check_dataid
#if [ "$check_dataid" != "CWB_A0017" ]; then
#  echo "[Warning] O-A0017-001.xml get $check_dataid"
#  cp /CRSdata/dataIn/OPENDATA/O-A0017-001.xml /CRSdata/dataTmp/OpenDataBackup/O-A0017-001.xml.$(date +"%Y%m%d%H%M%S")
#fi


#wget --no-proxy -O O-A0019-001.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=O-A0019-001&authorizationkey=$apikey"
#wget --no-check-certificate --no-proxy -O O-A0019-001.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=O-A0019-001&Authorization=$apikey&format=XML"

#check_dataid=`grep dataid /CRSdata/dataIn/OPENDATA/O-A0019-001.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
#echo $check_dataid
#if [ "$check_dataid" != "CWB_A0019" ]; then
#  echo "[Warning] O-A0019-001.xml get $check_dataid"
#  cp /CRSdata/dataIn/OPENDATA/O-A0019-001.xml /CRSdata/dataTmp/OpenDataBackup/O-A0019-001.xml.$(date +"%Y%m%d%H%M%S")
#fi




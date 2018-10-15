#!/bin/bash

apikey="CWB-53E33035-16C6-410B-B2A0-C0A2159BF783"
importPath="/CRSdata/dataIn/OPENDATA"
binPath="/home/crsadm/bin/importOpendata"

cd $importPath

# 不定期
#----------------------------
#V1
#----------------------------
#wget --no-proxy -O CWBEQ.xml "http://opendata.cwb.gov.tw/govdownload?dataid=E-A0015-001R&authorizationkey=rdec-key-123-45678-011121314"
#wget --no-proxy -O W-C0034-001.cap "http://opendata.cwb.gov.tw/opendataapi?dataid=W-C0034-001&authorizationkey=$apikey"
#wget --no-proxy -O W-C0034-002.kmz "http://opendata.cwb.gov.tw/opendataapi?dataid=W-C0034-002&authorizationkey=$apikey"
#wget --no-proxy -O W-C0034-003.kmz "http://opendata.cwb.gov.tw/opendataapi?dataid=W-C0034-003&authorizationkey=$apikey"
#wget --no-proxy -O W-C0034-004.xml "http://opendata.cwb.gov.tw/opendataapi?dataid=W-C0034-004&authorizationkey=$apikey"

#----------------------------
#V2
#----------------------------
#wget --no-check-certificate --no-proxy -O CWBEQ.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid==E-A0015-001R&Authorization=$apikey&format=XML"
#wget --no-check-certificate --no-proxy -O CWBEQ.zip "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=E-A0015-001&Authorization=CWB-53E33035-16C6-410B-B2A0-C0A2159BF783&format=ZIP"
#wget --no-check-certificate --no-proxy -O CWBEQ.xml "https://opendata.cwb.gov.tw/govdownload?dataid=E-A0015-001R&authorizationkey=rdec-key-123-45678-011121314"

#wget --no-check-certificate --no-proxy -O W-C0034-001.cap "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=W-C0034-001&Authorization=$apikey&format=CAP"
#wget --no-check-certificate --no-proxy -O W-C0034-002.kmz "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=W-C0034-002&Authorization=$apikey&format=KMZ"
#wget --no-check-certificate --no-proxy -O W-C0034-003.kmz "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=W-C0034-003&Authorization=$apikey&format=KMZ"
#wget --no-check-certificate --no-proxy -O W-C0034-004.xml "https://opendata.cwb.gov.tw/fileapi/v1/opendataapi?dataid=W-C0034-004&Authorization=$apikey&format=XML"

#----------------------------
# V3, add etag checking
#----------------------------
# 地震報告
/usr/bin/python $binPath/importGovdata.py --dataid=E-A0015-001R --target=$importPath --format=xml
cp $importPath/E-A0015-001R.xml $importPath/CWBEQ.xml

# 颱風警報單CAP
/usr/bin/python $binPath/importOpendata.py --dataid=W-C0034-001 --target=$importPath --format=cap
# 颱風消息-路徑潛勢
/usr/bin/python $binPath/importOpendata.py --dataid=W-C0034-002 --target=$importPath --format=kmz
unzip -o W-C0034-002.kmz
# 颱風消息-侵襲機率
/usr/bin/python $binPath/importOpendata.py --dataid=W-C0034-003 --target=$importPath --format=kmz
unzip -o W-C0034-003.kmz
/usr/bin/python $binPath/importOpendata.py --dataid=W-C0034-004 --target=$importPath --format=xml



#unzip -o W-C0034-002.kmz
#unzip -o W-C0034-003.kmz



check_dataid=`grep earthquakeNo /CRSdata/dataIn/OPENDATA/CWBEQ.xml | cut -d '>' -f 2 | cut -d '<' -f 1`
echo $check_dataid
if [ "$check_dataid" == "106000" ]; then
  echo "[Warning] CWBEQ.xml get $check_dataid"
  cp /CRSdata/dataIn/OPENDATA/CWBEQ.xml /CRSdata/dataTmp/OpenDataBackup/CWBEQ.xml.$(date +"%Y%m%d%H%M%S")
fi


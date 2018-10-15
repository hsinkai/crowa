#!/bin/bash

echo `date`: >> /home/crsadm/log/csv2db/$1.`date +%Y%m%d`

/package/python-2.7.3/bin/python2.7 /home/crsadm/bin/dbImport/xml2csv.py -f $2 -t /home/crsadm/data/xml2csv/$1.csv \
/home/crsadm/cfg/xml2csv/$1.yaml -e

sed -i 's/\+08:00//g' /home/crsadm/data/xml2csv/$1.csv
sed -i 's/\+0800//g' /home/crsadm/data/xml2csv/$1.csv
sed -i 's/<= 1/<=1/g' /home/crsadm/data/xml2csv/$1.csv
sed -i 's/>= 6/>=6/g' /home/crsadm/data/xml2csv/$1.csv
[ $1 == "O3monthly" ] && sed -i 's/\([0-9][0-9][0-9][0-9]\)-\([0-9][0-9]\)/\1\/\2\/01/g' /home/crsadm/data/xml2csv/$1.csv
[ $1 == "StationDaylight" ] && /package/python-2.7.3/bin/python2.7 /home/crsadm/bin/dbImport/stationdaylight.py /home/crsadm/data/xml2csv/$1.csv && mv /home/crsadm/data/xml2csv/$1.csv.bak /home/crsadm/data/xml2csv/$1.csv

mysqlimport -c `head -n1 /home/crsadm/data/xml2csv/$1.csv` -L --replace --fields-optionally-enclosed-by='"' \
--fields-terminated-by="," --lines-terminated-by="\r\n" --ignore-lines=1 CRSdb /home/crsadm/data/xml2csv/$1.csv \
>> /home/crsadm/log/csv2db/$1.`date +%Y%m%d` 2>&1

/home/crsadm/bin/cwsp-1.0/bin/startup.py $1

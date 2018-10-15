#!/bin/bash

echo `date`: >> /home/crsadm/log/csv2db/STCfor_PH.`date +%Y%m%d`

cd /home/crsadm/data

/package/python-2.7.3/bin/python2.7 /home/crsadm/bin/dbImport/ocm2_stcfor.py $1

mysqlimport -L --fields-optionally-enclosed-by='"' --fields-terminated-by="," --lines-terminated-by="\r\n" \
--ignore-lines=1 CRSdb ocm2_stcfor.csv >> /home/crsadm/log/csv2db/STCfor_PH.`date +%Y%m%d`

mysql -ND CRSdb -e "CALL ocm2_to_stcfor;"

rm ocm2_stcfor.csv

#!/bin/bash

timestr=$(echo $1 | sed -rn 's/.*_(.*)_(.*)_(.*)_(.*)_(.*)\.txt/\1-\2-\3 \4:\5:00/p')

echo `date`: >> /home/crsadm/log/csv2db/GT.`date +%Y%m%d`

sed 's/ \+/,/g' $1 > /home/crsadm/data/gt/sevk.txt
tail -n +2 /home/crsadm/data/gt/sevk.txt | grep "B\|I\|J" | awk -v var="$timestr" '{print $1 "," var}' > /home/crsadm/data/gt/GT.txt

mysqlimport -c `head -n1 /home/crsadm/data/gt/sevk.txt`,Time --fields-terminated-by="," --replace -L CRSdb \
/home/crsadm/data/gt/GT.txt >> /home/crsadm/log/csv2db/GT.`date +%Y%m%d`

/home/crsadm/bin/cwsp-1.0/bin/startup.py GT

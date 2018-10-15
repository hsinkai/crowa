#!/bin/sh

for i in /CRSdata/dataIn//MMCDATA/OCM3/ocm3_hvel_201610[0,1]?00_H01_24.nc

do 
echo $i
dirn=`dirname $i`
basen=`basename $i`
zcorn=${basen:0:4}_zcor_${basen:10:20}
echo $zcorn
wd=${basen:10:10}_dir.txt
ws=${basen:10:10}_spd.txt
./read_ocm3_uv_v2.exe $dirn/$zcorn $dirn/$basen colorbar_spd.tab ./ $wd $ws
#./read_ocm3_uv.exe /CRSdata/dataIn//MMCDATA/OCM3/ocm3_zcor_2016100500_H01_24.nc /CRSdata/dataIn//MMCDATA/OCM3/ocm3_hvel_2016100500_H01_24.nc colorbar_spd.tab ./ dir.txt spd.txt

done

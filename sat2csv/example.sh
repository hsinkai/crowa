
./read_ocm3_uv.exe /CRSdata/dataIn/MMCDATA/OCM3/ocm3_zcor_2016110200_H01_24.nc /CRSdata/dataIn/MMCDATA/OCM3/ocm3_hvel_2016110200_H01_24.nc colorbar_spd.tab ./ test_dir.txt test_spd.txt

./read_sst.exe /CRSdata/dataIn/MMCDATA/AVHRR/sst.day.mean.2016.v2.nc sst_lookuptab.txt ./ test_sst.txt

 ~/bin/sat2csv/read_file_v2.exe 201611030540 13 ~/bin/sat2csv/lookup.tab ./ test_sat.txt

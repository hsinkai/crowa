gfortran read_file.f90 -o read_file.exe -ffree-line-length-none
gfortran read_sst.f90 -o read_sst.exe -I/package/netcdf-fortran-4.4.0/include -L/package/netcdf-fortran-4.4.0/lib -lnetcdff -L/package/netcdf-4.4.0/lib -lnetcdf
gfortran read_ocm3_v2.f90 -o read_ocm3.exe -I/package/netcdf-fortran-4.4.0/include -L/package/netcdf-fortran-4.4.0/lib -lnetcdff -L/package/netcdf-4.4.0/lib -lnetcdf
gfortran read_ocm3_uv_v2.f90 -o read_ocm3_uv.exe -I/package/netcdf-fortran-4.4.0/include -L/package/netcdf-fortran-4.4.0/lib -lnetcdff -L/package/netcdf-4.4.0/lib -lnetcdf

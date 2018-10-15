
module read_netcdf_module

contains

  subroutine read_netcdf(FILE_NAME,VARS_NAME,data_out,lats,lons,miss)
  use netcdf
  implicit none
  
  ! This is the name of the data file we will read.
  character (len = *) :: FILE_NAME
  integer :: ncid

  ! timesteps of data.
  !integer, intent(in), optional :: TAU, level
  !integer*8,  intent(in) :: init_time
  !character (len=15) :: init_time_c
  integer :: MNX, MNY, MNT ,MNL, NT, NL, dayhr
  character (len = *), parameter :: LEV_NAME = "lev"
  character (len = *), parameter :: LAT_NAME = "lat"
  character (len = *), parameter :: LON_NAME = "lon"
  character (len = *), parameter :: REC_NAME = "time"

  ! The start and count arrays will tell the netCDF library where to
  ! read our data.
  integer, allocatable :: start(:), count(:)

  real, dimension(:),pointer   :: lats,lons 
  integer, allocatable  :: forecast(:), levs(:)
  integer :: lon_varid, lat_varid, time_varid, lev_varid
  integer :: lon_dimid, lat_dimid, time_dimid, lev_dimid

  ! We will read surface temperature and pressure fields. In netCDF
  ! terminology these are called "variables."
  character (len = *) :: VARS_NAME 
  integer :: vars_varid

  ! We recommend that each variable carry a "units" attribute.
  character (len = *), parameter :: UNITS = "units"
  character (len = *), parameter :: PRES_UNITS = "hPa", TEMP_UNITS = "k"
  character (len = *), parameter :: LAT_UNITS = "degrees_north"
  character (len = *), parameter :: LON_UNITS = "degrees_east"

  ! Program variables to hold the data we will read in. We will only
  ! need enough space to hold one timestep of data; one record.
  ! Allocate memory for data.
  real, dimension(:,:), allocatable :: values
  real, dimension(:,:), pointer :: data_out

  integer :: lvl, lat, lon, rec, i, j ,k
  real :: slat, elat, slon, elon
  integer :: numdim, numattr, status
  real :: maxlat, minlat, maxlon, minlon, dlat, dlon
  !real :: leftlat, rightlat, leftlon, rightlon
  integer , dimension(nf90_max_var_dims) :: latDimIds
  character(len=250) :: timeunit, cmd
  integer :: y,m,d,h,mi,se,timedata
  real,intent(out),optional :: miss

  if(len_trim(FILE_NAME)==0)then
     print *,'NO FILE FOUND'
     stop 2
  endif

  ! Open the file. 
  call check( nf90_open(trim(FILE_NAME), nf90_nowrite, ncid) )

  ! Get the varids of the latitude and longitude coordinate variables.
  call check( nf90_inq_varid(ncid, LAT_NAME, lat_varid) )
  call check( nf90_inq_varid(ncid, LON_NAME, lon_varid) )
  call check( nf90_inq_varid(ncid, REC_NAME, time_varid) )
  status=nf90_inq_varid(ncid, LEV_NAME, lev_varid)

  !call check( nf90_inquire_variable(ncid, lat_varid, dimids =  &
  !     latDimIds(:numlatDims) ) )
  !call check( nf90_get_att(ncid, lat_varid, "maximum", maxlat ) )
  !call check( nf90_get_att(ncid, lat_varid, "minimum", minlat ) )
  !call check( nf90_get_att(ncid, lat_varid, "resolution", dlat ) )
  !call check( nf90_get_att(ncid, lon_varid, "maximum", maxlon ) )
  !call check( nf90_get_att(ncid, lon_varid, "minimum", minlon ) )
  !call check( nf90_get_att(ncid, lon_varid, "resolution", dlon ) )
  call check( nf90_get_att(ncid, time_varid, "units", timeunit ) )
  
  !print *, nint((maxlat-minlat)/dlat)+1,nint((maxlon-minlon)/dlon)+1
  !MNY=nint((maxlat-minlat)/dlat)+1
  !MNX=nint((maxlon-minlon)/dlon)+1
  ! Read the latitude and longitude data.

  call check( nf90_inq_dimid(ncid, LAT_NAME, lat_dimid))
  call check( nf90_inq_dimid(ncid, LON_NAME, lon_dimid))
  call check( nf90_inq_dimid(ncid, REC_NAME, time_dimid))
  if(status == nf90_noerr)call check( nf90_inq_dimid(ncid, LEV_NAME, lev_dimid))

  call check( nf90_inquire_dimension(ncid, lat_dimid, len=MNY ))
  call check( nf90_inquire_dimension(ncid, lon_dimid, len=MNX ))
  call check( nf90_inquire_dimension(ncid, time_dimid, len=MNT ))
  if(status == nf90_noerr)call check( nf90_inquire_dimension(ncid, lev_dimid, len=MNL ))

  allocate (lats(MNY))
  allocate (lons(MNX))
  allocate (forecast(MNT))
  if(status == nf90_noerr)allocate (levs(MNL))
  allocate (data_out(MNX,MNY))

  call check( nf90_get_var(ncid, lat_varid, lats) )
  call check( nf90_get_var(ncid, lon_varid, lons) )
  if(status == nf90_noerr)call check( nf90_get_var(ncid, lev_varid, levs) )
  call check( nf90_get_var(ncid, time_varid, forecast) )

  !dayhr=(TAU/24)*100+mod(TAU,24)
  !call udinvparse(timeunit,init_time+dayhr,timedata)
  NT=MNT
  !do i = 1 , MNT
  !   if(timedata==forecast(i))NT=i
  !enddo

  if(status == nf90_noerr) then
  NL=0
  if(NL==0)then
     print *,'Error level value !'
     print *,'valid level is ',(levs(i),i=1,MNL)
     stop
  endif
  endif

  ! Get the varids of the pressure and temperature netCDF variables.
  call check( nf90_inq_varid(ncid, trim(VARS_NAME), vars_varid) )

  call check( nf90_get_att(ncid, vars_varid, "missing_value", miss ) )
  call check( nf90_inquire_variable(ncid, vars_varid, ndims=numdim, &
       natts=numattr) )
  !print *,numdim,numattr
  ! Read 1 record of NX*NY*NL values, starting at the beginning 
  ! of the record (the (1, 1, 1, rec) element in the netCDF file).
  if(numdim==4) then
     allocate(count(4))
     allocate(start(4))
     !count = (/ NX, NY, NL, 1 /)
     !start = (/ 1, 1, 1, NT /)
     count = (/ MNX, MNY, 1, 1 /)
     start = (/ 1, 1, NL, NT /)
  elseif(numdim==3) then
     allocate(count(3))
     allocate(start(3))
     count = (/ MNX, MNY, 1 /)
     start = (/ 1, 1, NT /)
  elseif(numdim==2) then
     allocate(count(2))
     allocate(start(2))
     count = (/ MNX, MNY /)
     start = (/ 1, 1 /)
  endif
  ! Read the surface pressure and temperature data from the file, one
  ! record at a time.
  allocate (values(MNX, MNY))

  do rec = NT, NT
     if(numdim==4)then
         start(4) = rec
     elseif(numdim==3)then
         start(3) = rec
     endif
     
     call check( nf90_get_var(ncid, vars_varid, values, start = start, &
                              count = count) )
  end do
         
  ! Close the file. This frees up any internal netCDF resources
  ! associated with the file.
  call check( nf90_close(ncid) )

  data_out=values

  !print *,(((data_out(i,j,k),i=1,NX),j=1,NY),k=1,NL)

  ! If we got this far, everything worked as expected. Yipee! 
  !print *,"**** SUCCESS reading  file ", FILE_NAME, "!"

  end subroutine read_netcdf

  subroutine check(status)
    integer, intent ( in) :: status
    
    if(status /= 0) then 
      !print *, nf90_strerror(status)
      print *,status
      stop 2
    end if
  end subroutine check  

end module read_netcdf_module


  program sst
  use read_netcdf_module

  real, dimension(:,:),pointer :: values
  real, dimension(:),pointer:: lats,lons
  character(len=200) :: long_name, frmt, cmd
  character(len=100):: varname, cbar, workdir, output
  real :: miss
  integer :: rgb(4,256), gain, offset
  
  k = iargc()
  
  ! command line
   if ( k /= 4 ) then
        print *, " call of program "
        print *, " ./read_sst.exe <nc filename> <color bar> <working directory> <output file>"
        print *, " EXIT! "
        stop
   end if

   call getarg(1,long_name)
   call getarg(2,cbar)
   call getarg(3,workdir)
   call getarg(4,output)

   call chdir(workdir)

  !long_name="sst.day.mean.2016.v2.nc"
  varname="sst"
 
  call read_netcdf(long_name,varname,values,lats,lons,miss)

  !print *, shape(lats),shape(lons)
  ix=size(values(:,1))
  iy=size(values(1,:))

  where(values==miss)values=-99999.0
  miss=-99999.0
  !print *,shape(values),((values(i,j),i=1,ix),i=1,ix)
  gain=1;offset=0
  open(60,file=cbar,status="old")
  open(90,file=output,status="unknown")
      do i = 1 , 256
         read(60,*,end=99)rgb(1,i),rgb(2,i),rgb(3,i),rgb(4,i) 
      enddo
99    k=i-1
  write(90,'(3(G0.5,:,","),(f5.3,","),7(G0.6,:,","))')ix,iy,"b",lons(1),lats(1),lons(ix),lats(iy),"float32",miss,miss,"EPSG:4326"
  !write(90,'(3(G0.5,:,","),4(f0.3,","),4(G0.5,:,","))')ix,iy,"B",lons(1),lats(1),abs(lons(ix)-lons(1))/ix, &
  !      abs(lats(iy)-lats(1))/iy,"float32",miss,miss
  write(90,'(a,G0.5,a,G0.5,a)')"linearTransform(",gain,",",offset,")"

    if(rgb(4,k)>rgb(4,1))then
       write(90,'(9999(G0.5,:,","))')rgb(1:4,1:k)
    else
       write(90,'(9999(G0.5,:,","))')((rgb(i,j),i=1,4),j=k,1,-1)
    endif
      write(frmt,'(a1,i4,a13)')"(",ix+1,'(f0.2,:,","))'
      do jj=1,iy-1
         write(90,frmt) (values(ii,jj),ii=1,ix)
      end do
      write(90,frmt,advance="no") (values(ii,iy),ii=1,ix)
      DEALLOCATE(values)
      close(80)
      close(90)
      cmd="perl -pi -e 'chomp if eof' "//output
      call system(cmd)
      cmd="sed s/-99999.00//g "//output//" >"//"tmp.txt"
      call system(cmd)
      cmd="mv tmp.txt "//output
      call system(cmd)
  stop
  end program

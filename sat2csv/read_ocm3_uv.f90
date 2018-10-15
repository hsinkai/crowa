
module read_ocm3_module

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
  character (len = *), parameter :: LAT_NAME = "nv"
  character (len = *), parameter :: LON_NAME = "node"
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
  character(len=10),intent(out),optional :: miss

  if(len_trim(FILE_NAME)==0)then
     print *,'NO FILE FOUND'
     stop 2
  endif

  ! Open the file. 
  call check( nf90_open(trim(FILE_NAME), nf90_nowrite, ncid) )

  ! Get the varids of the latitude and longitude coordinate variables.
  call check( nf90_inq_varid(ncid, "y", lat_varid) )
  call check( nf90_inq_varid(ncid, "x", lon_varid) )
  call check( nf90_inq_varid(ncid, REC_NAME, time_varid) )
  status=nf90_inq_varid(ncid, LEV_NAME, lev_varid)

  call check( nf90_get_att(ncid, time_varid, "units", timeunit ) )
  
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

   subroutine wind(irain,irain2,ws,dir,miss)
   real,intent(in):: irain(:,:), irain2(:,:)
   real,intent(out):: ws(:,:), dir(:,:)
   real :: miss
   ws=miss;dir=miss
   where (irain/=miss)
      ws=sqrt(irain**2+irain2**2)
      dir=atan2(irain2,irain)*180/3.141592653
   endwhere
   where(dir<0.and.dir/=miss)dir=dir+360
   end subroutine wind

end module read_ocm3_module


  program test
  use read_ocm3_module
  implicit none

  real, dimension(:,:),pointer :: values, valuev, zcor
  real, dimension(:),pointer:: lats,lons
  real, dimension(:), allocatable :: lon, lat
  real, dimension(:,:), allocatable :: repo, repo2, dir, spd
  integer, dimension(:),allocatable :: zlev
  real, dimension(:),allocatable :: dest
  character(len=200):: long_name1, long_name2, output1, output2
  character(len=100):: varname, cbar, workdir
  character(len=10) :: cmiss
  real :: miss, dis, dx, dy, buf(100)
  integer :: ix, iy, lev, itmp
  integer :: i,j,k,ij,nx,ny
  integer :: minlon, maxlon, minlat, maxlat
  real :: dist, distmin, gain, offset, xlat, xlon
  
  k = iargc()
  
  ! command line
   if ( k /= 6 ) then
        print *, " call of program "
        print *, " ./read_ocm3_uv.exe <nc filename> <nc filename> <color bar> <working directory> & 
                    <output file 1> <output file 2>"
        print *, " EXIT! "
        stop
   end if

   call getarg(1,long_name1)
   call getarg(2,long_name2)
   call getarg(3,cbar)
   call getarg(4,workdir)
   call getarg(5,output1)
   call getarg(6,output2)

   call chdir(workdir)

  !long_name1="ocm3_zcor_2016092000_H49_72.nc"
  do i = 1 , len(long_name1)
     j=index(long_name1(i:),"/")
     if(j==0)exit
  enddo
  !varname="zcor"
  varname=trim(long_name1(i+5:i+8))
 
  call read_netcdf(long_name1,varname,zcor,lats,lons,cmiss)

  ix=size(zcor(:,1))
  iy=size(zcor(1,:))
  allocate(zlev(ix),dest(ix))
  !print *,shape(zcor),((zcor(i,j),i=20,20),j=1,iy)
  !print *,((zcor(i,j),i=1,ix),j=iy,iy)
  lev=0 !-5,-10
  do i = 1 , ix
     dis=9999999.0
     do j = iy , 1 , -1
        if(abs(zcor(i,j)-lev)<dis)then
          dis=abs(zcor(i,j)-lev)
          itmp=j
        endif
     enddo
     zlev(i)=itmp
  enddo

  !long_name2="ocm3_temp_2016092000_H49_72.nc"
  do i = 1 , len(long_name2)
     j=index(long_name2(i:),"/")
     if(j==0)exit
  enddo
  !varname="temp"
  varname=trim(long_name2(i+5:i+8))
  if(varname=="hvel")varname="u" 
  call read_netcdf(long_name2,varname,values,lats,lons,cmiss)

  varname="v"
  call read_netcdf(long_name2,varname,valuev,lats,lons,cmiss)

  read(cmiss,'(f8.1)')miss
  miss=-999.0
  !print *, shape(lats),shape(lons)
  ix=size(values(:,1))
  iy=size(values(1,:))
  !print *,shape(values),((values(i,j),i=1,ix),j=1,iy)
  !print *,shape(values),((values(i,j),i=1,1),j=1,iy)

  do i = 1 , ix
     dest(i)=values(i,zlev(i))   
  enddo
  !print *,dest

  gain=1.0;offset=0.0

  open(11,file="CWB.ndX")
  open(12,file="CWB.ndY")
  allocate(lat(ix),lon(ix))
  do i = 1 , ix
     read(11,*) lon(i)
     read(12,*) lat(i)
  enddo
!! reprojection
!!
  minlon=int(minval(lon))
  minlat=int(minval(lat))
  maxlon=int(maxval(lon))+1
  maxlat=int(maxval(lat))+1
  dx=0.05; dy=0.05
  nx=real(maxlon-minlon)/dx+1
  ny=real(maxlat-minlat)/dy+1
  !print *,minlon,minlat,maxlon,maxlat,nx,ny
  allocate(repo(nx,ny))
  allocate(repo2(nx,ny))
  allocate(dir(nx,ny))
  allocate(spd(nx,ny))
  call reproj(dest,ix,repo,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  !print *,repo
  !open(21,file="out.bin",form="unformatted",access="direct",recl=nx*ny*4,status="unknown")
  !write(21,rec=1)repo

  do i = 1 , ix
     dest(i)=valuev(i,zlev(i))   
  enddo
  call reproj(dest,ix,repo2,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)

  call wind(repo,repo2,spd,dir,miss)
  call outpnt(dir,nx,ny,minlon,minlat,dx,dy,cbar,output1,miss)
  call outpnt(spd,nx,ny,minlon,minlat,dx,dy,cbar,output2,miss)

  deallocate(repo,repo2,dest,zlev,lat,lon)

  stop
  end program

  subroutine reproj(dest,ix,repo,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  integer :: nx,ny,i,j,k,ij
  real :: xlon,xlat,distmin,dist,miss
  real :: dest(ix), repo(nx,ny), lon(ix), lat(ix)
  do i = 1 , nx
     do j = 1 , ny
        xlon=real(minlon)+(i-1)*dx
        xlat=real(minlat)+(j-1)*dy
        distmin=999999.0
        ij=0
        do k = 1 , ix
          dist=(lon(k)-xlon)*(lon(k)-xlon)+(lat(k)-xlat)*(lat(k)-xlat)
          if(dist<distmin.and.dist<0.016)then
             distmin=dist
             repo(i,j)=dest(k)
             ij=k
             !print *,dist
          endif
        enddo
        if(ij==0.or.repo(i,j)<=-99.0)repo(i,j)=miss
        !print *,repo(i,j)
     enddo
  enddo

  return
  end subroutine reproj

  subroutine outpnt(values,nx,ny,minlon,minlat,dx,dy,cbar,output,miss)

  integer :: nx,ny
  real,dimension(nx,ny):: values
  real :: miss, gain, offset, dx, dy
  character(len=100):: cbar, workdir, output, frmt, cmd
  integer :: minlon, minlat, rgb(4,256)
  
  !print *,shape(values),((values(i,j),i=1,ix),i=1,ix)
  gain=1.0;offset=0.0
  open(60,file=cbar,status="old")
  open(90,file=output,status="unknown")
      do i = 1 , 256
         read(60,*,end=99)rgb(1,i),rgb(2,i),rgb(3,i),rgb(4,i) 
      enddo
99    k=i-1
  !write(6,'(3(G0.5,:,","),4(f0.2,","),4(G0.5,:,","))')ix,iy,"T",lons(1),lats(1),lons(ix),lats(iy),"float32",miss,miss,"EPSG:4326"
    write(90,'(5(G0.5,:,","),2(f5.3,","),4(G0.5,:,","))')nx,ny,"B",minlon,minlat,dx,dy,"float32",miss,miss
    write(90,'(a,f6.4,a,f6.4,a)')"LinearTransform(",gain,",",offset,")"

    if(rgb(4,k)>rgb(4,1))then
       write(90,'(9999(G0.5,:,","))')rgb(1:4,1:k)
    else
       write(90,'(9999(G0.5,:,","))')((rgb(i,j),i=1,4),j=k,1,-1)
    endif
      write(frmt,'(a1,i4,a13)')"(",ny+1,'(f0.3,:,","))'
      do ii=1,nx-1
         write(90,frmt) (values(ii,jj),jj=1,ny)
      end do
      write(90,frmt,advance="no") (values(nx,jj),jj=1,ny)
      close(80)
      close(90)
      cmd="perl -pi -e 'chomp if eof' "//output
      call system(cmd)

   close(60)
   close(90)
   return
   end subroutine outpnt


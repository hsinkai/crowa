
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
  integer,dimension(:,:),allocatable :: domain
  
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
  allocate(domain(nx,ny))
  call reproj(dest,ix,repo,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  !call reproj2(dest,ix,repo,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  !print *,repo

  do i = 1 , ix
     dest(i)=valuev(i,zlev(i))   
  enddo
  call reproj(dest,ix,repo2,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  !call reproj2(dest,ix,repo2,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)

  open(21,file="domain.dem",form="unformatted",access="direct",recl=nx*ny*4,status="unknown")
  read(21,rec=1)domain
  close(21)
  do j = 1 , ny
     do i = 1 , nx
        if(domain(i,j)>0)then
           repo(i,j)=miss
           repo2(i,j)=miss
        endif
     enddo
  enddo
  call wind(repo,repo2,spd,dir,miss)
  call outpnt(dir,nx,ny,minlon,minlat,maxlon,maxlat,cbar,output1,miss)
  call outpnt(spd,nx,ny,minlon,minlat,maxlon,maxlat,cbar,output2,miss)

  deallocate(repo,repo2,dest,zlev,lat,lon)

  !open(51,file="uv.dat",form="unformatted",access="direct",recl=nx*ny*4,status="unknown")
  !write(51,rec=1)spd*cos(dir/57.295779524)
  !write(51,rec=2)spd*sin(dir/57.295779524)
  !close(51)
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
          !if(dist<distmin.and.dist<0.010)then
          if(dist<distmin.and.dist<=0.3*dx*dy)then
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

  subroutine reproj2(dest,ix,repo,lon,lat,nx,ny,minlon,minlat,dx,dy,miss)
  integer :: nx,ny,i,j
  real :: xlon(nx*ny),xlat(nx*ny),distmin,dist,miss
  real :: dest(ix), repo(nx,ny), lon(ix), lat(ix)

      INTEGER :: MI,MO,KM
!      INTEGER :: IBI(KM)
!      REAL :: GI(MI,KM)
      INTEGER :: NO
      REAL,ALLOCATABLE :: RLAT(:),RLON(:)
      REAL :: GO(nx*ny)
      INTEGER :: IRET
!      REAL XPTS(MO),YPTS(MO)
      INTEGER IJKGDSA(20)
      REAL,PARAMETER:: FILL=-9999.
      INTEGER MSPIRAL,N,K,NK,NV,IJKGDS1
      INTEGER I1,J1,IXS,JXS,MX,KXS,KXT,IX,JX,NNX
      INTEGER,SAVE:: KGDSIX(200)=-1,KGDSOX(200)=-1,NOX=-1,IRETX=-1
      INTEGER,ALLOCATABLE,SAVE:: NXY(:)
      REAL,ALLOCATABLE,SAVE:: RLATX(:),RLONX(:),XPTSX(:),YPTSX(:)
      REAL,ALLOCATABLE::DUM1(:),DUM2(:)

  do i = 1 , nx
     do j = 1 , ny
        xlon((i-1)*ny+j)=real(minlon)+(i-1)*dx
        xlat((i-1)*ny+j)=real(minlat)+(j-1)*dy
     enddo
  enddo
      IRET=0
      MSPIRAL=1
      IF(IRET.EQ.0.) THEN
      mo=nx*ny
      no=ix
      ALLOCATE(RLON(mo))
      ALLOCATE(RLAT(mo))
      RLON=xlon
      RLAT=xlat
!        IF(KGDSO(1).GE.0) THEN
          ALLOCATE(DUM1(MO))
          ALLOCATE(DUM2(MO))
!          CALL GDSWIZ(KGDSO, 0,MO,FILL,XPTS,YPTS,RLON,RLAT,NO,0,
!     &                DUM1,DUM2)
          DEALLOCATE(DUM1,DUM2)
          IF(NO.EQ.0) IRET=3
!        ENDIF
        ALLOCATE(DUM1(NO))
        ALLOCATE(DUM2(NO))
!        CALL GDSWIZ(KGDSI,-1,NO,FILL,XPTS,YPTS,RLON,RLAT,NV,0,
!     &              DUM1,DUM2)
        DEALLOCATE(DUM1,DUM2)
        IF(IRET.EQ.0.AND.NV.EQ.0) IRET=2
!        KGDSIX=KGDSI
!        KGDSOX=KGDSO
        IF(NOX.NE.NO) THEN
          IF(NOX.GE.0) DEALLOCATE(RLATX,RLONX,XPTSX,YPTSX,NXY)
          ALLOCATE(RLATX(NO),RLONX(NO),XPTSX(NO),YPTSX(NO),NXY(NO))
          NOX=NO
        ENDIF
        IRETX=IRET
        IF(IRET.EQ.0) THEN
          CALL IJKGDS0(KGDSI,IJKGDSA)
          DO N=1,NO
            RLONX(N)=RLON(N)
            RLATX(N)=RLAT(N)
!            XPTSX(N)=XPTS(N)
!            YPTSX(N)=YPTS(N)
!            IF(XPTS(N).NE.FILL.AND.YPTS(N).NE.FILL) THEN
!              NXY(N)=IJKGDS1(NINT(XPTS(N)),NINT(YPTS(N)),IJKGDSA)
!            ELSE
!              NXY(N)=0
!            ENDIF
          ENDDO
        ENDIF
      ENDIF
      IF(IRET.EQ.0.AND.IRETX.EQ.0) THEN
!        IF(KGDSO(1).GE.0) THEN
          NO=NOX
          DO N=1,NO
            RLON(N)=RLONX(N)
            RLAT(N)=RLATX(N)
          ENDDO
!        ENDIF
        DO N=1,NO
!          XPTS(N)=XPTSX(N)
!          YPTS(N)=YPTSX(N)
        ENDDO
        DO NK=1,NO*KM
          K=(NK-1)/NO+1
          N=NK-NO*(K-1)
!          GO(N,K)=0
!          LO(N,K)=.FALSE.
          IF(NXY(N).GT.0) THEN
!            IF(LI(NXY(N),K)) THEN
!              GO(N,K)=GI(NXY(N),K)
!              LO(N,K)=.TRUE.
!            ELSEIF(MSPIRAL.GT.1) THEN
!              I1=NINT(XPTS(N))
!              J1=NINT(YPTS(N))
!              IXS=SIGN(1.,XPTS(N)-I1)
!              JXS=SIGN(1.,YPTS(N)-J1)
              DO MX=2,MSPIRAL**2
                KXS=SQRT(4*MX-2.5)
                KXT=MX-(KXS**2/4+1)
                SELECT CASE(MOD(KXS,4))
                CASE(1)
                  IX=I1-IXS*(KXS/4-KXT)
                  JX=J1-JXS*KXS/4
                CASE(2)
                  IX=I1+IXS*(1+KXS/4)
                  JX=J1-JXS*(KXS/4-KXT)
                CASE(3)
                  IX=I1+IXS*(1+KXS/4-KXT)
                  JX=J1+JXS*(1+KXS/4)
                CASE DEFAULT
                  IX=I1-IXS*KXS/4
                  JX=J1+JXS*(KXS/4-KXT)
                END SELECT
!                NNX=IJKGDS1(IX,JX,IJKGDSA)
                IF(NNX.GT.0) THEN
!                  IF(LI(NX,K)) THEN
!                    GO(N,K)=GI(NX,K)
!                    LO(N,K)=.TRUE.
!                    EXIT
!                  ENDIF
                ENDIF
              ENDDO
!            ENDIF
          ENDIF
        ENDDO
!        DO K=1,KM
!          IBO(K)=IBI(K)
!          IF(.NOT.ALL(LO(1:NO,K))) IBO(K)=1
!        ENDDO
!        IF(KGDSO(1).EQ.0) CALL POLFIXS(NO,MO,KM,RLAT,RLON,IBO,LO,GO)
      ELSE
        IF(IRET.EQ.0) IRET=IRETX
!        IF(KGDSO(1).GE.0) NO=0
      ENDIF

  end subroutine reproj2

  subroutine outpnt(values,nx,ny,minlon,minlat,maxlon,maxlat,cbar,output,miss)

  integer :: nx,ny
  real,dimension(nx,ny):: values
  real :: miss, dx, dy, x
  character(len=100):: cbar, workdir, output, frmt, cmd
  integer :: minlon, maxlon, minlat, maxlat, rgb(1:4,256), gain, offset
  real :: rgb2(256)
  character(len=5):: vname
  
  gain=1;offset=0
  open(60,file=cbar,status="old")
  open(90,file=output,status="unknown")
      do i = 1 , 256
         read(60,*,end=99)rgb(1,i),rgb(2,i),rgb(3,i),rgb2(i) 
      enddo
99    k=i-1
  !write(6,'(3(G0.5,:,","),4(f0.2,","),4(G0.5,:,","))')ix,iy,"T",lons(1),lats(1),lons(ix),lats(iy),"float32",miss,miss,"EPSG:4326"
    write(90,'(4(G0.4,:,","),G0.3,:,",",G0.4,",",G0.3,",",6(G0.4,:,","))')nx,ny,"b",real(minlon),real(minlat), & 
          real(maxlon),real(maxlat),"float32",miss,miss,"EPSG:4326"
    write(90,'(a,G0,a,G0,a)')"linearTransform(",gain,",",offset,")"

    if(rgb2(k)>rgb2(1))then
       !write(90,'(999(3(G0.2,:,","),f0.1,","))')(rgb(1:3,j),rgb2(j),j=1,k)
       write(90,'(9999(G0.2,:,","))')(rgb(1:3,j),rgb2(j),j=1,k)
    else
       write(90,'(9999(G0.2,:,","))')(rgb(1:3,j),rgb2(j),j=k,1,-1)
    endif
      write(frmt,'(a1,i4,a13)')"(",nx+1,'(f0.2,:,","))'
      do ii=1,ny-1
         write(90,frmt) (values(jj,ii),jj=1,nx)
      end do
      write(90,frmt,advance="no") (values(ii,ny),ii=1,nx)
      close(60)
      close(90)
      cmd="/usr/bin/perl -pi -e 'chomp if eof' "//output
      call system(cmd)
      call random_seed()
      call init_random_seed() !<- this line is for GFortran
      call random_number(x)
      write(vname,'(i5.5)') int(x*100000)
      cmd="/bin/sed 's/-999.00//g' "//trim(output)//" > "//vname
      call system(cmd)
      cmd="/bin/mv "//vname//" "//trim(output)
      call system(cmd)


   return
   end subroutine outpnt

      SUBROUTINE IJKGDS0(IM,JM,RLON1,RLAT1,RLON2,RLAT2,IJKGDSA)
      INTEGER KGDS(200)
      INTEGER IJKGDSA(20)
      IWRAP=0
      JWRAP1=0
      JWRAP2=0
      NSCAN=0
      KSCAN=0
      IF(KGDS(1).EQ.0) THEN
        !RLON1=KGDS(5)*1.E-3
        !RLON2=KGDS(8)*1.E-3
        ISCAN=MOD(64/128,2)
        IF(ISCAN.EQ.0) THEN
          DLON=(MOD(RLON2-RLON1-1+3600,360.)+1)/(IM-1)
        ELSE
          DLON=-(MOD(RLON1-RLON2-1+3600,360.)+1)/(IM-1)
        ENDIF
        IWRAP=NINT(360/ABS(DLON))
        IF(IM.LT.IWRAP) IWRAP=0
        IF(IWRAP.GT.0.AND.MOD(IWRAP,2).EQ.0) THEN
          !RLAT1=KGDS(4)*1.E-3
          !RLAT2=KGDS(7)*1.E-3
          DLAT=ABS(RLAT2-RLAT1)/(JM-1)
          IF(ABS(RLAT1).GT.90-0.25*DLAT) THEN
            JWRAP1=2
          ELSEIF(ABS(RLAT1).GT.90-0.75*DLAT) THEN
            JWRAP1=1
          ENDIF
          IF(ABS(RLAT2).GT.90-0.25*DLAT) THEN
            JWRAP2=2*JM
          ELSEIF(ABS(RLAT2).GT.90-0.75*DLAT) THEN
            JWRAP2=2*JM+1
          ENDIF
        ENDIF
      ENDIF
      IJKGDSA(1)=IM
      IJKGDSA(2)=JM
      IJKGDSA(3)=IWRAP
      IJKGDSA(4)=JWRAP1
      IJKGDSA(5)=JWRAP2
      IJKGDSA(6)=NSCAN
      IJKGDSA(7)=KSCAN
      END

      SUBROUTINE init_random_seed()
      INTEGER :: i, n, clock
      INTEGER, ALLOCATABLE :: seed(:)

      call RANDOM_SEED(SIZE = n)
      ALLOCATE(seed(n))
      call SYSTEM_CLOCK(COUNT=clock)
      seed = clock - 2047 * (/ (i - 1, i = 1, n) /)
      seed = seed * 1103515245 + 2531011
      call RANDOM_SEED(PUT = seed)
      DEALLOCATE(seed)
      END SUBROUTINE


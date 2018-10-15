      program read_file
      include 'hisd.inc'
      !integer, parameter  :: i_short = selected_int_kind(4)
      !integer, parameter  :: i_byte = selected_int_kind(1)
      !integer, parameter  :: r_double = selected_real_kind(15) ! double precision
      integer(i_short),allocatable,dimension(:,:,:) :: buff
      real,allocatable,dimension(:) :: buff2
      real,allocatable,dimension(:,:) :: buf2
      real,allocatable,dimension(:,:) :: buf
      CHARACTER(len=100) :: input1, input2, frmt, cmd
      CHARACTER(LEN=100) :: output, list(10), workdir, cbar
      CHARACTER(len=8) :: dd
      CHARACTER(len=4) :: tt
      CHARACTER(len=2) :: bb
      CHARACTER(len=2) :: seg, rr
      !integer(i_byte),dimension(1523) :: header
      integer :: i,j,k,j1,j2, nx, ny, nz, nbit
      logical :: exist
      integer :: rgb(4,256)
      real(r_double) :: radiance, tbb,rlat1,rlon1

      type(HisdHeader) :: HisdHeader1

      k = iargc()
  
     ! command line
      if ( k /= 5 ) then
        print *, " call of program "
        print *, " ./read_filev1.exe <time> <band> <color bar> <working directory> <output file>"
        print *, " EXIT! "
        stop
      end if

      call getarg(1,input1)
      call getarg(2,input2)
      call getarg(3,cbar)
      call getarg(4,workdir)
      call getarg(5,output)

      call chdir(workdir)

      dd=input1(1:8)
      tt=input1(9:12)
      bb=input2(1:2)
      
      if(bb.eq."03") then
         nx=22000
         rr="05"
      elseif(bb.eq."01".or.bb.eq."02".or.bb.eq."04") then
         nx=11000
         rr="10"
      else
         nx=5500
         rr="20"
      endif
      ny=nx/10
      nz=10
      if(bb.eq."07")then
         nbit=64
      elseif(bb.eq."10".or.bb.eq."11".or.bb.eq."12".or.bb.eq."13".or.bb.eq."14".or.bb.eq."15")then
         nbit=16
      else
         nbit=8
      endif
      allocate(buff(nx,ny,nz))
      allocate(buff2(nx))
      allocate(buf2(nx,ny*nz))

      do j = 1 , 10
        write(seg,'(I2.2)')j
        list(j)="HS_H08_"//dd//"_"//tt//"_B"//bb//"_FLDK_R"//rr//"_S"//seg//"10.DAT"
        inquire(file=trim(list(j)),exist=exist)
        if(.not.exist) print *,"file: ",trim(list(j))," not found"
         open(10+j,file=trim(list(j)), &
             form='unformatted',access='stream',status='old',iostat=ier)
         if(ier.ne.0)then
            print *,trim(list(j))," file error number:",ier
            stop
         endif
         read(10+j,pos=1)HisdHeader1%basic
         k=HisdHeader1%basic%BlockLen+1
         read(10+j,pos=k)HisdHeader1%data
         k=k+HisdHeader1%data%BlockLen
         read(10+j,pos=k)HisdHeader1%proj
         k=k+HisdHeader1%proj%BlockLen
         read(10+j,pos=k)HisdHeader1%Navi_Info
         k=k+HisdHeader1%Navi_Info%BlockLen
         read(10+j,pos=k)HisdHeader1%calib
         k=k+HisdHeader1%calib%BlockLen
         read(10+j,pos=k)HisdHeader1%interCalib
         k=k+HisdHeader1%interCalib%BlockLen
         read(10+j,pos=k)HisdHeader1%seg
         k=k+HisdHeader1%seg%BlockLen
         read(10+j,pos=k)HisdHeader1%navcorr
         k=k+HisdHeader1%navcorr%BlockLen
         read(10+j,pos=k)HisdHeader1%obstime
         k=k+HisdHeader1%obstime%BlockLen
         read(10+j,pos=k)HisdHeader1%error
         k=k+HisdHeader1%error%BlockLen
         read(10+j,pos=k)HisdHeader1%spare
         inquire(10+j,pos=i)
         read(10+j,pos=HisdHeader1%basic%totalHeaderLen+1)buff(:,:,j)
      enddo
      !open(50,file="ir1.dat",form='unformatted',access='direct',recl=nx*ny*nz,status='unknown')
      do i = 1 , 10
         do j = 1 , ny
            !buff2=int(buff(:,j,i)/nbit)
            do k = 1 , nx
             radiance=buff(k,j,i)*HisdHeader1%calib%gain_cnt2rad+HisdHeader1%calib%cnst_cnt2rad
             if(HisdHeader1%calib%bandNo>=7)then
             call hisd_radiance_to_tbb(HisdHeader1,radiance,tbb)
             buff2(k)=tbb
             else
             tbb=radiance* HisdHeader1%calib%rad2btp_c0
             buff2(k)=tbb*255
             endif
            enddo
            !write(50,rec=(i-1)*ny+j)buff2
            buf2((i-1)*ny+j,:)=buff2
         enddo
      enddo
      !write(50,rec=1)buf2
      !print *,buff
      DEALLOCATE(buff2,buff)

      np=2501
      xstart=100.
      ystart=-5.
      resol=0.02
      gain=1.0;offset=0.0
      allocate(buf(np,np))
      do i = 1 , np
        do j = 1 , np
        rlat=-ystart+real(i-1)/50.
        rlon=xstart+real(j-1)/50.
        call geocoord2pixcoord(rlat,rlon,HisdHeader1%proj%coff,HisdHeader1%proj%loff,ll,lll,HisdHeader1)
        buf(np+1-i,j)=buf2(ll,lll)
        !call pixcoord2geocoord(ll,lll,rlat1,rlon1,HisdHeader1)
        !print *,ll,lll,rlat1,rlon1
        enddo
      enddo
      !open(50,file="ir1.dat",form='unformatted',access='direct',recl=2501*2501,status='unknown')
      !write(50,rec=1)buf
      open(60,file=cbar,status="old")
      open(90,file=output,status="unknown")
      do i = 1 , 256
         read(60,*,end=99)rgb(4,i),rgb(1,i),rgb(2,i),rgb(3,i) 
      enddo
99    k=i-1
      write(90,'(3(G0.5,:,","),2(f0.2,","),2(f4.2,","),4(G0.5,:,","))')np,np,"T",xstart,ystart,resol,resol,"int16",-9999,-9999
      write(90,'(a,f6.4,a,f6.4,a)')"LinearTransform(",gain,",",offset,")"
      if(rgb(4,k)>rgb(4,1))then
         write(90,'(9999(G0.5,:,","))')rgb(1:4,1:k)
      else
         write(90,'(9999(G0.5,:,","))')((rgb(i,j),i=1,4),j=k,1,-1)
      endif
      !where (buf < 0) buf=buf+256 
      write(frmt,'(a1,i4,a13)')"(",np+1,'(f0.2,:,","))'
      do jj=1,np-1
         write(90,frmt) (buf(ii,jj),ii=1,np)
      end do
      write(90,frmt,advance="no") (buf(ii,np),ii=1,np)
      DEALLOCATE(buf2,buf)
      close(80)
      close(90)
      cmd="perl -pi -e 'chomp if eof' "//output
      call system(cmd)
      stop
      end

      subroutine hisd_radiance_to_tbb(HisdHeader1, radiance, tbb)
      include 'hisd.inc'
      type(HisdHeader) :: HisdHeader1
      real(r_double) :: radiance, tbb
      real(r_double) :: effective_temperature, lambda
      real(r_double) :: planck_c1, planck_c2

      lambda= HisdHeader1%calib%waveLen / 1000000.0 ![micro m] => [m]
      radiance=radiance * 1000000.0 ![ W/(m^2 sr micro m)] => [ W/(m^2 sr m)]
      ! planck_c1 = (2 * h * c^2 / lambda^5)
      planck_c1= 2.0 * HisdHeader1%calib%planckConst * &
                       HisdHeader1%calib%lightSpeed **2 &
                       / ( lambda ** 5 ) 
      ! planck_c2 = (h * c / k / lambda ) 
      planck_c2= HisdHeader1%calib%planckConst * HisdHeader1%calib%lightSpeed / &
                 HisdHeader1%calib%bolzConst / lambda
      if(radiance > 0 ) then
         effective_temperature = planck_c2/ log( (planck_c1 / radiance ) + 1.0 )
         tbb= HisdHeader1%calib%rad2btp_c0 + &
              HisdHeader1%calib%rad2btp_c1 * effective_temperature + &
              HisdHeader1%calib%rad2btp_c2 * effective_temperature **2
      else
         tbb= -10000000000.0
      endif
      return
      end subroutine
      
SUBROUTINE pixcoord2geocoord( column,  row,  latitude, longitude, HisdHeader1)

  !USE GLOBAL

  IMPLICIT NONE
  include 'hisd.inc'

  INTEGER, INTENT (IN) :: column, row
  REAL(KIND(0.0d0)) , INTENT (OUT) :: latitude, longitude

  REAL(KIND(0.0d0)),parameter :: PI=3.14159265359d0
  
  REAL(KIND(0.0d0)) :: s1, s2, s3, sn, sd, sxy
  REAL(KIND(0.0d0)) :: x, y, xx, yy
  REAL(KIND(0.0d0)) :: longi, lati
  REAL(KIND(0.0d0)) :: lat
  REAL(KIND(0.0d0)) :: lon


  REAL(KIND(0.0d0)) :: a, b, sa

  INTEGER ::  c, l

  type(HisdHeader), INTENT (IN) :: HisdHeader1

  c=column
  l=row

  x = (2.0d0**16.0d0 * ( DBLE(c) - DBLE(HisdHeader1%proj%coff) )) / (DBLE(HisdHeader1%proj%cfac)*180d0/PI)
  y = (2.0d0**16.0d0 * ( DBLE(l) - DBLE(HisdHeader1%proj%loff) )) / (DBLE(HisdHeader1%proj%lfac)*180d0/PI)

  sa =  (HisdHeader1%proj%satDis * cos(x) * cos(y) )**2 - (cos(y)*cos(y) + HisdHeader1%proj%projParam3 * sin(y)*sin(y)) * HisdHeader1%proj%projParamSd

  if ( sa .LE. 0.0 ) then
     latitude = -999.999
     longitude = -999.999
     return 
  end if

  sd = sqrt( (HisdHeader1%proj%satDis * cos(x) * cos(y) )**2 - (cos(y)*cos(y) + HisdHeader1%proj%projParam3 * sin(y)*sin(y)) * HisdHeader1%proj%projParamSd )
  sn = (HisdHeader1%proj%satDis * cos(x) * cos(y) - sd) / ( cos(y)*cos(y) + HisdHeader1%proj%projParam3 * sin(y)*sin(y) ) 
  
  s1 = HisdHeader1%proj%satDis - sn * cos(x) * cos(y)
  s2 = sn * sin(x) * cos(y)
  s3 = -sn * sin(y)

  sxy = sqrt( s1*s1 + s2*s2 )

  longi = atan(s2/s1) + HisdHeader1%proj%subLon *PI/180.d0
  lati  = atan((HisdHeader1%proj%projParam3*s3)/sxy)
  ! convert from radians into degrees
  latitude = lati*180.0d0/PI
  longitude = longi*180.0d0/PI


END SUBROUTINE pixcoord2geocoord

SUBROUTINE geocoord2pixcoord( latitude,  longitude,  ccoff,  lloff,  column, row, HisdHeader1)

  !USE GLOBAL

  IMPLICIT NONE
  include 'hisd.inc'


  REAL, INTENT (IN) :: latitude, longitude
  REAL, INTENT (IN)  :: ccoff, lloff
  INTEGER, INTENT (OUT) :: column, row
  REAL(KIND(0.0d0)),parameter :: PI=3.14159265359d0
  

  INTEGER :: c=0, l=0
  INTEGER :: ccc=0, lll=0
  INTEGER :: x=0, y=0

  REAL(KIND(0.0d0)) :: lati, longi
  REAL(KIND(0.0d0)) :: c_lat
  REAL(KIND(0.0d0)) :: lat
  REAL(KIND(0.0d0)) :: lon
  REAL(KIND(0.0d0)) :: r1, r2, r3, rn, re, rl
  REAL(KIND(0.0d0)) :: xx, yy, sa
  REAL(KIND(0.0d0)) :: cc, ll
  REAL(KIND(0.0d0)) :: dotprod
  type(HisdHeader), INTENT (IN) :: HisdHeader1


  lati= latitude
  longi= longitude

  lat = lati*PI / 180.0d0
  lon = longi *PI / 180.0d0

  c_lat = atan ( (0.993243d0*(sin(lat)/cos(lat)) ))
  re = HisdHeader1%proj%polrRadius / sqrt( (1.0d0 - 0.00675701d0 * cos(c_lat) * cos(c_lat) ) )


  rl = re
  r1 = HisdHeader1%proj%satDis - rl * cos(c_lat) * cos(lon -HisdHeader1%proj%subLon*PI/180.0d0)
  r2 = - rl *  cos(c_lat) * sin(lon -HisdHeader1%proj%subLon*PI/180.0d0)
  r3 = rl * sin(c_lat)
  rn = sqrt( r1*r1 + r2*r2 +r3*r3 )


  dotprod = r1*(rl * cos(c_lat) * cos(lon -HisdHeader1%proj%subLon*PI/180.0d0)) - r2*r2 - r3*r3*((HisdHeader1%proj%eqtrRadius/HisdHeader1%proj%polrRadius)**2)

  if (dotprod .LE. 0.0d0 ) then
!     column = -999
!     row = -999
     column = 1
     row = 1
     return
  end if


  xx = atan( (-r2/r1) )
  yy = asin( (-r3/rn) )


  cc = DBLE(ccoff) + xx *  2.0d0**(-16.0d0) * DBLE(HisdHeader1%proj%cfac/PI*180)
  ll = DBLE(lloff) + yy *  2.0d0**(-16.0d0) * DBLE(HisdHeader1%proj%lfac/PI*180)

  ccc=nint(cc)
  lll=nint(ll)		

  column = ccc
  row = lll

      
END SUBROUTINE geocoord2pixcoord

      program read_file
      include 'hisd.inc'
      !integer, parameter  :: i_short = selected_int_kind(4)
      !integer, parameter  :: i_byte = selected_int_kind(1)
      !integer, parameter  :: r_double = selected_real_kind(15) ! double precision
      integer(i_short),allocatable,dimension(:,:,:) :: buff
      integer(i_byte),allocatable,dimension(:) :: buff2
      CHARACTER(len=100) :: input1, input2
      CHARACTER(LEN=100) :: output, list(10)
      CHARACTER(len=8) :: dd
      CHARACTER(len=4) :: tt
      CHARACTER(len=2) :: bb
      CHARACTER(len=2) :: seg, rr
      !integer(i_byte),dimension(1523) :: header
      integer :: i,j,k,j1,j2, nx, ny, nz, nbit
      logical :: exist
      real(r_double) :: radiance, tbb

      type(HisdHeader) :: HisdHeader1

      k = iargc()
  
     ! command line
      if ( k .NE. 2 ) then
        print *, " call of program "
        print *, " ./a.out <time> <band> "
        print *, " EXIT! "
        stop
      end if

      call getarg(1,input1)
      call getarg(2,input2)


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
         !read(10+j,pos=1)HisdHeader1
         !print *,HisdHeader1%basic%HeaderNum
         !print *,HisdHeader1%basic%BlockLen
         !print *,HisdHeader1%basic%headernumb
         !print *,HisdHeader1%basic%byteOrder
         !print *,(HisdHeader1%basic%satName)
         !print *,HisdHeader1%basic%proName
         !print *,HisdHeader1%basic%ObsType1
         !print *,HisdHeader1%basic%ObsType2
         !print *,HisdHeader1%basic%TimeLine
         !print *,HisdHeader1%basic%ObsStartTime
         !print *,HisdHeader1%basic%totalHeaderLen
         !print *,HisdHeader1%basic%verName
         !print *,HisdHeader1%basic%fileName
         print *,HisdHeader1%basic
         print *,HisdHeader1%data
         print *,HisdHeader1%proj
         print *,HisdHeader1%Navi_Info%HeaderNum
         !print *,HisdHeader1%calib%HeaderNum
         !print *,HisdHeader1%calib%gain_cnt2rad
         !print *,HisdHeader1%calib%cnst_cnt2rad
         print *,HisdHeader1%calib
         print *,HisdHeader1%interCalib%HeaderNum
         print *,HisdHeader1%seg%HeaderNum
         print *,HisdHeader1%navcorr%HeaderNum
         print *,HisdHeader1%navcorr%BlockLen
         print *,HisdHeader1%navcorr%correctNum
         print *,HisdHeader1%navcorr%columnShift,HisdHeader1%navcorr%lineShift
         print *,HisdHeader1%obstime%HeaderNum
         print *,HisdHeader1%obstime%BlockLen
         print *,HisdHeader1%obstime%obsNum
         print *,HisdHeader1%error%HeaderNum
         print *,HisdHeader1%error%BlockLen
         print *,HisdHeader1%error%errorNum
         print *,HisdHeader1%spare%HeaderNum
         inquire(10+j,pos=i)
         print *,'position=',i
         read(10+j,pos=HisdHeader1%basic%totalHeaderLen+1)buff(:,:,j)
      enddo
      !open(50,file="ir1.dat",form='unformatted',access='direct',recl=nx,status='unknown')
      do i = 1 , 10
         do j = 1 , ny
            buff2=int(buff(:,j,i)/nbit)
            do k = 1 , nx
             radiance=buff(k,j,i)*HisdHeader1%calib%gain_cnt2rad+HisdHeader1%calib%cnst_cnt2rad
             if(HisdHeader1%calib%bandNo>=7)then
             call hisd_radiance_to_tbb(HisdHeader1,radiance,tbb)
             !buff2(k)=tbb-50.
             else
             tbb=radiance* HisdHeader1%calib%rad2btp_c0
             !buff2(k)=tbb*250
             endif
            enddo
            !write(50,rec=(i-1)*ny+j)buff2
         enddo
      enddo
         do j = 1 , 4096
             radiance=j*HisdHeader1%calib%gain_cnt2rad+HisdHeader1%calib%cnst_cnt2rad
             call hisd_radiance_to_tbb(HisdHeader1,radiance,tbb)
             !print *,j,tbb,j/16
             if(mod(j+1,16)==0)print *,j,tbb,j/16
         enddo
      !print *,buff
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
      

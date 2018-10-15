      program read_QPE_header
      character :: filename*256

      integer yyyy,mm,dd,hh,mn,ss,nx,ny,nz  ! 1-9th vars
      character proj*4                      ! 10th vars
      integer map_scale,projlat1,projlat2,projlon,alon,alat
      integer xy_scale,dx,dy,dxy_scale      ! 11-20th vars
      integer z_scale,i_bb_mode,unkn01(9)
      character varname*20,varunit*6
      integer var_scale,missing,nradar
      integer,allocatable :: zht(:)
      character,allocatable ::  mosradar(:)*4
      integer*2,allocatable :: var(:,:)
      integer*4,allocatable :: var4(:,:)
      real,allocatable :: var_true(:,:)
      character(len=100) :: output, workdir, cbar
      integer*4,allocatable :: I_var_true(:,:)
      character var_type
      character*100 :: frmt, cmd
      integer :: rgb(4,256)
      real :: elon,elat

!!!!!!!!!!!!!================================!!!!!!!!!!!!!!!!!!!
      k = iargc()
  
     ! command line
      if ( k /= 4 ) then
        print *, " call of program "
        print *, " ./header.exe <data filename> <color bar> <working directory> <output file>"
        print *, " EXIT! "
        stop
      end if

      call getarg(1,filename)
      call getarg(2,cbar)
      call getarg(3,workdir)
      call getarg(4,output)
      !    write(*,*)trim(filename)
      call chdir(workdir)
      open(60,file=cbar,status="old")
      do i = 1 , 256
         read(60,*,end=99)rgb(1,i),rgb(2,i),rgb(3,i),rgb(4,i) 
      enddo
      close(60)
99    k=i-1

      open(11,file=trim(filename),form='unformatted',status='old', &
           access='stream')
!        open(11,file=trim(filename),form="binary")
        read(11)yyyy,mm,dd,hh,mn,ss,nx,ny,nz,proj,map_scale, &
          projlat1,projlat2,projlon,alon,alat,xy_scale,dx,dy,dxy_scale
          allocate(var(nx,ny),var4(nx,ny),var_true(nx,ny))
          allocate(I_var_true(nx,ny))
          allocate(zht(nz))
        read(11)zht,z_scale,i_bb_mode,unkn01,varname,varunit, &
             var_scale,missing,nradar
          allocate(mosradar(nradar))
        read(11)mosradar,var
      close(11)

      elon=real(alon)/xy_scale+(nx-1)*real(dx)/dxy_scale
      elat=real(alat)/xy_scale-(ny-1)*real(dy)/dxy_scale
!!!!!!!!!!!!!!!!1================================!!!!!!!!!!!!!!!!!!!
       !write(*,*)"====================================="
       !write(*,*)"Please check your output data type"
       !write(*,*)"If Integer, select var_type=1;"
       !write(*,*)"If Real, select var_type=2"
       !write(*,*)"====================================="

!      open(31,file="var.bin",form="unformatted",access='direct', 
!     +     recl=nx*ny*4)
      open(3,file=output)
       var_type="1"
         var4=var
       select case(var_type)
        case("1")
          I_var_true=var4/var_scale
          !write(3,*)nx, ny, "T", alat/xy_scale, float(alon)/xy_scale, &
          !        float(dx)/dxy_scale, float(dy)/dxy_scale, "int16", &
          !        -99, -999
          !write(3,*)var_scale,0
          !write(3,*)0
         write(3,'(3(G0.5,:,","),4(f0.2,","),5(G0.5,:,","))')nx,ny,"T",real(alon)/map_scale,elat, &
            elon,real(alat)/map_scale,"int16",-99,missing,"EPSG:4326"
         write(3,'(a,f6.4,a,f6.4,a)')"linearTransform(",1/real(var_scale),",",0.,")"
      if(rgb(4,k)>rgb(4,1))then
         write(3,'(9999(G0.5,:,","))')rgb(1:4,1:k)
      else
         write(3,'(9999(G0.5,:,","))')((rgb(i,j),i=1,4),j=k,1,-1)
      endif
         write(frmt,'(a1,i4,a13)')"(",nx+1,'(G0.2,:,","))'
          do i = 1 , ny-1
            !write(frmt,'(a1,i5,a12)')"(",nx-1,'(i5,","),i5)'
            write(3,frmt) (var4(j,i),j=1,nx)
          enddo
          write(3,frmt,advance="no") (var4(j,ny),j=1,nx)
!          write(31,rec=1)I_var_true
!           write(*,*)"max",maxval(I_var_true)
!           write(*,*)"min",minval(I_var_true)
        case("2")
            var_true=float(var4)/float(var_scale)
!          write(31,rec=1)var_true
!           write(*,*)"max",maxval(var_true)
!           write(*,*)"min",minval(var_true)
       end select
       close(3)
       cmd="perl -pi -e 'chomp if eof' "//trim(output)
       call system(cmd)
       cmd="sed 's/-9990//g; s/-990//g' "//trim(output)//" > tmp.txt"
       call system(cmd)
       cmd="mv tmp.txt "//trim(output)
       call system(cmd)

!!!!!!!!!!!!!1================================!!!!!!!!!!!!!!!!!!!

       !write(*,*)'yyyy  = ',yyyy
       !write(*,*)'mm    = ',mm
       !write(*,*)'dd    = ',dd
       !write(*,*)'hh    = ',hh
       !write(*,*)'mn    = ',mn
       !write(*,*)'ss    = ',ss
       !write(*,*)'nx    = ',nx
       !write(*,*)'ny    = ',ny
       !write(*,*)'nz    = ',nz
       !write(*,*)'map_scale  = ',map_scale
       !write(*,*)'alon       = ',alon
       !write(*,*)'alat       = ',alat
       !write(*,*)'xy_scale   = ',xy_scale
       !write(*,*)'dx         = ',dx
       !write(*,*)'dy         = ',dy
       !write(*,*)'dxy_scale  = ',dxy_scale
       !write(*,*)'zht        = ',zht
       !write(*,*)'z_scale    = ',z_scale
       !write(*,*)'i_bb_mode  = ',i_bb_mode
       !write(*,*)'varname    = ',trim(varname)
       !write(*,*)'varunit    = ',trim(varunit)
       !write(*,*)'var_scale  = ',var_scale
       !write(*,*)'missing    = ',missing
       !!write(*,*)'nradar     = ',nradar
       !write(*,*)'mosradar   = '
        ! do ii=1,nradar
        !    write(*,*)'             ',mosradar(ii)
        ! enddo

      deallocate(var,zht,mosradar)

       end

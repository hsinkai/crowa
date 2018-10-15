
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! Introduction:
! =============
! The Program "MSG_navigation.f90" is an example code provided to give
! the users guidance for a possible implementation of the equations
! given in the LRIT/HRIT Global Specification [1] to navigate MSG
! (METEOSAT 8 onwards) data, i.e. to link the pixel coordinates column
! and line to the corresponding geographical coordinates latitude and
! longitude.
!
! Users should take note, however, that it does NOT provide software
! for reading MSG data either in LRIT/HRIT, in native or any other
! format and that EUMETSAT cannot guarantee the accuracy of this
! software. The software is for use with MSG data only and will not
! work in the given implementation for Meteosat first generation data.
! 
! Two functions/subroutines are provided:
!   pixcoord2geocoord: for conversion of column/line into lat./long.
!   geocoord2pixcoord: for conversion of lat./long. into column/line
! 
! The main routine gives an example how to utilize these two subroutines by
! reading a value for column and line at the start of the program on the
! command line and convert these values into the corresponding
! geographical coordinates and back again. The results are then printed
! out on the screen.
! 
! To Compile the program use for example:
!
! COMMAND PROMPT: f90 MSG_navigation.c -o MSG_navigation
! 
! Run the program by typing 
! 
! COMMAND PROMPT: ./MSG_navigation <COLUMS> <ROWS>
! 
! ----------------------------------------------------------------------
! 
! NOTE: Please be aware, that the program assumes the MSG image is
! ordered in the operational scanning direction which means from south
! to north and from east to west. With that the VIS/IR channels contains
! of 3712 x 3712 pixels, start to count on the most southern line and the
! most eastern column with pixel number 1,1.
!
!
! NOTE on CFAC/LFAC and COFF/LOFF:
! The parameters CFAC/LFAC and COFF/LOFF are the scaling coefficients
! provided by the navigation record of the LRIT/HRIT header and used
! by the scaling function given in Ref [1], page 28.
!
! COFF/LOFF are the offsets for column and line which are basically 1856
! and 1856 for the VIS/IR channels and refer to the middle of the image 
! (centre pixel). The values regarding the High Resolution Visible Channel 
! (HRVis) will be made available in a later issue of this software.
!
! CFAC/LFAC are responsible for the image "spread" in the NS and EW
! directions. They are calculated as follows:
! CFAC = LFAC = 2^16 / delta
! with
! delta = 83.84333 micro Radian (size of one VIS/IR MSG pixel)
! 
! CFAC     = LFAC     =  781648343.404  rad^-1 for VIS/IR
!
! which should be rounded to the nearest integer as stated in Ref [1].
! 
! CFAC     = LFAC     =  781648343  rad^-1 for VIS/IR
!
! the sign of CFAC/LFAC gives the orientation of the image.
! Negative sign give data scanned from south to north as in the
! operational scanning. Positive sign vice versa.
!
! The terms "line" and "row" are used interchangeable.
!
! PLEASE NOTE that the values of CFAC/LFAC which are given in the
! Header of the LRIT/HRIT Level 1.5 Data (see [2]) are actually in 
! Degrees and should be converted in Radians for use with these 
! routines (see example and values above).
!
! The other parameters are given in Ref [1].
!
! Further information may be found in either Ref [1], Ref [2] or
!  Ref [3] or on the Eumetsat website http://www.eumetsat.int/ .
!
!  REFERENCE:                                            
!  [1] LRIT/HRIT Global Specification                     
!      (CGMS 03, Issue 2.6, 12.08.1999)                  
!      for the parameters used in the program.
!  [2] MSG Ground Segment LRIT/HRIT Mission Specific 
!      Implementation, EUMETSAT Document, 
!      (EUM/MSG/SPE/057, Issue 6, 21. June 2006).
!  [3] MSG Level 1.5 Image Data Format Description
!      (EUM/MSG/ICD/105, Issue v5A, 22. August 2007).
!
! Please email the User Service (via
! http://www.eumetsat.int/Home/Basic/Contact_Us/index.htm) if you have
! any questions regarding this software.
!
!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


MODULE GLOBAL
  ! define global parameters used in the routines as given in Ref. [1].
  ! to distinguish between them and other variables they are written
  ! in CAPITAL LETTERS.

  REAL(KIND(0.0d0)), PARAMETER :: PI=3.14159265359d0

  REAL(KIND(0.0d0)), PARAMETER ::  SAT_HEIGHT= 42164.0d0  ! distance from Earth centre to satellite    
  REAL(KIND(0.0d0)), PARAMETER ::  R_EQ = 6378.137d0      ! radius from Earth centre to equator
  REAL(KIND(0.0d0)), PARAMETER ::  R_POL= 6356.7523d0     !
!  REAL(KIND(0.0d0)), PARAMETER ::  SUB_LON = 0.0d0       ! Longitude of Sub-Satellite Point in radiant
  REAL(KIND(0.0d0)), PARAMETER ::  SUB_LON = 140.7*PI/180.d0 ! for mtsat

!  INTEGER, PARAMETER ::  CFAC = -781648343 
!  INTEGER, PARAMETER ::  LFAC = -781648343
 REAL(KIND(0.0d0)), PARAMETER ::  CFAC = 20466275.*180/PI !for mtsat
 REAL(KIND(0.0d0)), PARAMETER ::  LFAC = 20466275.*180/PI !for mtsat

!  INTEGER, PARAMETER ::  COFF = 1856
!  INTEGER, PARAMETER ::  LOFF = 1856
  REAL, PARAMETER ::  COFF = 2750.5  ! for mtast
  REAL, PARAMETER ::  LOFF = 2750.5  ! for mtsat

END MODULE GLOBAL

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! 
! The following program gives an example how to incorporate the
! functions "geocoord2pixcoord" and "pixcoord2geocoord"
!
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!


PROGRAM navi
  
  USE GLOBAL

 IMPLICIT NONE

! command line variables
  CHARACTER *100 BUFFER
  integer k, iof

! working variables
  INTEGER :: column, row, line, col,i,j,ll,iv
  INTEGER :: c, l
  INTEGER :: ccc, lll

  REAL(KIND(0.0d0)) :: d_lat, d_lon
  REAL(KIND(0.0d0)) :: latitude,longitude
  REAL(KIND(0.0d0)) :: lat1,lat2,lon1,lon2
  character, allocatable, dimension(:,:) :: buf
  character :: buf2(5500,5500)
  integer iargc
  character *7 img,fname

  k = iargc()

! command line
  if ( k .NE. 6 ) then
     print *, " call of program "
     print *, " ./MTSAT_navi <BOT LAT> <UPP LAT> <LEF LON> <RGT LON> <IMG> <int>"
     print *, " EXIT! "
     stop
  end if

  call getarg(1,BUFFER)
  read(buffer,*) lat1
  call getarg(2,BUFFER)
  read(buffer,*) lat2
  call getarg(3,BUFFER)
  read(buffer,*) lon1
  call getarg(4,BUFFER)
  read(buffer,*) lon2
  call getarg(5,BUFFER)
  read(buffer,*) img
  call getarg(6,BUFFER)
  read(buffer,*) iv
!  lat1=10.
!  lat2=40.
!  lon1=110.
!  lon2=140.
!  img="ir1"

  if( lat2.lt.lat1.or.lon2.lt.lon1)then
      print *, " call of program "
     print *, " ./MTSAT_navigation <BOT LAT> <UPP LAT> <LEF LON> <RGT LON> <int>"
     print *, " EXIT! "
     stop
  endif

!  determine col and line number
  c=(lat2-lat1)*100/iv+1
  l=(lon2-lon1)*100/iv+1

  print *,"col= ",c,",line= ",l
  !open input image svissr_ir1.gray
  !open(2,file="svissr_vis.gray",access='direct',form="unformatted",recl=2750,status="old")
  fname=img(1:3)//".dat"
  inquire(file=fname, iostat=iof)
  if ( iof .ne. 0 ) then
     print *, fname, " not found!"
     stop
  endif
  open(2,file=fname,access='direct',form="unformatted",recl=5500,status="old",iostat=iof)
  if ( iof .ne. 0 ) then
     print *, fname, " file open error !"
     stop
  endif
  !open output image
  open(1,file="out.bin",access='direct',form="unformatted",recl=l,status="unknown")

  do i = 1 , 5500
    read(2,rec=i)(buf2(i,j),j=1,5500)
  enddo

  line=0
  ALLOCATE ( buf(c,l))
  do i = nint(lat1*100) , nint(lat2*100) , iv
   line=line+1
   ll=c-line+1
   col=0
     do j = nint(lon1*100) , nint(lon2*100) , iv
     col=col+1
     latitude=real(i)/100
     longitude=real(j)/100

     call geocoord2pixcoord(latitude, longitude, COFF, LOFF, ccc, lll)
  
!     print *,line,col,c,l
     buf(ll,col)=buf2(lll,ccc)
  ! print out results
!  print *, "c=",c," l=",l," lat=",latitude," lon=",longitude, " col=",ccc, "row=",lll
!  print *, "lat=",latitude," lon=",longitude, " col=",ccc, "row=",lll
     enddo
     write(1,rec=ll)(buf(ll,j),j=1,l)

   enddo

   DEALLOCATE ( buf )

END PROGRAM navi





!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  
! subroutine pixcoord2geocoord 
!  
!  PURPOSE: 
!  return the geograhic latitude and longitude of an MSG image   
!    for a given pair of latitude/longitude.             
!    (based on the formulas given in Ref. [1])                
!                                                        
!                                                        
!  DEPENDENCIES:                                         
!    none                                                 
!                                                        
!                                                        
!  REFERENCE:                                            
!  [1] LRIT/HRIT Global Specification                     
!      (CGMS 03, Issue 2.6, 12.08.1999)                  
!      for the parameters used in the program           
!  [2] MSG Ground Segment LRIT/HRIT Mission Specific 
!      Implementation, EUMETSAT Document, 
!      (EUM/MSG/SPE/057, Issue 6, 21. June 2006).
!                                                        
!  MODIFICATION HISTORY:                                 
!    Version 1.01
!  08.08.2008 removed a bug in longi = atan(s2/s1) statement
!    Copyright(c) EUMETSAT 2005, 2009
!                                                        
!                                                        
!  INPUT:                                                
!    row   (int) row-value of the pixel
!    colum (int) columb-value of the pixel
!    ccoff (int) coefficient of the scalling function    
!                (see page 28, Ref [1])                  
!                NOTE: since Fortran cannot distinguish between 
!                      upper case and lower case letters the name
!                      "ccoff" is used rather than "COFF" to distinguish
!                      between them.
!    lloff (int) coefficient of the scalling function    
!                (see page 28, Ref [1])                  
!                NOTE: since Fortran cannot distinguish between 
!                      upper case and lower case letters the name
!                      "ccoff" is used rather than "COFF" to distinguish
!                      between them.
!                                                        
!  OUTPUT:                                               
!    latitude (double) geographic Latitude of the wanted pixel [Degrees]
!    longitude (double) geographic Longitude of the wanted pixel [Degrees]
!                                                        
!                                                        
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

SUBROUTINE pixcoord2geocoord( column,  row,  ccoff,  lloff, latitude, longitude)

  USE GLOBAL

  IMPLICIT NONE

  INTEGER, INTENT (IN) :: column, row, ccoff, lloff
  REAL(KIND(0.0d0)) , INTENT (OUT) :: latitude, longitude

  
  REAL(KIND(0.0d0)) :: s1, s2, s3, sn, sd, sxy
  REAL(KIND(0.0d0)) :: x, y, xx, yy
  REAL(KIND(0.0d0)) :: longi, lati
  REAL(KIND(0.0d0)) :: lat
  REAL(KIND(0.0d0)) :: lon


  REAL(KIND(0.0d0)) :: a, b, sa

  INTEGER ::  c, l


  c=column
  l=row

  !  calculate viewing angle of the satellite by use of the equation 
  !  on page 28, Ref [1]. 

  x = (2.0d0**16.0d0 * ( DBLE(c) - DBLE(ccoff) )) / DBLE(CFAC)
  y = (2.0d0**16.0d0 * ( DBLE(l) - DBLE(lloff) )) / DBLE(LFAC)


  !  now calculate the inverse projection using equations on page 25, Ref. [1]  

  !  first check for visibility, whether the pixel is located on the Earth 
  !  surface or in space. 
  !  To do this calculate the argument to sqrt of "sd", which is named "sa". 
  !  If it is negative then the sqrt will return NaN and the pixel will be 
  !  located in space, otherwise all is fine and the pixel is located on the 
  !  Earth surface.

  sa =  (SAT_HEIGHT * cos(x) * cos(y) )**2 - (cos(y)*cos(y) + 1.006803d0 * sin(y)*sin(y)) * 1737121856.0d0

  ! take care if the pixel is in space, that an error code will be returned
  if ( sa .LE. 0.0 ) then
     latitude = -999.999
     longitude = -999.999
     return 
  end if

  ! now calculate the rest of the formulas using eq. on page 25 Ref [1]

  sd = sqrt( (SAT_HEIGHT * cos(x) * cos(y) )**2	- (cos(y)*cos(y) + 1.006803d0 * sin(y)*sin(y)) * 1737121856.0d0 )
  sn = (SAT_HEIGHT * cos(x) * cos(y) - sd) / ( cos(y)*cos(y) + 1.006803d0 * sin(y)*sin(y) ) 
  
  s1 = SAT_HEIGHT - sn * cos(x) * cos(y)
  s2 = sn * sin(x) * cos(y)
  s3 = -sn * sin(y)

  sxy = sqrt( s1*s1 + s2*s2 )

  ! using the previous calculations now the inverse projection can be
  ! calculated, which means calculating the lat./long. from the pixel
  ! row and column by equations on page 25, Ref [1].

  longi = atan(s2/s1) + SUB_LON
  lati  = atan((1.006803d0*s3)/sxy)
  ! convert from radians into degrees
  latitude = lati*180.0d0/PI
  longitude = longi*180.0d0/PI


END SUBROUTINE pixcoord2geocoord


!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
! subroutine geocoord2pixcoord                                    
!                                                       
! PURPOSE:                                              
!   return the pixel column and line of an MSG image 
!   for a given pair of geographic latitude/longitude.                   
!   (based on the formulas given in Ref. [1])                
!                                                       
!                                                       
! DEPENDENCIES:                                         
!   none                                       
!                                                       
!                                                       
! REFERENCE:                                            
! [1] LRIT/HRIT Global Specification                     
!     (CGMS 03, Issue 2.6, 12.08.1999)                  
!     for the parameters used in the program.
! [2] MSG Ground Segment LRIT/HRIT Mission Specific 
!     Implementation, EUMETSAT Document, 
!     (EUM/MSG/SPE/057, Issue 6, 21. June 2006).
!                                                       
!                                                       
! MODIFICATION HISTORY:
!   Version 1.01
!    Copyright(c) EUMETSAT 2005, 2009
!                                                       
!                                                       
! INPUT:                                                
!   latitude  (double) geographic Latitude of a point [Degrees] 
!   longitude (double) geographic Longitude of a point [Degrees]
!   ccoff (int)        coefficient of the scalling function   
!                      (see page 28, Ref [1])                 
!                      NOTE: since Fortran cannot distinguish between 
!                            upper case and lower case letters the name
!                            "ccoff" is used rather than "COFF" 
!                            to distinguish between them.
!                   
!   lloff (int)        coefficient of the scalling function   
!                      (see page 28, Ref [1])                 
!                      NOTE: since Fortran cannot distinguish between 
!                            upper case and lower case letters the name
!                            "lloff" is used rather than "LOFF" 
!                            to distinguish between them.
!                                                       
!                                                       
! OUTPUT:                                               
!   row    (int)       row-value of the pixel
!   column (int)       column-value of the pixel
!                                                       
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

SUBROUTINE geocoord2pixcoord( latitude,  longitude,  ccoff,  lloff,  column, row)

  USE GLOBAL

  IMPLICIT NONE


  REAL(KIND(0.0d0)), INTENT (IN) :: latitude, longitude
  REAL, INTENT (IN)  :: ccoff, lloff
  INTEGER, INTENT (OUT) :: column, row
  

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


  lati= latitude
  longi= longitude

  ! check if the values are sane, otherwise return error value
!  if (lati .LT. -90.0d0 .OR. lati .GT. 90.0d0 .OR. longi .LT. -180.0d0 .OR. longi .GT. 180.0d0 ) then
!     row = -999
!     column = -999
!     return
!  end if

  ! convert them to radians 
  lat = lati*PI / 180.0d0
  lon = longi *PI / 180.0d0


  ! calculate the geocentric latitude from the       
  ! geographic one using equations on page 24, Ref. [1] 

  c_lat = atan ( (0.993243d0*(sin(lat)/cos(lat)) ))
      
  ! using c_lat calculate the length from the Earth 
  ! centre to the surface of the Earth ellipsoid    
  ! equations on page 23, Ref [1]                      
  
  re = R_POL / sqrt( (1.0d0 - 0.00675701d0 * cos(c_lat) * cos(c_lat) ) )


  ! calculate the forward projection using equations on page 24, Ref. [1]

  rl = re
  r1 = SAT_HEIGHT - rl * cos(c_lat) * cos(lon - SUB_LON)
  r2 = - rl *  cos(c_lat) * sin(lon - SUB_LON)
  r3 = rl * sin(c_lat)
  rn = sqrt( r1*r1 + r2*r2 +r3*r3 )

  ! check for visibility, whether the point on the Earth given by the
  ! latitude/longitude pair is visible from the satellte or not. This 
  ! is given by the dot product between the vectors of:
  ! 1) the point to the spacecraft,
  ! 2) the point to the centre of the Earth.
  ! If the dot product is positive the point is visible otherwise it
  ! is invisible.

  dotprod = r1*(rl * cos(c_lat) * cos(lon - SUB_LON)) - r2*r2 - r3*r3*((r_EQ/R_POL)**2)

  if (dotprod .LE. 0.0d0 ) then
!     column = -999
!     row = -999
     column = 1
     row = 1
     return
  end if

  ! the forward projection is x and y 

  xx = atan( (-r2/r1) )
  yy = asin( (-r3/rn) )


  ! convert to pixel column and row using the scaling functions on 
  ! page 28, Ref. [1]. And finding nearest integer value for them. 

  cc = DBLE(ccoff) + xx *  2.0d0**(-16.0d0) * DBLE(CFAC)
  ll = DBLE(lloff) + yy *  2.0d0**(-16.0d0) * DBLE(LFAC)


  ccc=nint(cc)
  lll=nint(ll)		

  column = ccc
  row = lll

      

END SUBROUTINE geocoord2pixcoord


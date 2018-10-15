SUBROUTINE L2DINTERPOL(IntIm,Image,x,y,NPts,M,N)
  implicit none

  mwSize, PARAMETER             :: dp = kind(0.d0) ! Double precision
  mwSize                        :: NPts, M,N       ! Input
  REAL(dp),DIMENSION(Npts)      :: x,y             ! Input
  REAL(dp),DIMENSION(M,N)       :: Image           ! Input
  mwSize                        :: jj
  mwSize, DIMENSION(NPts)       :: x1,y1,x2,y2      
  REAL(dp),DIMENSION(Npts)      :: wx1,wx2,wy1,wy2
  REAL(dp),DIMENSION(Npts)      :: IntIm           ! Output


  x1 = FLOOR(x)
  x2 = CEILING(x)
  y1 = FLOOR(y)
  y2 = CEILING(y)

  wx1 = x2-x
  wy1 = y2-y

  wx2 = 1 - wx1
  wy2 = 1 - wy1

  FORALL( jj=1 : NPts)

     IntIm(jj) = wy1(jj)*(wx1(jj)*Image(y1(jj),x1(jj))+wx2(jj)*
 $        Image(y1(jj),x2(jj))) + wy2(jj)*(wx1(jj)*
     $        Image(y2(jj),x1(jj))+wx2(jj)*Image(y2(jj),x2(jj)))

  END FORALL


  RETURN
  END

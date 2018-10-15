SUBROUTINE L2DINTERPOL3(IntIm,Image,x,y,NPts,M,N)
!   IntIm
!   Image
!   x,y:
  INTEGER*8        :: NPts,M,N,jj
  INTEGER*8        :: x1(NPts),y1(NPts),x2(NPts),y2(NPts)
  DOUBLE PRECISION :: IntIm(NPts)
  DOUBLE PRECISION :: Image(M,N)
  DOUBLE PRECISION :: f1,f2
  DOUBLE PRECISION :: x(NPts),y(NPts)
  DOUBLE PRECISION :: wx1(NPts),wx2(NPts),wy1(NPts),wy2(NPts)

!c Take the nearest integers around the input. 

   x1 = FLOOR(x)
   x2 = CEILING(x)
   y1 = FLOOR(y)
   y2 = CEILING(y)

   wx1 = (x2-x)/(x2-x1)
   wx2 = (x-x1)/(x2-x1)
   wy1 = (y2-y)/(y2-y1)
   wy2 = (y-y1)/(y2-y1)

!c Whenever the input are already integers, weights go to infinity,
!c so set each pair to 1 and 0.

   WHERE(x1 .EQ. x2)
      wx1 = 1.
      wx2 = 0.
   END WHERE

   WHERE (y1 .EQ. y2)
      wy1 = 1.
      wy2 = 0.
   END WHERE

!c Main calculation, loop over each element of the input. 

  DO 10 jj=1,NPts


     f1 = wx1(jj)*Image(y1(jj),x1(jj)) + wx2(jj)*Image(y1(jj),x2(jj))
     f2 = wx1(jj)*Image(y2(jj),x1(jj)) + wx2(jj)*Image(y2(jj),x2(jj))

     IntIm(jj) = wy1(jj)*f1 + wy2(jj)*f2


 10   CONTINUE

  RETURN
  END

      open(1,file="lookup_ir.tab")
      open(2,file="lookup.tab")
      do i = 1 , 256
          read(1,*)it,buf
          read(2,*)itt,ir,ig,ib
          print *,nint(buf),ir,ig,ib
      enddo
  
      stop
      end

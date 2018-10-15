  integer, parameter  :: i_byte  = selected_int_kind(1)      ! byte  integer
  integer, parameter  :: i_short = selected_int_kind(4)      ! short integer
  integer, parameter  :: i_long  = selected_int_kind(8)      ! long  integer
  integer, parameter :: llong_t = selected_int_kind(16)     ! llong integer
  integer, parameter  :: r_single = selected_real_kind(6)  ! single precision
  integer, parameter  :: r_double = selected_real_kind(15) ! double precision

type  Basic_Info
    sequence
    integer(i_byte)  :: HeaderNum
    integer(i_short) :: BlockLen
    integer(i_short) :: headernumb
    integer(i_byte)  :: byteOrder
    character(len=16):: satName
    character(len=16):: proName
    character(len=4) :: ObsType1
    character(len=2) :: ObsType2
    integer(i_short) :: TimeLine
    real(r_double)   :: ObsStartTime
    real(r_double)   :: ObsEndTime
    real(r_double)   :: fileCreationMjd
    integer(i_long)  :: totalHeaderLen
    integer(i_long)  :: dataLen
    integer(i_byte)  :: qflag1
    integer(i_byte)  :: qflag2 
    integer(i_byte)  :: qflag3
    integer(i_byte)  :: qflag4
    character(len=32):: verName
    character(len=128):: fileName
    character(len=40):: spare
end type Basic_Info

type Data_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    integer(i_short)  :: bitPix
    integer(i_short)  :: nPix
    integer(i_short)  :: nLin
    integer(i_byte)   :: comp
    character(len=40):: spare
end type Data_Info

type Proj_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    real(r_double)     :: subLon
    integer(i_long)  :: cfac
    integer(i_long)  :: lfac
    real(r_single)     :: coff
    real(r_single)     :: loff
    real(r_double)     :: satDis
    real(r_double)     :: eqtrRadius
    real(r_double)     :: polrRadius
    real(r_double)     :: projParam1
    real(r_double)     :: projParam2
    real(r_double)     :: projParam3
    real(r_double)     :: projParamSd
    integer(i_short)  :: resampleKind
    integer(i_short)  :: resampleSize
    character(len=40):: spare
end type Proj_Info

type Navi_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    real(r_double)     :: navMjd
    real(r_double)     :: sspLon
    real(r_double)     :: sspLat
    real(r_double)     :: satDis
    real(r_double)     :: nadirLon
    real(r_double)     :: nadirLat
    real(r_double)     :: sunPos_x
    real(r_double)     :: sunPos_y
    real(r_double)     :: sunPos_z
    real(r_double)     :: moonPos_x
    real(r_double)     :: moonPos_y
    real(r_double)     :: moonPos_z
    character(len=40):: spare
end type Navi_Info

type Calib_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    integer(i_short)  :: bandNo
    real(r_double)     :: waveLen
    integer(i_short)  :: bitPix
    integer(i_short)  :: errorCount
    integer(i_short)  :: outCount
    real(r_double)     :: gain_cnt2rad
    real(r_double)     :: cnst_cnt2rad
    real(r_double)     :: rad2btp_c0
    real(r_double)     :: rad2btp_c1
    real(r_double)     :: rad2btp_c2
    real(r_double)     :: btp2rad_c0
    real(r_double)     :: btp2rad_c1
    real(r_double)     :: btp2rad_c2
    real(r_double)     :: lightSpeed
    real(r_double)     :: planckConst
    real(r_double)     :: bolzConst
    character(len=40):: spare
    !real(r_double)     :: rad2albedo
    !character(len=104)::spareV
end type Calib_Info

type InterCalib_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    real(r_double)     :: gsicsCorr_C
    real(r_double)     :: gsicsCorr_C_er
    real(r_double)     :: gsicsCorr_1
    real(r_double)     :: gsicsCorr_1_er
    real(r_double)     :: gsicsCorr_2
    real(r_double)     :: gsicsCorr_2_er
    real(r_double)     :: gsicsCorr_StrMJD
    real(r_double)     :: gsicsCorr_EndMJD
    !character(len=64):: gsicsCorrInfo
    real(r_single)     :: gsicsUpperLimit
    real(r_single)     :: gsicsLowerLimit
    character(len=128)::gsicsFilename
    character(len=56)::spare
end type InterCalib_Info

type Segm_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    integer(i_byte)   :: totalSegNum
    integer(i_byte)   :: segSeqNo
    integer(i_short)  :: strLineNo
    character(len=40):: spare
end type Segm_Info

type NaviCorr_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    real(r_single)     :: RoCenterColumn
    real(r_single)     :: RoCenterLine
    real(r_double)     :: RoCorrection
    integer(i_short)  :: correctNum
    integer(i_short)  :: lineNo(2)
    real(r_single)     :: columnShift(2)
    real(r_single)     :: lineShift(2)
    !integer(i_short)  :: lineNo2
    !real(r_single)     :: columnShift2
    !real(r_single)     :: lineShift2
    character(len=40):: spare
end type NaviCorr_Info

type ObsTime_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    integer(i_short)  :: obsNum
    integer(i_short)  :: lineNo(4)
    real(r_double)     :: obsMJD(4)
    !integer(i_short)  :: lineNo2
    !real(r_double)     :: obsMJD2
    !integer(i_short)  :: lineNo3
    !real(r_double)     :: obsMJD3
    !integer(i_short)  :: lineNo4
    !real(r_double)     :: obsMJD4
    character(len=40):: spare
end type ObsTime_Info

type Error_Info
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_long )  :: BlockLen
    integer(i_short)  :: errorNum
    !integer(i_short)  :: lineNo(0)
    !integer(i_short)  :: errPixNum(0)
    character(len=40):: spare
end type Error_Info

type Spare
    sequence
    integer(i_byte)   :: HeaderNum
    integer(i_short)  :: BlockLen
    character(len=256):: spare
end type Spare

type Correct_Table
    sequence
    integer(i_byte)  :: flag
    integer          :: startLineNo
    integer          :: lineNum
    real             :: cmpCoff
    real             :: cmpLoff
end type Correct_Table

type HisdHeader
    sequence
    type(Basic_Info) :: basic
    type(Data_Info)  :: data
    type(Proj_Info)  :: proj
    type(Navi_Info)  :: Navi_Info
    type(Calib_Info) :: calib
    type(InterCalib_Info):: interCalib
    type(Segm_Info)  :: seg
    type(NaviCorr_Info) :: navcorr 
    type(ObsTime_Info) :: obstime
    type(Error_Info) :: error
    type(Spare)      :: spare
    !type(Correct_Table)::correct_table
end type HisdHeader

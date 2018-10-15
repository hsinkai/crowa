# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models


class Aquaculture(models.Model):
    issuetime = models.DateTimeField(db_column='issueTime')  # Field name made lowercase.
    update = models.DateTimeField()
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=10)
    lat = models.FloatField()
    lon = models.FloatField()
    at = models.DateTimeField()
    t = models.IntegerField(db_column='T')  # Field name made lowercase.
    td = models.FloatField(db_column='Td')  # Field name made lowercase.
    rh = models.IntegerField(db_column='RH')  # Field name made lowercase.
    pop6h = models.IntegerField(db_column='PoP6h', blank=True, null=True)  # Field name made lowercase.
    pop6hend = models.DateTimeField(db_column='PoP6hEnd', blank=True, null=True)  # Field name made lowercase.
    p = models.IntegerField(db_column='P', blank=True, null=True)  # Field name made lowercase.
    pop12h = models.IntegerField(db_column='PoP12h', blank=True, null=True)  # Field name made lowercase.
    pop12hend = models.DateTimeField(db_column='PoP12hEnd', blank=True, null=True)  # Field name made lowercase.
    dir = models.CharField(max_length=3)
    mspeed = models.CharField(db_column='mSpeed', max_length=5)  # Field name made lowercase.
    beauspeed = models.CharField(db_column='beauSpeed', max_length=4)  # Field name made lowercase.
    ci = models.IntegerField(db_column='CI')  # Field name made lowercase.
    citext = models.CharField(db_column='CIText', max_length=4)  # Field name made lowercase.
    apparentt = models.IntegerField(db_column='ApparentT')  # Field name made lowercase.
    wxtext = models.CharField(db_column='Wxtext', max_length=15)  # Field name made lowercase.
    wxvalue = models.IntegerField(db_column='WxValue')  # Field name made lowercase.
    wxend = models.DateTimeField(db_column='WxEnd')  # Field name made lowercase.
    weatherdescription = models.CharField(db_column='WeatherDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    weatherdescriptionend = models.DateTimeField(db_column='WeatherDescriptionEnd', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'AquaCulture'
        unique_together = (('id', 'at'),)


class Buoy(models.Model):
    stationid = models.CharField(db_column='stationId', primary_key=True, max_length=10)  # Field name made lowercase.
    obstime = models.DateTimeField(db_column='obsTime')  # Field name made lowercase.
    gust1 = models.IntegerField(blank=True, null=True)
    avgwind1 = models.IntegerField(db_column='avgWind1', blank=True, null=True)  # Field name made lowercase.
    dir1 = models.IntegerField(blank=True, null=True)
    gust2 = models.IntegerField(blank=True, null=True)
    avgwind2 = models.IntegerField(db_column='avgWind2', blank=True, null=True)  # Field name made lowercase.
    dir2 = models.IntegerField(blank=True, null=True)
    pressure = models.IntegerField(blank=True, null=True)
    temp = models.IntegerField(blank=True, null=True)
    stemp = models.IntegerField(db_column='sTemp', blank=True, null=True)  # Field name made lowercase.
    height = models.IntegerField(blank=True, null=True)
    cycle = models.IntegerField(blank=True, null=True)
    wavedir = models.IntegerField(db_column='waveDir', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Buoy'
        unique_together = (('stationid', 'obstime'),)


class Gt(models.Model):
    id = models.CharField(db_column='ID', primary_key=True, max_length=10)  # Field name made lowercase.
    longitude = models.FloatField(db_column='Longitude', blank=True, null=True)  # Field name made lowercase.
    latitude = models.FloatField(db_column='Latitude', blank=True, null=True)  # Field name made lowercase.
    temp = models.IntegerField(db_column='Temp', blank=True, null=True)  # Field name made lowercase.
    rh = models.IntegerField(db_column='RH', blank=True, null=True)  # Field name made lowercase.
    rain = models.FloatField(db_column='Rain', blank=True, null=True)  # Field name made lowercase.
    cloud = models.IntegerField(db_column='Cloud', blank=True, null=True)  # Field name made lowercase.
    ws = models.IntegerField(db_column='WS', blank=True, null=True)  # Field name made lowercase.
    wd = models.IntegerField(db_column='WD', blank=True, null=True)  # Field name made lowercase.
    at = models.IntegerField(db_column='AT', blank=True, null=True)  # Field name made lowercase.
    time = models.DateTimeField(db_column='Time')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'GT'
        unique_together = (('id', 'time'),)


class Harbor(models.Model):
    issuetime = models.DateTimeField(db_column='issueTime')  # Field name made lowercase.
    update = models.DateTimeField()
    id = models.CharField(primary_key=True, max_length=4)
    name = models.CharField(max_length=10)
    lat = models.FloatField()
    lon = models.FloatField()
    at = models.DateTimeField()
    t = models.IntegerField(db_column='T')  # Field name made lowercase.
    td = models.FloatField(db_column='Td')  # Field name made lowercase.
    rh = models.IntegerField(db_column='RH')  # Field name made lowercase.
    pop6h = models.IntegerField(db_column='PoP6h', blank=True, null=True)  # Field name made lowercase.
    pop6hend = models.DateTimeField(db_column='PoP6hEnd', blank=True, null=True)  # Field name made lowercase.
    pop12h = models.IntegerField(db_column='PoP12h', blank=True, null=True)  # Field name made lowercase.
    pop12hend = models.DateTimeField(db_column='PoP12hEnd', blank=True, null=True)  # Field name made lowercase.
    dir = models.CharField(max_length=3)
    mspeed = models.CharField(db_column='mSpeed', max_length=5)  # Field name made lowercase.
    beauspeed = models.CharField(db_column='beauSpeed', max_length=4)  # Field name made lowercase.
    ci = models.IntegerField(db_column='CI')  # Field name made lowercase.
    citext = models.CharField(db_column='CIText', max_length=4)  # Field name made lowercase.
    apparentt = models.IntegerField(db_column='ApparentT')  # Field name made lowercase.
    wxtext = models.CharField(db_column='Wxtext', max_length=15)  # Field name made lowercase.
    wxvalue = models.IntegerField(db_column='WxValue')  # Field name made lowercase.
    wxend = models.DateTimeField(db_column='WxEnd')  # Field name made lowercase.
    weatherdescription = models.CharField(db_column='WeatherDescription', max_length=255, blank=True, null=True)  # Field name made lowercase.
    weatherdescriptionend = models.DateTimeField(db_column='WeatherDescriptionEnd', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Harbor'
        unique_together = (('id', 'at'),)


class Marine(models.Model):
    issuetime = models.DateTimeField(db_column='issueTime')  # Field name made lowercase.
    update = models.DateTimeField()
    locationname = models.CharField(db_column='locationName', primary_key=True, max_length=10)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='startTime')  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='endTime')  # Field name made lowercase.
    wx = models.CharField(db_column='Wx', max_length=10)  # Field name made lowercase.
    winddir = models.CharField(db_column='WindDir', max_length=10)  # Field name made lowercase.
    windspeed = models.CharField(db_column='WindSpeed', max_length=50)  # Field name made lowercase.
    waveheight = models.CharField(db_column='WaveHeight', max_length=10)  # Field name made lowercase.
    wavetype = models.CharField(db_column='WaveType', max_length=10)  # Field name made lowercase.
    wxvalue = models.IntegerField(db_column='WxValue')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'Marine'
        unique_together = (('locationname', 'starttime'),)


class Pointindex(models.Model):
    type = models.CharField(primary_key=True, max_length=10)
    no = models.IntegerField()
    lat = models.DecimalField(max_digits=6, decimal_places=3)
    lon = models.DecimalField(max_digits=6, decimal_places=3)
    buoyid = models.CharField(db_column='BuoyId', max_length=6, blank=True, null=True)  # Field name made lowercase.
    tideid = models.CharField(db_column='TideId', max_length=6, blank=True, null=True)  # Field name made lowercase.
    harborid = models.CharField(db_column='HarborId', max_length=6, blank=True, null=True)  # Field name made lowercase.
    staiondaylightid = models.CharField(db_column='StaionDaylightId', max_length=6, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'PointIndex'
        unique_together = (('type', 'no'),)


class Stcfor(models.Model):
    type = models.CharField(primary_key=True, max_length=15)
    no = models.IntegerField()
    time = models.DateTimeField()
    depth = models.IntegerField()
    lat = models.DecimalField(max_digits=6, decimal_places=3)
    lon = models.DecimalField(max_digits=6, decimal_places=3)
    temp = models.FloatField()
    speed = models.FloatField()
    dir = models.FloatField()

    class Meta:
        managed = False
        db_table = 'STCFor'
        unique_together = (('type', 'no', 'time', 'depth'),)


class Stobs(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    time = models.DateTimeField()
    lat = models.FloatField()
    lon = models.FloatField()
    sst = models.FloatField(blank=True, null=True)
    ws = models.FloatField(blank=True, null=True)
    oni = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'STObs'
        unique_together = (('name', 'time'),)


class Stwarning(models.Model):
    name = models.CharField(primary_key=True, max_length=10)
    time = models.DateTimeField()
    warning = models.CharField(max_length=100)
    max_fhs = models.FloatField()

    class Meta:
        managed = False
        db_table = 'STWarning'
        unique_together = (('name', 'time'),)


class Stationdaylight(models.Model):
    locationname = models.CharField(db_column='locationName', max_length=30, blank=True, null=True)  # Field name made lowercase.
    stationid = models.CharField(db_column='stationId', primary_key=True, max_length=6)  # Field name made lowercase.
    obstime = models.DateTimeField(db_column='obsTime')  # Field name made lowercase.
    pressure = models.FloatField(blank=True, null=True)
    temp = models.FloatField(blank=True, null=True)
    humidity = models.IntegerField(blank=True, null=True)
    wspeed = models.FloatField(db_column='wSpeed', blank=True, null=True)  # Field name made lowercase.
    wdir = models.CharField(db_column='wDir', max_length=20, blank=True, null=True)  # Field name made lowercase.
    precipitation = models.FloatField(db_column='Precipitation', blank=True, null=True)  # Field name made lowercase.
    sunshine = models.FloatField(db_column='Sunshine', blank=True, null=True)  # Field name made lowercase.
    tmax = models.FloatField(db_column='TMax', blank=True, null=True)  # Field name made lowercase.
    tmin = models.FloatField(db_column='TMin', blank=True, null=True)  # Field name made lowercase.
    tavg = models.FloatField(db_column='TAvg', blank=True, null=True)  # Field name made lowercase.
    updatetime = models.DateTimeField(db_column='updateTime')  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StationDaylight'
        unique_together = (('stationid', 'obstime'),)


class Stationobs(models.Model):
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    stationid = models.CharField(db_column='stationId', primary_key=True, max_length=6)  # Field name made lowercase.
    obstime = models.DateTimeField(db_column='obsTime')  # Field name made lowercase.
    elev = models.IntegerField(db_column='ELEV', blank=True, null=True)  # Field name made lowercase.
    wdir = models.IntegerField(db_column='WDIR', blank=True, null=True)  # Field name made lowercase.
    wdsd = models.FloatField(db_column='WDSD', blank=True, null=True)  # Field name made lowercase.
    temp = models.FloatField(db_column='TEMP', blank=True, null=True)  # Field name made lowercase.
    humd = models.FloatField(db_column='HUMD', blank=True, null=True)  # Field name made lowercase.
    pres = models.FloatField(db_column='PRES', blank=True, null=True)  # Field name made lowercase.
    sun = models.FloatField(db_column='SUN', blank=True, null=True)  # Field name made lowercase.
    h_24r = models.FloatField(db_column='H_24R', blank=True, null=True)  # Field name made lowercase.
    h_fx = models.FloatField(db_column='H_FX', blank=True, null=True)  # Field name made lowercase.
    h_xd = models.IntegerField(db_column='H_XD', blank=True, null=True)  # Field name made lowercase.
    h_fxt = models.CharField(db_column='H_FXT', max_length=20, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StationObs'
        unique_together = (('stationid', 'obstime'),)


class Stationobs2(models.Model):
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    stationid = models.CharField(db_column='stationId', primary_key=True, max_length=6)  # Field name made lowercase.
    obstime = models.DateTimeField(db_column='obsTime')  # Field name made lowercase.
    elev = models.IntegerField(db_column='ELEV', blank=True, null=True)  # Field name made lowercase.
    wdir = models.IntegerField(db_column='WDIR', blank=True, null=True)  # Field name made lowercase.
    wdsd = models.FloatField(db_column='WDSD', blank=True, null=True)  # Field name made lowercase.
    temp = models.FloatField(db_column='TEMP', blank=True, null=True)  # Field name made lowercase.
    humd = models.FloatField(db_column='HUMD', blank=True, null=True)  # Field name made lowercase.
    pres = models.FloatField(db_column='PRES', blank=True, null=True)  # Field name made lowercase.
    number_24r = models.FloatField(db_column='24R', blank=True, null=True)  # Field name made lowercase. Field renamed because it wasn't a valid Python identifier.
    h_fx = models.FloatField(db_column='H_FX', blank=True, null=True)  # Field name made lowercase.
    h_xd = models.IntegerField(db_column='H_XD', blank=True, null=True)  # Field name made lowercase.
    h_fxt = models.IntegerField(db_column='H_FXT', blank=True, null=True)  # Field name made lowercase.
    h_f10 = models.FloatField(db_column='H_F10', blank=True, null=True)  # Field name made lowercase.
    h_10d = models.IntegerField(db_column='H_10D', blank=True, null=True)  # Field name made lowercase.
    h_f10t = models.IntegerField(db_column='H_F10T', blank=True, null=True)  # Field name made lowercase.
    h_uvi = models.FloatField(db_column='H_UVI', blank=True, null=True)  # Field name made lowercase.
    d_tx = models.FloatField(db_column='D_TX', blank=True, null=True)  # Field name made lowercase.
    d_txt = models.IntegerField(db_column='D_TXT', blank=True, null=True)  # Field name made lowercase.
    d_ts = models.FloatField(db_column='D_TS', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        managed = False
        db_table = 'StationObs2'
        unique_together = (('stationid', 'obstime'),)


class Tide(models.Model):
    locationname = models.CharField(db_column='locationName', max_length=20)  # Field name made lowercase.
    stationid = models.CharField(db_column='stationId', primary_key=True, max_length=6)  # Field name made lowercase.
    starttime = models.DateTimeField(db_column='startTime')  # Field name made lowercase.
    endtime = models.DateTimeField(db_column='endTime')  # Field name made lowercase.
    lunar = models.CharField(max_length=5)
    range = models.CharField(max_length=2)
    tide = models.CharField(max_length=2)
    time = models.DateTimeField()
    twvd = models.IntegerField(db_column='TWVD', blank=True, null=True)  # Field name made lowercase.
    local = models.IntegerField()
    relative = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'Tide'
        unique_together = (('stationid', 'time'),)


class Wave(models.Model):
    type = models.CharField(primary_key=True, max_length=15)
    no = models.IntegerField()
    time = models.DateTimeField()
    lon = models.DecimalField(max_digits=6, decimal_places=3)
    lat = models.DecimalField(max_digits=6, decimal_places=3)
    dir = models.FloatField()
    hs = models.FloatField()
    fd = models.FloatField()
    fhs = models.FloatField()

    class Meta:
        managed = False
        db_table = 'Wave'
        unique_together = (('type', 'time', 'no'),)


class ManageInfoData(models.Model):
    longname = models.CharField(unique=True, max_length=16)
    category = models.CharField(max_length=8)
    is_api_available = models.IntegerField()
    description = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'manage_info_data'


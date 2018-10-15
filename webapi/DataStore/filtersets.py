# -*- coding: utf-8 -*-

from django_filters.rest_framework import MultipleChoiceFilter
from . import models
from DataStore.models import (
    Gt,
    Marine,
    Aquaculture,
    Buoy,
    Fishing,
    Harbor,
    Stationobs,
    Stationobs2,
    Stationdaylight,
    Tide,
    ObserveDatum,
    Ocm3,
    Nww3Wrf,
    STwarn,
)
from qiange.filtersets import BaseFilterSet, filter_fields


class GtFilterSet(BaseFilterSet(Gt, localtion_field_name='id', time_field_name='time')):
    class Meta:
        model = Gt
        fields = filter_fields


class AquaCultureFilterSet(BaseFilterSet(Aquaculture, localtion_field_name='id', time_field_name='at')):
    class Meta:
        model = Aquaculture
        fields = filter_fields


class MarineFilterSet(BaseFilterSet(Marine, localtion_field_name='locationname', time_field_name='issuetime')):
    class Meta:
        model = Marine
        fields = filter_fields


class BuoyFilterSet(BaseFilterSet(Buoy, localtion_field_name='stationid', time_field_name='obstime')):
    class Meta:
        model = Buoy
        fields = filter_fields


class FishingFilterSet(BaseFilterSet(Fishing, localtion_field_name='id', time_field_name='at')):
    class Meta:
        model = Fishing
        fields = filter_fields


class HarborFilterSet(BaseFilterSet(Harbor, localtion_field_name='id', time_field_name='at')):
    class Meta:
        model = Harbor
        fields = filter_fields


class StationdaylightFilterSet(BaseFilterSet(Stationdaylight, localtion_field_name='stationid', time_field_name='obstime')):
    class Meta:
        model = Stationdaylight
        fields = filter_fields


class StcforFilterSet(BaseFilterSet(Stationdaylight, localtion_field_name='stationid', time_field_name='obstime')):
    class Meta:
        model = Stationdaylight # Stcfor
        fields = filter_fields


class TideFilterSet(BaseFilterSet(Tide, localtion_field_name='stationid', time_field_name='time')):
    class Meta:
        model = Tide
        fields = filter_fields


class ObserveDatumFilterSet(BaseFilterSet(ObserveDatum, localtion_field_name='stationid', time_field_name='observetime')):
    class Meta:
        model = ObserveDatum
        fields = filter_fields


class Ocm3FilterSet(BaseFilterSet(Ocm3, localtion_field_name='mapper_id', time_field_name='time')):
    depth = MultipleChoiceFilter(choices=[(-1, -1), (-5, -5), (-10, -10)], name='depth', label='depth', help_text=u'深度')

    class Meta:
        model = Ocm3
        fields = filter_fields + ['depth']


class Nww3WrfFilterSet(BaseFilterSet(Nww3Wrf, localtion_field_name='mapper_id', time_field_name='time')):
    class Meta:
        model = Nww3Wrf
        fields = filter_fields


class StationObsFilterSet(BaseFilterSet(Stationobs, localtion_field_name='stationid', time_field_name='obstime')):
    class Meta:
        model = Stationobs
        fields = filter_fields


class StationObs2FilterSet(BaseFilterSet(Stationobs2, localtion_field_name='stationid', time_field_name='obstime')):
    class Meta:
        model = Stationobs2
        fields = filter_fields


class STwarnFilterSet(BaseFilterSet(STwarn, localtion_field_name='view_id', time_field_name='time')):
    class Meta:
        model = STwarn
        fields = filter_fields


class AqfnFilterSet(BaseFilterSet(models.Aqfn, localtion_field_name='area', time_field_name='publish_time')):
    class Meta:
        model = models.Aqfn
        fields = filter_fields


class AqiFilterSet(BaseFilterSet(models.Aqi, localtion_field_name='site_name', time_field_name='publish_time')):
    class Meta:
        model = models.Aqi
        fields = filter_fields

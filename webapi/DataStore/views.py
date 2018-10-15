# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import sys
import urllib
import datetime
import copy
from collections import OrderedDict

from astral import Astral
import requests
from django_filters import rest_framework as filters
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.response import Response
from rest_framework.exceptions import NotFound, ValidationError

from Manage.models import Polygon
from Manage.serializers import SinglePointSerializer
from qiange.serializers import UselessSerializer
from qiange.util import calculate_dis
from qiange.related_fields import _reverse
from qiange.drf_reqparser import RequestParser, str2dt_tztaipei, parse_uri_timestr, tz_taipei

time_start, time_end = 'time_start', 'time_end'


from qiange.views import ListView
from . import models, serializers, filtersets
from Manage.models import (
    Mapper,
    View,
    SinglePoint,
    GRID,
    dataset_qs
)
from Manage.serializers import ViewSerializer


class GtViewSet(ListView):
    queryset = models.Gt.objects.all()
    serializer_class = serializers.GtSerializer
    filter_class = filtersets.GtFilterSet


class AquaCultureViewSet(ListView):
    queryset = models.Aquaculture.objects.all()
    serializer_class = serializers.AquaCultureSerializer
    filter_class = filtersets.AquaCultureFilterSet


class BuoyViewSet(ListView):
    queryset = models.Buoy.objects.all()
    serializer_class = serializers.BuoySerializer
    filter_class = filtersets.BuoyFilterSet


class FishingViewSet(ListView):
    queryset = models.Fishing.objects.all()
    serializer_class = serializers.FishingSerializer
    filter_class = filtersets.FishingFilterSet


class HarborViewSet(ListView):
    queryset = models.Harbor.objects.all()
    serializer_class = serializers.HarborSerializer
    filter_class = filtersets.HarborFilterSet


class MarineViewSet(ListView):
    queryset = models.Marine.objects.all()
    serializer_class = serializers.MarineSerializer
    filter_class = filtersets.MarineFilterSet


class StationDaylightViewSet(ListView):
    queryset = models.Stationdaylight.objects.all()
    serializer_class = serializers.StationDaylightSerializer
    filter_class = filtersets.StationdaylightFilterSet


class STObsViewSet(ListView):
    queryset = models.Stobs.objects.all()
    serializer_class = serializers.STObsSerializer

    class STObsFilter(filters.FilterSet):
        time_start = filters.DateTimeFilter(name='time', lookup_expr='gte', label='time_start', required=True)
        time_end = filters.DateTimeFilter(name='time', lookup_expr='lte', label='time_end', required=True)

        class Meta:
            model = models.Stobs
            fields = ['time_start', 'time_end']

    filter_class = STObsFilter


class TideViewSet(ListView):
    queryset = models.Tide.objects.all()
    serializer_class = serializers.TideSerializer
    filter_class = filtersets.TideFilterSet


class ObserveDatumViewSet(ListView):
    queryset = models.ObserveDatum.objects.all()
    serializer_class = serializers.ObserveDatumSerializer
    filter_class = filtersets.ObserveDatumFilterSet


class Ocm3ViewSet(ListView):
    queryset = models.Ocm3.objects.all()
    serializer_class = serializers.Ocm3Serializer
    filter_class = filtersets.Ocm3FilterSet


class Nww3WrfViewSet(ListView):
    queryset = models.Nww3Wrf.objects.all()
    serializer_class = serializers.Nww3WrfSerializer
    filter_class = filtersets.Nww3WrfFilterSet


class STWarnViewSet(ListView):
    queryset = models.STwarn.objects.all()
    serializer_class = serializers.STwarnSerializer
    filter_class = filtersets.STwarnFilterSet


class StationObsViewSet(ListView):
    queryset = models.Stationobs.objects.all()
    serializer_class = serializers.StationObsSerializer
    filter_class = filtersets.StationObsFilterSet


class StationObs2ViewSet(ListView):
    queryset = models.Stationobs2.objects.all()
    serializer_class = serializers.StationObs2Serializer
    filter_class = filtersets.StationObs2FilterSet


class AqfnViewSet(ListView):
    queryset = models.Aqfn.objects.all()
    serializer_class = serializers.AqfnSerializer
    filter_class = filtersets.AqfnFilterSet


class AqiViewSet(ListView):
    queryset = models.Aqi.objects.all()
    serializer_class = serializers.AqiSerializer
    filter_class = filtersets.AqiFilterSet


class SunriseViewSet(ListView):
    """查詢日出日落時間：
    -選擇性參數： lat、lng、maps_id、time_start、time_end
    """
    from django_filters import rest_framework as filters

    class FilterSet(filters.FilterSet):
        map_ids = filters.NumberFilter(required=False, help_text=u'mapping識別，點須有lat(維度)、lng(經度)屬性。', label='map_ids')
        time_start = filters.DateTimeFilter(required=False, help_text=u'開始時間，ISO格式，預設今日。', label='time_start')
        time_end = filters.DateTimeFilter(required=False, help_text=u'開始時間，ISO格式，預設今日。', label='time_end')
        lat = filters.NumberFilter(required=False, help_text=u'維度。', label='lat')
        lng = filters.NumberFilter(required=False, help_text=u'經度。', label='lng')
        token = filters.CharFilter(required=False, help_text=u'合法的 JWToken。', label='token')

        class Meta:
            model = Mapper
            fields = ['map_ids', 'time_start', 'time_end', 'lat', 'lng', 'token']

        @property
        def qs(self, *args, **kwargs):
            pass

    request_parser = RequestParser()
    request_parser.add_argument(time_start, type=parse_uri_timestr, required=False, default=None)
    request_parser.add_argument(time_end, type=parse_uri_timestr, required=False, default=None)
    request_parser.add_argument('map_ids', type=int, required=False, default=None)
    request_parser.add_argument('lat', type=float, required=False, default=23.5)
    request_parser.add_argument('lng', type=float, required=False, default=120)

    serializer_class = UselessSerializer
    filter_class = FilterSet

    def get_queryset(self):
        return Mapper.objects.all()

    def list(self, request, *args, **kwargs):
        incoming = self.request_parser.parse_args(request.query_params)
        map_ids = incoming['map_ids']
        if map_ids is not None:
            try:
                mapper = Mapper.objects.select_related('view').get(id=map_ids)
            except ObjectDoesNotExist:
                raise ValidationError({'map_ids': [u"The mapper '%s' does not exist." % map_ids]})
            lat = mapper.lat or mapper.view.lat
            lng = mapper.lng or mapper.view.lng
        else:
            lat, lng = incoming['lat'], incoming['lng']
        ViewSerializer.intercept_validate_lat_lng(lat, lng, allow_null=False)

        _tz_info = tz_taipei
        _time_start = incoming[time_start]
        _time_end = incoming[time_end]
        if _time_start:
            _tz_info = _time_start.tzinfo or _tz_info
        if _time_end:
            _tz_info = _time_end.tzinfo or _tz_info
        if _time_start is None:
            _time_start = datetime.datetime.now(tz=_tz_info)
        if _time_end is None:
            _time_end = datetime.datetime.now(tz=_tz_info)
        _time_start = _time_start.replace(tzinfo=_tz_info)
        _time_end = _time_end.replace(tzinfo=_tz_info)
        _astral = Astral()
        _count = 0
        data = []
        if _time_end < _time_start:
            raise ValidationError({
                time_start: ["%s '%s' > %s '%s'" % (time_start, _time_start.isoformat(), time_end, _time_end.isoformat())],
                time_end: ["%s '%s' > %s '%s'" % (time_start, _time_start.isoformat(), time_end, _time_end.isoformat())],
            })

        while True:
            _iter_dt = _time_start + datetime.timedelta(days=_count)
            if _iter_dt > _time_end:
                break
            _count += 1
            try:
                date = _iter_dt.date()
                sunrise = _astral.sunrise_utc(date, lat, lng).astimezone(_tz_info)
                sunset = _astral.sunset_utc(date, lat, lng).astimezone(_tz_info)
                detail = {
                    'date': date,
                    'sunrise': sunrise,
                    'sunset': sunset,
                    'lat': lat,
                    'lng': lng,
                    'utcoffset': _tz_info.utcoffset(_time_start),
                }
            except Exception as e:
                raise ValidationError({'lat': [str(e)], 'lng': [str(e)]})
            data.append(detail)
        return Response(data)


class AdvancedQueryViewSet(ListView):
    """進階查詢
    - 必要Path參數：view_id 、dataset_name
    - 選擇性參數：選擇性查詢參數與基礎查詢API同
    """
    from django_filters import rest_framework as filters

    class FilterSet(filters.FilterSet):
        # dataset_name = filters.CharFilter(required=True, help_text=u'要查詢的資料集名稱。')
        # view_id = filters.BaseInFilter(required=True, help_text=u'顯示點ID。')
        time_start = filters.DateTimeFilter(help_text=u'資料開始時間，ISO格式。')
        time_end = filters.DateTimeFilter(help_text=u'資料結束時間，ISO格式。')
        token = filters.CharFilter(help_text=u'合法的 JWToken。')
        depth = filters.CharFilter(help_text=u'海洋資料的深度。')
        ordering = filters.CharFilter(help_text=u'排序的欄位和方法，與基礎查詢API同')

    request_parser = RequestParser()
    # request_parser.add_argument('dataset_name', type=unicode, required=True, default=None)
    # request_parser.add_argument('view_id', type=int, required=True, default=None)
    request_parser.add_argument(time_start, type=str2dt_tztaipei, required=False, default=None)
    request_parser.add_argument(time_end, type=str2dt_tztaipei, required=False, default=None)

    serializer_class = UselessSerializer
    filter_class = FilterSet

    def get_queryset(self):
        return Mapper.objects.all()

    def get_data_source_endpoint(self, request, table_name):
        end_point = _reverse(table_name.lower() + '-list', request=request)
        return end_point

    def list(self, request, view_id, dataset_name, *args, **kwargs):
        incoming = self.request_parser.parse_args(request.query_params)
        mappers = Mapper.objects.select_related('dataset', 'singlepoint', 'datapoint_strategy')\
            .filter(view=int(view_id), dataset__dataset_name=dataset_name)
        if not mappers.exists():
            raise ValidationError({'detail': [u"The view '%s' was not associated with the dataset '%s' or dataset_name is invalid." % (view_id, dataset_name)],})

        metadata = {
            'dataset': _reverse(viewname='dataset-detail', args=[dataset_name], request=request),
            'view': _reverse(viewname='view-detail', args=[view_id], request=request),
        }
        if incoming.get(time_start):
            metadata.update({time_start: incoming[time_start]})
        if incoming.get(time_end):
            metadata.update({time_end: incoming[time_end]})

        dataset_category = mappers[0].dataset.category
        ret = []
        sub_query_params = []
        urlencode = request.GET.urlencode()
        if urlencode:
            sub_query_params.append(urlencode)
        for mapper in mappers:
            query_params = copy.deepcopy(sub_query_params)
            strategy_name = mapper.datapoint_strategy.strategy_name
            detail = OrderedDict([
                ('mapper', _reverse(viewname='mapper-detail', args=[mapper.id], request=request)),
                ('strategy_name', mapper.datapoint_strategy.strategy_name),
            ])
            if dataset_category == GRID:
                key_value = 'map_ids=%s' % mapper.id
                if strategy_name == Polygon.strategy_name:
                    detail['latlng'] = mapper.latlng
                else:
                    detail['lat'] = mapper.lat
                    detail['lng'] = mapper.lng
            else: # dataset_category == SINGLE:
                key_value = 'map_ids=%s' % urllib.quote(mapper.singlepoint.point_id.encode('utf8'))
                detail['point_id'] = mapper.singlepoint.point_id
            query_params.append(key_value)
            query_params_str = '&'.join(query_params)
            url = self.get_data_source_endpoint(request, dataset_name) + '?' + query_params_str
            url = url.replace('127.0.0.1', 'localhost')
            try:
                res = requests.get(
                    url,
                    cookies={'sessionid': request.COOKIES['sessionid']} if 'sessionid' in request.COOKIES else {},
                    headers={'Authorization': request.META.get('Authorization')},
                )
            except Exception:
                raise ValidationError({"detail": u"GET '%s' Fail." % url})
            try:
                _json = res.json()
            except Exception:
                raise ValidationError({"detail": res.text})
            if res.status_code != 200:
                raise ValidationError(_json)
            detail['dts'] = _json
            ret.append(detail)

        return Response({
            'metadata': metadata,
            'data': ret
        })


class ClosestSinglePointView(ListView):
    """從單點資料集中找出最近資料點
    - 必要Path參數：dataset_name
    - 選擇性參數：lat、lng、view_id
    """

    class FilterSet(filters.FilterSet):
        # dataset_name = filters.CharFilter(required=True, help_text=u'要查詢的資料集名稱。')
        view_id = filters.CharFilter(help_text=u'顯示點ID，顯示點必須具有lat/lng屬性。')
        lat = filters.NumberFilter(help_text=u'緯度。')
        lng = filters.NumberFilter(help_text=u'經度。')
        token = filters.NumberFilter(help_text=u'合法的JWToken')

        class Meta:
            model = SinglePoint
            fields = ['lat', 'lng', 'view_id', 'token']

    request_parser = RequestParser()
    # request_parser.add_argument('dataset_name', type=unicode, required=True, default=None)
    request_parser.add_argument('view_id', type=int, required=False, default=None)
    request_parser.add_argument('lat', type=float, required=False, default=23.5)
    request_parser.add_argument('lng', type=float, required=False, default=120)

    serializer_class = UselessSerializer
    filter_class = FilterSet

    def get_queryset(self):
        return SinglePoint.objects.all()

    def list(self, request, dataset_name, *args, **kwargs):
        incoming = self.request_parser.parse_args(request.query_params)
        try:
            dataset = dataset_qs.get(dataset_name=dataset_name)
        except ObjectDoesNotExist:
            raise ValidationError({'dataset_name': [u"資料集 '%s' 不存在." % dataset_name]})

        view_id = incoming['view_id']
        if view_id is not None:
            try:
                view = View.objects.get(id=view_id)
                lat, lng = view.lat, view.lng
            except ObjectDoesNotExist:
                raise ValidationError({'view_id': [u"顯示點 '%s' 不存在." % view_id]})
            if lat is None:
                raise ValidationError({'view': ["The attribute 'lat' of view '%s' could not be empty value." % view_id]})
            if lng is None:
                raise ValidationError({'view': ["The attribute 'lng' of view '%s' could not be empty value." % view_id]})
        else:
            lat, lng = incoming['lat'], incoming['lng']
            try:
                ViewSerializer.validate_lat(lat, allow_null=False)
            except ValidationError as e:
                raise ValidationError({'lat': e.detail})
            try:
                ViewSerializer.validate_lng(lng, allow_null=False)
            except ValidationError as e:
                raise ValidationError({'lng': e.detail})

        dataset_category = dataset.category
        if dataset_category != 'Single':
            raise ValidationError({'dataset': [u"無法對非單點資料集取最近點."]})

        singlepoints = dataset.singlepoint_set.all()
        if singlepoints[0].lat is None and singlepoints[0].lng is None:
            sql = """
                        SELECT *, id from info_single_point
                        WHERE CONTAINS(`mpoly`, Point({lng}, {lat}));
                        """.format(lng=lng, lat=lat)
            datapoints = [point for point in SinglePoint.objects.raw(sql)]
            if not datapoints:
                raise NotFound({'detail': "The Point(%s, %s) was not completely contained by any MultiPolygon" % (lng, lat)})
            datapoint = datapoints[0]
        else:
            datapoint, distance, dis2 = None, sys.maxint, sys.maxint
            for p1 in dataset.singlepoint_set.all():
                if p1.lat is not None and p1.lng is not None:
                    dis2 = calculate_dis(lng, lat, p1.lng, p1.lat)
                if dis2 < distance:
                    datapoint, distance = p1, dis2
            if not datapoint:
                raise NotFound({"detail": "NotFound any datapoint in dataset '%s'" % dataset.dataset_name})

        res = Response(SinglePointSerializer(datapoint, context=self.get_serializer_context()).data)
        return res

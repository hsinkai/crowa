# -*- coding: utf-8 -*-

from rest_framework import viewsets, permissions, authentication
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from Manage.models import (
    SinglePoint,
    Dataset,
    Application,
    View,
    Mapper,
    Species,
    City,
    Town,
)
from Manage.serializers import (
    SinglePointSerializer,
    DataSetSerializer,
    ApplicationSerializer,
    ViewSerializer,
    MapperSerializer,
    SpeciesSerializer,
    CitySerializer,
    TownSerializer,
)
import qiange
from qiange.authentications import JWTokenAuthentication
from qiange.related_fields import application_related_context, dataset_related_context
from .filtersets import ViewFilterSet


class UpdateMixin(object):
    """
    Update a model instance.
    """
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()


class CustModelViewSet(qiange.ListLog,
                       qiange.RetrieveLog,
                       qiange.WriteLog,
                       qiange.LogFacade,
                       viewsets.mixins.ListModelMixin,
                       viewsets.mixins.RetrieveModelMixin,
                       viewsets.mixins.CreateModelMixin,
                       viewsets.mixins.DestroyModelMixin,
                       UpdateMixin,
                       viewsets.GenericViewSet):

    authentication_classes = (JWTokenAuthentication, authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions, )


class SinglePointViewSet(CustModelViewSet):
    """
    單點資料點：
    每一個點實例具有 point_id 以及其所屬的 dataset；lat/lon/mpoly 用來取最近點。
    """
    queryset = SinglePoint.objects.all()
    serializer_class = SinglePointSerializer
    filter_fields = ('point_id', 'dataset', 'dataset__dataset_name')
    pagination_class = LimitOffsetPagination
    PAGE_SIZE = 10


class DataSetViewSet(CustModelViewSet):
    """
    資料集：
    dataset_name (資料集名稱)、
    datapoint_strategies (資料集的取點方法)、
    singlepoints (單點資料點清單)、
    mappers (顯示點&資料點Mapping)、
    datastore (資料集存取點)。
    """
    queryset = Dataset.objects.all()
    serializer_class = DataSetSerializer
    lookup_field = dataset_related_context()['lookup_field']
    filter_fields = ('dataset_name', 'id')


class ApplicationViewSet(CustModelViewSet):
    """
    應用:
    每一個 app 聚合了多個資料集，為該應用所需要的資料源。
    """
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer
    lookup_field = application_related_context()['lookup_field']
    filter_fields = ('name', 'service', 'service__cname')


class CityViewSet(CustModelViewSet):
    """縣市清單"""
    queryset = City.objects.all()
    serializer_class = CitySerializer
    filter_fields = ('code', 'cname', )


class TownViewSet(CustModelViewSet):
    """鄉鎮清單"""

    queryset = Town.objects.all()
    serializer_class = TownSerializer
    filter_fields = ('code', 'city_cname', 'cname', 'name', )
    pagination_class = LimitOffsetPagination
    PAGE_SIZE = 10


class ViewViewSet(CustModelViewSet):
    """顯示點：
    app (* 顯示點所屬的 App URL)、
    label ( * 顯示點標籤)、
    name (顯示點名稱)、
    category (顯示點類別)、
    location_name (顯示點所在的位置名稱)、
    city (顯示點所在縣市)、
    town (顯示點所在鄉鎮)。
    lat (取資料的緯度)、
    lng (取資料的經度)、
    latlng (取資料的多邊形經緯度)、
    """
    queryset = View.objects.select_related('city', 'town').all()
    serializer_class = ViewSerializer
    filter_class = ViewFilterSet
    pagination_class = LimitOffsetPagination
    PAGE_SIZE = 10


class MapperViewSet(CustModelViewSet):
    """顯示點&資料點Mapping：
    view (顯示點實例)、
    dataset (資料集 URL)
    singlepoint (單點資料點實例)、
    datapoint_strategy (取點方法)。
    lat (取資料的緯度)、
    lng (取資料的經度)、
    latlng (取資料的多邊形經緯度)、
    """
    queryset = Mapper.objects.select_related('view', 'singlepoint', 'datapoint_strategy').all()
    serializer_class = MapperSerializer
    filter_fields = ('view', 'app', 'dataset', 'singlepoint', 'datapoint_strategy')
    pagination_class = LimitOffsetPagination
    PAGE_SIZE = 10


class SpeciesViewSet(CustModelViewSet):
    """養殖物種 & Default Setting：
        mmin_acc_temp: 最小最適合氣溫
        mmax_acc_temp: 最大最適合氣溫
        min_acc_temp: 最小適合氣溫
        max_acc_temp: 最大適合氣溫
        min_pressure: 最小適合氣壓差
        max_1h_rain: 最大時雨量
        max_6h_rain: 最大6小時累積雨量
    """
    queryset = Species.objects.all()
    serializer_class = SpeciesSerializer
    filter_fields = ('id', 'species_id', 'species_name')

    def list(self, request, *args, **kwargs):
        raise RuntimeError('dsdfadd')


# -*- coding: utf-8 -*-

from django_filters import rest_framework as filters

from qiange.filtersets import GenericFilterSet
from .models import View, Application, City, Town


class ViewFilterSet(GenericFilterSet, filters.FilterSet):
    app = filters.ModelChoiceFilter(help_text=u'應用 ID 做精確查詢.', queryset=Application.objects.all(), label='app')
    app__name = filters.CharFilter(help_text=u'應用名稱 做精確查詢.', name='app__name', label='app__name')
    label = filters.CharFilter(help_text=u'label 做精確查詢.', name='label', label='label')
    category = filters.CharFilter(help_text=u'category 做包含查詢.', name='category', lookup_expr='icontains', label='category')
    name = filters.CharFilter(help_text=u'name 做包含查詢.', name='name', lookup_expr='icontains', label='name')
    location_name = filters.CharFilter(help_text=u'location_name 做包含查詢.', name='location_name', lookup_expr='icontains', label='location_name')
    city = filters.ModelChoiceFilter(help_text=u'縣市 ID 做精確查詢.', queryset=City.objects.all(), label='city')
    city__cname = filters.CharFilter(help_text=u'縣市名稱做包含查詢.', name='city__cname', lookup_expr='icontains', label='city__cname')
    town = filters.ModelChoiceFilter(help_text=u'鄉鎮 ID 做精確查詢.', queryset=Town.objects.all(), label='town')
    town__city_cname = filters.ChoiceFilter(help_text=u'鄉鎮內的縣市名稱 做包含查詢.', choices=[(o.cname, o) for o in City.objects.all()], name='town__city_cname', lookup_expr='icontains', label='town__city_cname')
    town__cname = filters.CharFilter(help_text=u'鄉鎮名稱 做包含查詢.', name='town__cname', lookup_expr='icontains', label='town__cname')
    columns = [(f.name, f.name) for f in View._meta.fields] + [('warnings', 'warnings')]
    fields = filters.MultipleChoiceFilter(required=False, help_text=u'指定取值欄位.', label='fields', choices=columns, )

    class Meta:
        model = View
        fields = [
            'app', 'app__name', 'label', 'category', 'name', 'location_name',
            'city', 'city__cname',
            'town', 'town__city_cname', 'town__cname',
            'fields',
        ]

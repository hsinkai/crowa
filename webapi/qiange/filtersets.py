# -*- coding: utf-8 -*-

from django.db.models import Max, Model
from django import forms
from django.utils import six
from django_filters import rest_framework as filters, utils
from rest_framework.exceptions import ValidationError

from qiange.keys import QUERY_DICT
from qiange.drf_reqparser import str2dt_tztaipei


filter_fields = ['map_ids', 'time_start', 'time_end', 'fields', 'ordering', 'token']


class GenericFilterSet(object):
    @property
    def qs(self, *args, **kwargs):
        try:
            return self._run_qs()
        except forms.ValidationError as e:
            raise ValidationError(utils.raw_validation(e))

    def _run_qs(self):
        ########################
        query_dict = {}
        setattr(self, QUERY_DICT, query_dict)
        ########################

        if not hasattr(self, '_qs'):
            if not self.is_bound:
                self._qs = self.queryset.all()
                return self._qs

            if not self.form.is_valid():
                pass
            # start with all the results and filter from there
            qs = self.queryset.all()
            for name, filter_ in six.iteritems(self.filters):
                if name in ('fields', 'ticket', 'token', 'apikey', 'withmeta'):
                    continue
                value = self.form.cleaned_data.get(name)

                if name == 'point_ids' and value is None and self.request.query_params.get('point_ids', '').strip():
                    value = self.request.query_params.get('point_ids').split(',')

                if value is None and name in ('time_start', 'time_end'):
                    time_str = self.request.query_params.get(name)
                    if time_str:
                        try:
                            value = str2dt_tztaipei(time_str)
                            value = value.replace(tzinfo=None)
                        except ValidationError as e:
                            raise ValidationError({name: e.detail})
                        except Exception as e:
                            raise ValidationError({name: str(e)})
                    else:
                        value = qs.aggregate(Max(filter_.name)).values()[0]
                    qs = filter_.filter(qs, value)
                elif value is not None or (isinstance(value, basestring) and value.strip() != ''):  # valid & clean data
                    qs = filter_.filter(qs, value)
                ########################
                if value == 0 or value:
                    query_dict[name] = value
                ########################

            self._qs = qs
        return self._qs


def DatetimeMixin(time_field_name='time', model=None):
    if model:
        assert hasattr(model, time_field_name), "Model '%s' has not attribute '%s'" % (model, time_field_name)

    class _DatetimeMixin(object):
        time_start = filters.DateTimeFilter(name=time_field_name, lookup_expr='gte', label='time_start',
                            help_text=u"資料開始時間，ISO格式， 針對 %s 欄位，預設值取 MAX(%s)。" % (time_field_name, time_field_name))
        time_end = filters.DateTimeFilter(name=time_field_name, lookup_expr='lte', label='time_end',
                            help_text=u"資料結束時間，ISO格式，針對 %s 欄位，預設值取 MAX(%s)。" % (time_field_name, time_field_name))
    return _DatetimeMixin


def LocationMixin(localtion_field_name='id', model=None):
    if model:
        assert hasattr(model, localtion_field_name), "Model '%s' has not attribute '%s'" % (model, localtion_field_name)

    class _DatetimeMixin(object):
        if model:
            LOCATION_FIELDS = [(o[localtion_field_name], o[localtion_field_name]) for o in
                               model.objects.values(localtion_field_name).distinct()]
            map_ids = filters.MultipleChoiceFilter(choices=LOCATION_FIELDS, name=localtion_field_name, label='map_ids',
                                                   help_text=u"點識別，針對 %s 欄位，預設取全部。" % localtion_field_name)
        else:
            map_ids = filters.CharFilter(name=localtion_field_name, label='map_ids',
                                         help_text=u"點識別，針對 %s 欄位，預設取全部。" % localtion_field_name)
    return _DatetimeMixin


def BaseFilterSet(model, localtion_field_name='id', time_field_name='time'):
    assert issubclass(model, Model), "The argument model must be `django.db.models.Model`, but '%s'." % model
    assert hasattr(model, localtion_field_name), "Model '%s' has not attribute '%s'" % (model, localtion_field_name)
    assert hasattr(model, time_field_name), "Model '%s' has not attribute '%s'" % (model, time_field_name)

    # print [f.name for f in model._meta.fields]

    class _BaseFilterSet(GenericFilterSet, filters.FilterSet):
        LOCATION_FIELDS = [(o[localtion_field_name], o[localtion_field_name]) for o in model.objects.values(localtion_field_name).distinct()]
        FIELDS = [(f.name, f.name) for f in model._meta.fields]
        time_start = filters.DateTimeFilter(name=time_field_name, lookup_expr='gte', label='time_start',
                    help_text=u"資料開始時間，ISO格式， 針對 %s 欄位，預設值取 MAX(%s)。" % (time_field_name, time_field_name))
        time_end = filters.DateTimeFilter(name=time_field_name, lookup_expr='lte', label='time_end',
                    help_text=u"資料結束時間，ISO格式，針對 %s 欄位，預設值取 MAX(%s)。" % (time_field_name, time_field_name))
        map_ids = filters.MultipleChoiceFilter(choices=LOCATION_FIELDS, name=localtion_field_name, label='map_ids',
                                               help_text=u"mapping 識別，針對 %s 欄位，預設取全部。" % localtion_field_name)
        fields = filters.MultipleChoiceFilter(choices=FIELDS, label='fields', required=False,
                    help_text=u"選取的欄位: %s" % ','.join(f[0] for f in FIELDS))
        ordering = filters.OrderingFilter(fields=[time_field_name, localtion_field_name], label='ordering',
                    help_text=u"選擇排序欄位和方法：%s" % ' | '.join((time_field_name, localtion_field_name, '-' + time_field_name, '-' + localtion_field_name)))
        token = filters.CharFilter(label='token', help_text=u"有效的JWToken")

        class Meta:
            model = None
            fields = filter_fields

    return _BaseFilterSet


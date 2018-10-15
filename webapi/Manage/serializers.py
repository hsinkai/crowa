# -*- coding: utf-8 -*-
import re

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from Manage.models import DatapointStrategy, DatasetDatapointStrategy, Application, Dataset, ApplicationDataset, Service, Species
from Manage.models import PointID, ClosestPair, ApproachPoint, Polygon, GRID, SINGLE
from Manage.models import Town, City, View, Mapper, SinglePoint
from qiange.dynamic_fields_mixin import DynamicFieldsMixin
from qiange.util import http_intercept_get, InterceptedException
from qiange.util import instance_from_url, http_forward_get
from qiange.related_fields import _reverse
from qiange.related_fields import application_related_context, dataset_related_context
from qiange.related_fields import make_hyperlinked_related_field, make_hyperlinked_identity_field
from url_meta import LatLngURLCreator, PolygenURLCreator
from qiange import err_logger


class SinglePointSerializer(serializers.HyperlinkedModelSerializer):
    dataset = make_hyperlinked_related_field(**dataset_related_context())

    class Meta:
        model = SinglePoint
        fields = ['url', 'id', 'point_id', 'dataset', 'name', 'lat', 'lng', ]


class DatapointStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatapointStrategy
        fields = '__all__'


class DatapointStrategySerializer(serializers.ModelSerializer):
    class Meta:
        model = DatapointStrategy
        fields = '__all__'


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'


class DataSetSerializer(serializers.HyperlinkedModelSerializer):
    SINGLE_STRATEGIES = set([PointID, ClosestPair])
    GRID_STRATEGIES = set([ApproachPoint, Polygon])

    url = make_hyperlinked_identity_field(**dataset_related_context(with_queryset=False))
    is_api_available = serializers.ChoiceField(choices=(0, 1), )
    category = serializers.ChoiceField(choices=(SINGLE, GRID), )
    datapoint_strategies = serializers.SlugRelatedField(queryset=DatapointStrategy.objects.all(), slug_field='strategy_name', many=True)

    class Meta:
        depth = 1
        model = Dataset
        fields = ('url', 'id', 'dataset_name', 'category', 'description', 'is_api_available', 'datapoint_strategies')

    def to_representation(self, instance):
        data = super(type(self), self).to_representation(instance)
        data['singlepoints'] = _reverse('singlepoint-list', request=self.context['request']) + '?dataset=%d' % instance.id
        data['mappers'] = _reverse('mapper-list', request=self.context['request']) + '?dataset=%d' % instance.id
        try:
            data['datastore'] = _reverse(instance.dataset_name.lower() + '-list', request=self.context['request'])
        except Exception:
            data['datastore'] = None
        return data

    def create(self, validated_data):
        datapoint_strategies = self.__get_datapoint_strategies(validated_data)
        dataset = Dataset.objects.create(dataset_name=validated_data['dataset_name'],
                                         category=validated_data['category'],
                                         is_api_available=validated_data['is_api_available'],
                                         description=validated_data['description'])
        for datapoint_strategy in datapoint_strategies:
            dataset.datasetdatapointstrategy_set.add(
                DatasetDatapointStrategy.objects.create(dataset=dataset, datapoint_strategy=datapoint_strategy)
            )
        return dataset

    def update(self, instance, validated_data):
        datapoint_strategies = set(validated_data['datapoint_strategies'])
        self.__check_datapoint_strategies(datapoint_strategies, instance.category)

        instance.dataset_name = validated_data.get('dataset_name', instance.dataset_name)
        instance.category = validated_data.get('category', instance.category)
        instance.is_api_available = validated_data.get('is_api_available', instance.is_api_available)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        members = []
        old_datapoint_strategies = set(member.datapoint_strategy for member in instance.datasetdatapointstrategy_set.all())
        for datapoint_strategy in datapoint_strategies - old_datapoint_strategies:
            member = DatasetDatapointStrategy.objects.create(datapoint_strategy=datapoint_strategy, dataset=instance)
            members.append(member)
        for datapoint_strategy in old_datapoint_strategies - datapoint_strategies:
            for member in DatasetDatapointStrategy.objects.filter(datapoint_strategy=datapoint_strategy, dataset=instance):
                member.delete()
        instance.datasetdatapointstrategy_set.set(members)
        return instance

    def __get_datapoint_strategies(self, validated_data):
        category = validated_data['category']
        datapoint_strategies = set(validated_data['datapoint_strategies'])
        if not datapoint_strategies:
            datapoint_strategies = self.GRID_STRATEGIES if category == GRID else self.SINGLE_STRATEGIES
        self.__check_datapoint_strategies(datapoint_strategies, category)
        return datapoint_strategies

    def __check_datapoint_strategies(self, datapoint_strategies, category):
        if category == GRID:
            if not datapoint_strategies <= self.GRID_STRATEGIES:
                vas = ','.join(o.strategy_name for o in datapoint_strategies - self.GRID_STRATEGIES)
                raise ValidationError({'datapoint_strategies': "Invalid '%s' strategies for dataset type '%s'" % (vas, category)})
        else:
            if not datapoint_strategies <= self.SINGLE_STRATEGIES:
                vas = ','.join(o.strategy_name for o in datapoint_strategies - self.SINGLE_STRATEGIES)
                raise ValidationError({'datapoint_strategies': "Invalid '%s' strategies for dataset type '%s'" % (vas, category)})
        return datapoint_strategies


class ApplicationSerializer(serializers.ModelSerializer):
    url = make_hyperlinked_identity_field(**application_related_context(with_queryset=False))
    datasets = make_hyperlinked_related_field(allow_empty=True, many=True, **dataset_related_context())
    service = serializers.SlugRelatedField(queryset=Service.objects.all(), slug_field='cname')

    class Meta:
        model = Application
        fields = ['url', 'id', 'name', 'service', 'description',  'datasets']

    def create(self, validated_data):
        app = Application.objects.create(name=validated_data['name'],
                                         service=validated_data['service'],
                                         description=validated_data['description'])
        for dataset in validated_data['datasets']:
            app.applicationdataset_set.add(ApplicationDataset.objects.create(app=app, dataset=dataset))
        return app

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.service = validated_data.get('service', instance.service)
        # import pdb;pdb.set_trace()
        instance.description = validated_data.get('description', instance.description)
        members = []
        old_datasets = set(member.dataset for member in instance.applicationdataset_set.all())
        datasets = set(validated_data['datasets'])
        for dataset in datasets - old_datasets:
            members.append(ApplicationDataset.objects.create(app=instance, dataset=dataset))
        for dataset in old_datasets - datasets:
            Mapper.objects.filter(app=instance, dataset=dataset).delete()
            for it in ApplicationDataset.objects.filter(app=instance, dataset=dataset):
                it.delete()
        instance.applicationdataset_set.set(members)
        instance.save()
        return instance

    # def to_representation(self, instance):
    #     data = super(ApplicationSerializer, self).to_representation(instance)
    #     data['service'] = ServiceSerializer(instance.service).data if instance.service else None
    #     return data


class ApplicationDatasetSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):

    class Meta:
        model = ApplicationDataset
        fields = '__all__'


class ViewListSerializer(serializers.ListSerializer):
    def update(self, instance, validated_data):
        exist_view = {book.id: book for book in instance}
        input_view = {item['id']: item for item in validated_data}

        ret = []
        for view_id, data in input_view.items():
            view = exist_view.get(view_id, None)
            if view is None:
                ret.append(self.child.create(data))
            else:
                ret.append(self.child.update(view, data))

        for view_id, view in exist_view.items():
            if view_id not in input_view:
                view.delete()
        return ret

    def create(self, validated_data):
        views = [View(**item) for item in validated_data]
        return View.objects.bulk_create(views)


class TownSerializer(serializers.ModelSerializer):
    city_cname = serializers.ChoiceField(help_text=u'縣市名稱', choices=[(o.cname, o) for o in City.objects.all()])

    class Meta:
        model = Town
        fields = '__all__'


class CitySerializer(serializers.ModelSerializer):
    class Meta:
        model = City
        fields = '__all__'


class ViewSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    app = serializers.PrimaryKeyRelatedField(label='app', help_text=u'* 顯示點所屬的 App ID（必填）。', queryset=Application.objects.all(), required=True)
    name = serializers.CharField(label='name', max_length=255, required=True, allow_blank=False, allow_null=False, help_text=u'* 顯示點名稱（必填）。')
    label = serializers.CharField(label='label', max_length=255, required=True, allow_blank=False, allow_null=False, help_text=u'* 顯示點標籤（必填），可用於綁定資料點。')
    category = serializers.CharField(label='category', max_length=255, required=False, allow_null=True, help_text=u'顯示點類別，如：高中/大學/漁業養殖')
    location_name = serializers.CharField(label='location_name',  max_length=255, required=False, allow_null=True, help_text=u'顯示點所在的位置名稱')
    lat = serializers.DecimalField(label='lat', help_text=u'取資料的緯度，預設值 $town.lat。', allow_null=True, decimal_places=8, max_digits=12, required=False)
    lng = serializers.DecimalField(label='lng', help_text=u'取資料的經度，預設值 $town.lng。', allow_null=True, decimal_places=8, max_digits=12, required=False)
    latlng = serializers.CharField(label='latlng', help_text=u'取資料的多邊形經緯度；如："23,120; 23,120.5; 22.6,120; 23,120;"', required=False, allow_null=True)
    city = serializers.SlugRelatedField(label='city', help_text=u'顯示點所在縣市代碼', queryset=City.objects.all(), slug_field='code', allow_null=True, allow_empty=True, required=False)
    town = serializers.SlugRelatedField(label='town', help_text=u'顯示點所在鄉鎮代碼', queryset=Town.objects.all(), slug_field='code', allow_null=True, allow_empty=True, required=False)

    class Meta:
        model = View
        fields = ['id', 'app', 'label', 'name', 'category', 'location_name', 'city', 'town', 'lat', 'lng', 'latlng', ]
        list_serializer_class = ViewListSerializer

    def to_representation(self, instance):
        data = super(ViewSerializer, self).to_representation(instance)
        data['city'] = CitySerializer(instance.city).data if instance.city else None
        data['town'] = TownSerializer(instance.town).data if instance.town else None
        params = self.context['request'].query_params
        if params.has_key('fields') and 'warnings' not in params.getlist('fields'):
            return data

        dataset_set_1 = set(instance.app.datasets.all())
        dataset_set_2 = set(vp.dataset for vp in instance.mappers.all())
        warnings = []
        for t in dataset_set_1 - dataset_set_2:
            warning = u"顯示點尚未綁定資料集 '%s' 中的任何資料點." % t.dataset_name
            warnings.append(warning)
        data['warnings'] = warnings
        return data

    def to_internal_value(self, data):
        data = super(ViewSerializer, self).to_internal_value(data)
        town = data.get('town')
        if 'town' not in data:
            data['town'] = None
        if town:
            if data.get('lat') is None:
                data['lat'] = town.lat
            if data.get('lng') is None:
                data['lng'] = town.lng
        return data

    @classmethod
    def validate_lat(self, lat, allow_null=True):
        if allow_null and lat is None:
            return None
        if not allow_null and lat is None:
            raise ValidationError(["This field may not be empty value."])

        lat = float(lat) if isinstance(lat, basestring) else lat
        if not -90 <= lat <= 90:
            raise ValidationError(["Invalid value %s, it must be in range(-90, 90)." % lat])
        return lat

    @classmethod
    def validate_lng(self, lng, allow_null=True):
        if allow_null and lng is None:
            return None
        if not allow_null and lng is None:
            raise ValidationError(["This field may not be empty value.."])

        lng = float(lng) if isinstance(lng, basestring) else lng
        if not -180 <= lng <= 180:
            raise ValidationError(["Invalid value '%s', it must be in range(-180, 180)." % lng])
        return lng

    @classmethod
    def validate_latlng(self, latlng, allow_null=True):
        if allow_null and latlng is None:
            return None
        if not allow_null and latlng is None:
            raise ValidationError(["This field may not be empty value."])

        if len(latlng) > 65535:
            raise ValidationError(["Ensure this field has no more than 65535 characters."])
        _latlng = latlng if latlng.endswith(';') else latlng + ';'
        raw = r'([-+]??\d+[.]??\d*?,[-+]??\d+[.]??\d*?;\s*?){4,5000}'
        if not re.compile(raw).match(_latlng):
            raise ValidationError(["Invalid pattern, it must match '%s'." % raw])
        latlngs = re.compile(r';\s*').split(_latlng)
        if latlngs[0] != latlngs[-2]:
            raise ValidationError(["Invalid value, the path of points must be a cycle."])
        for lat, lng in (_.split(',') for _ in latlngs if _):
            try:
               self.validate_lat(lat)
               self.validate_lng(lng)
            except ValidationError as e:
                raise ValidationError(e.detail)

        return latlng

    @classmethod
    def intercept_validate_lat_lng(self, lat, lng, allow_null=False):
        try:
            ViewSerializer.validate_lat(lat, allow_null=allow_null)
        except ValidationError as e:
            raise ValidationError({'lat': e.detail})
        try:
            ViewSerializer.validate_lng(lng, allow_null=allow_null)
        except ValidationError as e:
            raise ValidationError({'lng': e.detail})


class MapperSerializer(DynamicFieldsMixin, serializers.HyperlinkedModelSerializer):
    id = serializers.IntegerField(read_only=True)
    view = serializers.PrimaryKeyRelatedField(label='view', help_text=u'* 顯示點 ID（必填）。', queryset=View.objects.all())
    # view = make_hyperlinked_related_field(label='view', help_text=u'* 顯示點URL（必填）。', queryset=View.objects.all(), view_name='view-detail')
    dataset = make_hyperlinked_related_field(label='dataset', help_text=u'* 資料集URL（必填）。', **dataset_related_context())
    singlepoint = serializers.CharField(required=False, read_only=True, allow_null=True)
    point_id = serializers.CharField(label='point_id', help_text=u'單點資料點 ID（選擇）， 用來和 $view.name 做綁定。', required=False, allow_blank=True, write_only=True)
    lat = serializers.FloatField(label='lat', help_text=u'緯度（選擇），預設取 $view.lat。', required=False, allow_null=True)
    lng = serializers.FloatField(label='lng', help_text=u'經度（選擇），預設取 $view.lng。', required=False, allow_null=True)
    latlng = serializers.CharField(label='latlng', help_text=u'多邊形經緯度（選擇），預設取 $view.latlng，如："23,120; 23,120.5; 22.6,120; 23,120;"。', required=False, allow_null=True, allow_blank=True)
    datapoint_strategy = serializers.SlugRelatedField(label='datapoint_strategy', help_text=u"綁定方法（選擇），單點資料預設取 'PointID'，格點資料依參數而定。", allow_null=True,
                                                      slug_field='strategy_name', queryset=DatapointStrategy.objects.all(), required=False,)

    class Meta:
        model = Mapper
        fields = ['url', 'id', 'view', 'dataset', 'datapoint_strategy', 'point_id', 'singlepoint', 'lat', 'lng', 'latlng', ]

    def to_representation(self, instance):
        data = super(MapperSerializer, self).to_representation(instance)
        data['view'] = ViewSerializer(instance.view, context=self.context).data
        data['singlepoint'] = SinglePointSerializer(instance.singlepoint, context=self.context).data if instance.singlepoint_id else None
        return data

    def validate(self, attrs):
        view = attrs['view']
        dataset = attrs['dataset']
        point_id = attrs.pop('point_id', None)
        attrs['app'] = app = view.app
        lat = attrs.get('lat') or view.lat
        lng = attrs.get('lng') or view.lng
        latlng = attrs.get('latlng') or view.latlng

        if dataset not in app.datasets.all():
            msg = u"The dataset '%s' has not associated to the app '%s'." % (dataset.dataset_name, app.name)
            raise ValidationError({'dataset': [msg]})

        datapoint_strategy = attrs['datapoint_strategy']
        datapoint_strategies = set(o for o in dataset.datapoint_strategies.all())
        if datapoint_strategy is None and dataset.category == SINGLE:
            datapoint_strategy = PointID
        if datapoint_strategy is None and dataset.category == GRID:
            datapoint_strategy = Polygon if latlng and latlng.strip() else ApproachPoint
        if datapoint_strategy not in datapoint_strategies:
            msg = "Invalid value, it should be an item of [%s]" % ','.join(o.strategy_name for o in datapoint_strategies)
            raise ValidationError({'datapoint_strategy': [msg]})
        attrs['datapoint_strategy'] = datapoint_strategy

        strategy_name = datapoint_strategy.strategy_name
        if dataset.category == SINGLE:
            if strategy_name == PointID.strategy_name:
                attrs['singlepoint'] = singlepoint = self.associate_by_point_id(dataset, point_id or view.label)
            elif strategy_name == ClosestPair.strategy_name:
                attrs['singlepoint'] = singlepoint = self.associate_by_closest_pair(dataset, lat, lng)
                attrs['lat'], attrs['lng'] = lat, lng
            else:
                raise RuntimeError("Invalid datapoint_strategy '%s'." % strategy_name)
            viewset = self.context['view']
            qs = Mapper.objects.filter(view=view, dataset=dataset)
            if viewset.action == 'create' and qs.filter(singlepoint=singlepoint).exists():
                if strategy_name == PointID.strategy_name:
                    msg = "The single point_id($view.label) '%s' had been associated with dataset '%s'." % (
                        singlepoint.point_id, dataset.dataset_name)
                    raise ValidationError({'point_id': [msg]})
                else:
                    msg = "The SinglePoint '%s' close to location(%s, %s) in dataset '%s' had been associated with view '%s'." % (
                        singlepoint.id, lng, lat, dataset.dataset_name, view.id)
                    raise ValidationError({'lat': [msg], 'lng': [msg]})
        elif dataset.category == GRID:
            if strategy_name == ApproachPoint.strategy_name:
                self.associate_by_closest_point(dataset, lat, lng)
                attrs['lat'], attrs['lng'] = lat, lng
            elif strategy_name == Polygon.strategy_name:
                self.associate_by_polygeon(dataset, latlng)
                attrs['latlng'] = latlng
            else:
                raise RuntimeError("Invalid datapoint_strategy '%s'." % strategy_name)
        else:
            msg = u"can not handle datapoint_strategy_name '%s' dataset_category '%s'" % (strategy_name, dataset.category)
            err_logger.waring(msg)
            raise ValidationError({'detail': [msg]})

        return attrs

    def associate_by_point_id(self, dataset, point_id):
        if point_id is None:
            raise ValidationError({'point_id': ['This may not be empty.']})
        try:
            singlepoint = SinglePoint.objects.get(point_id=point_id, dataset=dataset)
        except ObjectDoesNotExist:
            raise ValidationError({'point_id': ["The point_id '%s' is not defined in the dataset '%s'." % (point_id, dataset.dataset_name)]})
        return singlepoint

    def associate_by_closest_pair(self, dataset, lat, lng):
        try:
            ViewSerializer.validate_lat(lat, allow_null=False)
        except ValidationError as e:
            raise ValidationError({'lat': e.detail})
        try:
            ViewSerializer.validate_lng(lng, allow_null=False)
        except ValidationError as e:
            raise ValidationError({'lng': e.detail})

        request = self.context['request']
        query_params = ["lat=%s&lng=%s" % (lat, lng)]
        urlencode = request.GET.urlencode()
        if urlencode:
            query_params.append(urlencode)
        url = _reverse(viewname='closestpoint-list',
                       kwargs={'dataset_name': dataset.dataset_name},
                       request=self.context['request'],
                       ) + '?' + '&'.join(query_params)
        url = url.replace('127.0.0.1', 'localhost')
        res = http_forward_get(url, self.context['request'])
        if res.status_code != 200:
            raise ValidationError(res.json())
        single_point_url = res.json()['url']
        return instance_from_url(single_point_url)

    def associate_by_closest_point(self, dataset, lat, lng):
        try:
            ViewSerializer.validate_lat(lat, allow_null=False)
        except ValidationError as e:
            raise ValidationError({'lat': e.detail})
        try:
            ViewSerializer.validate_lng(lng, allow_null=False)
        except ValidationError as e:
            raise ValidationError({'lng': e.detail})
        creator = LatLngURLCreator(dataset.dataset_name, lat, lng)
        if creator.has_url():
            url = creator.get_url()
            try:
                json = http_intercept_get(url).json()
            except InterceptedException as e:
                raise ValidationError({'lat': [e.detail], 'lng': [e.detail]})
            if not json.get('data') or str(json['data'][0]["dts"][0]["taus"][0]["val"]) == str(-9999):
                latlng = "%s,%s; %s,%s; %s,%s; %s,%s; %s,%s;" % (
                lat + 0.25, lng - 0.25, lat + 0.25, lng + 0.25, lat - 0.25, lng + 0.25, lat - 0.25, lng - 0.25, lat + 0.25, lng - 0.25)
                msg = u"無效的點Point(%s, %s)超出了資料集 '%s' 的定義範圍. 建議您使用Polygon([%s])取值。" % (lat, lng, dataset.dataset_name, latlng)
                raise ValidationError({'lat': [msg], 'lng': [msg]})
        return self

    def associate_by_polygeon(self, dataset, latlng):
        try:
            ViewSerializer.validate_latlng(latlng, allow_null=False)
        except ValidationError as e:
            raise ValidationError({'latlng': e.detail})
        creator = PolygenURLCreator(dataset.dataset_name, latlng)
        if creator.has_url():
            url = creator.get_url()
            try:
                json = http_intercept_get(url).json()
            except InterceptedException as e:
                raise ValidationError({'latlng': [e.detail]})
            if not json.get('data') or str(json['data'][0]["dts"][0]["taus"][0]["val"]) == str(-9999):
                msg = u"無效的區域 Polygon([%s]) 超出了資料集'%s'的定義範圍，請重新劃定區域。" % (latlng, dataset.dataset_name)
                raise ValidationError({'latlng': [msg]})
        else:
            err_logger.warning(u"無法對資料集 '%s' 的資料取點 Polygon('%s')。" % (dataset.dataset_name, latlng))
        return self


class SpeciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Species
        fields = '__all__'

from rest_framework import serializers
from qiange.dynamic_fields_mixin import DynamicFieldsMixin

from . import models


class GtSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Gt
        fields = '__all__'


class AquaCultureSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Aquaculture
        fields = '__all__'


class BuoySerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Buoy
        fields = '__all__'


class FishingSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Fishing
        fields = '__all__'


class HarborSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Harbor
        fields = '__all__'


class MarineSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Marine
        fields = '__all__'


class MarineSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Marine
        fields = '__all__'


class StationDaylightSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stationdaylight
        fields = '__all__'


class StationObsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stationobs
        fields = '__all__'


class StationObs2Serializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stationobs2
        fields = '__all__'


class STObsSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Stobs
        fields = '__all__'


class TideSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Tide
        fields = '__all__'


class ObserveDatumSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.ObserveDatum
        fields = '__all__'


class Nww3WrfSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Nww3Wrf
        fields = '__all__'


class Ocm3Serializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Ocm3
        fields = '__all__'


class STwarnSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.STwarn
        fields = '__all__'


class AqfnSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Aqfn
        fields = '__all__'


class AqiSerializer(DynamicFieldsMixin, serializers.ModelSerializer):
    class Meta:
        model = models.Aqi
        fields = '__all__'

# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey has `on_delete` set to the desired behavior.
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from __future__ import unicode_literals

from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class SinglePoint(models.Model):
    dataset = models.ForeignKey('Dataset', models.CASCADE)
    point_id = models.CharField(max_length=32)
    name = models.CharField(max_length=20, blank=True, null=True)
    lng = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, null=True)
    # mpoly = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'info_single_point'

    def __unicode__(self):
        return u'{ServerURL}/datapoints/%s/ => %s|%s' % (self.id, self.dataset.dataset_name, self.point_id)


class DatapointStrategy(models.Model):
    strategy_name = models.CharField(unique=True, max_length=16)
    description = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'info_datapoint_strategy'

    def __unicode__(self):
        return u'%s => %s' % (self.strategy_name, self.description)


class DatasetDatapointStrategy(models.Model):
    dataset = models.ForeignKey('Dataset', models.CASCADE)
    datapoint_strategy = models.ForeignKey(DatapointStrategy, models.CASCADE)

    class Meta:
        managed = False
        db_table = 'info_dataset_datapoint_strategy'


class Service(models.Model):
    cname = models.CharField(unique=True, max_length=16)

    class Meta:
        managed = False
        db_table = 'info_service'

    def __unicode__(self):
        return u'%s: %s' % (self.id, self.cname)


class Application(models.Model):
    name = models.CharField(unique=True, max_length=16)
    description = models.CharField(max_length=255)
    service = models.ForeignKey(Service, models.CASCADE)
    datasets = models.ManyToManyField('Dataset', through='ApplicationDataset')

    class Meta:
        managed = False
        db_table = 'manage_app'

    def __unicode__(self):
        return u'%s => %s | %s' % (self.id, self.name, self.service.cname)


class ApplicationDataset(models.Model):
    app = models.ForeignKey(Application, models.CASCADE)
    dataset = models.ForeignKey('Dataset', models.CASCADE)

    class Meta:
        managed = False
        db_table = 'manage_app_dataset'


class Dataset(models.Model):
    dataset_name = models.CharField(unique=True, max_length=16)
    category = models.CharField(max_length=6)
    description = models.CharField(max_length=255, blank=True, null=True)
    is_api_available = models.SmallIntegerField(blank=True, null=True)
    datapoint_strategies = models.ManyToManyField(DatapointStrategy, through='DatasetDatapointStrategy')

    class Meta:
        managed = False
        db_table = 'info_dataset'

    def __unicode__(self):
        return u'{ServerURL}/datasets/%s/' % self.dataset_name


class City(models.Model):
    code = models.CharField(unique=True, max_length=6)
    cname = models.CharField(unique=True, max_length=4)

    class Meta:
        managed = False
        db_table = 'info_city'

    def __unicode__(self):
        return u'%s => %s' % (self.code, self.cname, )


class Town(models.Model):
    code = models.CharField(unique=True, max_length=16)
    city_cname = models.CharField(max_length=10)
    cname = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    lng = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'info_town'
        unique_together = (('city_cname', 'cname'),)

    def __unicode__(self):
        return u'%s => %s-%s' % (self.code, self.city_cname, self.cname)


class View(models.Model):
    app = models.ForeignKey(Application, models.CASCADE)
    label = models.CharField(max_length=255)
    name = models.CharField(max_length=255, blank=True, null=True)
    category = models.CharField(max_length=255, blank=True, null=True)
    location_name = models.CharField(max_length=255, blank=True, null=True)
    city = models.ForeignKey(City, models.DO_NOTHING, blank=True, null=True)
    town = models.ForeignKey(Town, models.DO_NOTHING, blank=True, null=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    lng = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    latlng = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ('id', )
        managed = False
        db_table = 'manage_view'
        unique_together = (('app', 'label', 'name'),)

    def __unicode__(self):
        return u'%s => %s | %s | %s' % (self.id, self.label, self.category, self.name)


class Mapper(models.Model):
    view = models.ForeignKey(View, models.CASCADE, related_name='mappers')
    app = models.ForeignKey(Application, models.CASCADE)
    dataset = models.ForeignKey(Dataset, models.CASCADE)
    datapoint_strategy = models.ForeignKey(DatapointStrategy, models.CASCADE)
    singlepoint = models.ForeignKey(SinglePoint, models.CASCADE, blank=True, null=True)
    lat = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    lng = models.DecimalField(max_digits=12, decimal_places=8, blank=True, null=True)
    latlng = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'manage_mapper'


class Species(models.Model):
    species_id = models.CharField(max_length=4)
    species_name = models.CharField(max_length=16)
    species_alias = models.CharField(max_length=16, blank=True, null=True)
    mmin_acc_temp = models.IntegerField(default=17, validators=[MaxValueValidator(17), MinValueValidator(10)])
    mmax_acc_temp = models.IntegerField(default=33, validators=[MaxValueValidator(36), MinValueValidator(33)])
    min_acc_temp = models.IntegerField(default=15, validators=[MaxValueValidator(15), MinValueValidator(8)])
    max_acc_temp = models.IntegerField(default=35, validators=[MaxValueValidator(38), MinValueValidator(35)])
    min_pressure = models.SmallIntegerField(default=10, validators=[MaxValueValidator(30), MinValueValidator(10)])
    max_1h_rain = models.SmallIntegerField(default=20, validators=[MaxValueValidator(100), MinValueValidator(20)])
    max_6h_rain = models.SmallIntegerField(default=40, validators=[MaxValueValidator(100), MinValueValidator(40)])

    class Meta:
        managed = False
        db_table = 'info_species'


PointID = DatapointStrategy.objects.get(strategy_name='PointID')
ClosestPair = DatapointStrategy.objects.get(strategy_name='ClosestPair')
ApproachPoint = DatapointStrategy.objects.get(strategy_name='ApproachPoint')
Polygon = DatapointStrategy.objects.get(strategy_name='Polygon')

GRID = 'Grid'
SINGLE = 'Single'
dataset_qs = Dataset.objects.filter(is_api_available=1)

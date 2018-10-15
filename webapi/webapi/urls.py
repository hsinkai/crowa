"""webapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.views import get_swagger_view

from django.conf import settings
from django.conf.urls.static import static
import DataStore.views
import Manage.views
import Authorization.views
from qiange.router import BaseRouter

router = BaseRouter()
router.register(r'apps', Manage.views.ApplicationViewSet)
router.register(r'datasets', Manage.views.DataSetViewSet)
router.register(r'cities', Manage.views.CityViewSet)
router.register(r'towns', Manage.views.TownViewSet)
router.register(r'views', Manage.views.ViewViewSet)
router.register(r'views', Manage.views.ViewViewSet)
router.register(r'mappers', Manage.views.MapperViewSet)
router.register(r'singlepoints', Manage.views.SinglePointViewSet)
router.register(r'species', Manage.views.SpeciesViewSet)
router.register(r'closestpoint/dataset_name/(?P<dataset_name>[a-zA-Z0-9_-]+)', DataStore.views.ClosestSinglePointView, 'closestpoint')

router.register(r'datastore/GT', DataStore.views.GtViewSet)
router.register(r'datastore/AquaCulture', DataStore.views.AquaCultureViewSet)
router.register(r'datastore/Buoy', DataStore.views.BuoyViewSet)
router.register(r'datastore/Harbor', DataStore.views.HarborViewSet)
router.register(r'datastore/Fishing', DataStore.views.FishingViewSet)
router.register(r'datastore/Marine', DataStore.views.MarineViewSet)
router.register(r'datastore/StationObs', DataStore.views.StationObsViewSet)
router.register(r'datastore/StationObs2', DataStore.views.StationObs2ViewSet)
router.register(r'datastore/StationDaylight', DataStore.views.StationDaylightViewSet)
router.register(r'datastore/Tide', DataStore.views.TideViewSet)
router.register(r'datastore/ObserveDatum', DataStore.views.ObserveDatumViewSet)
router.register(r'datastore/AQFN', DataStore.views.AqfnViewSet)
router.register(r'datastore/AQI', DataStore.views.AqiViewSet)
# router.register(r'datastore/STWarn', DataStore.views.STWarnViewSet)
router.register(r'datastore/OCM3', DataStore.views.Ocm3ViewSet)
router.register(r'datastore/NWW3_WRF', DataStore.views.Nww3WrfViewSet, 'nww3_wrf')
router.register(r'datastore/Sunrise', DataStore.views.SunriseViewSet, 'sunrise')
router.register(r'query/view_id/(?P<view_id>[0-9]+)/dataset_name/(?P<dataset_name>[a-zA-Z0-9_-]+)', DataStore.views.AdvancedQueryViewSet, 'qeury')
# router.register(r'query', DataStore.views.DataViewSet, 'qeury')


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'accounts/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'schema/$', get_schema_view(title='CRS WebAPI')),
    url(r'document/$', get_swagger_view(title='CRS WebAPI', url='/api/v1')),
    url(r'auth/token/', Authorization.views.TokenAuthorizationView.as_view()),
    # url(r'auth/token2/', Authorization.views.JWTokenLoginRequiredAuthorizationView.as_view()),
    # url(r'document/$', get_swagger_view(title='CRS WebAPI', url='/')),
    url(r'', include(router.urls)),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


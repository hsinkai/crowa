
apikey = 'dbJKVicktSCyQzg6GNUQOn9yUKV473Wv'
apiroot = 'http://wddpapigate.cwb.gov.tw/API'


url_meta = {
    'OCM3': {
        'grid_url': apiroot + '/pointValueLatestApi-OCM3/model/OCM3/element/100/level/W00/latitude/{latitude}/longitude/{longitude}/q?apikey=%s' % apikey,
        'poly_url': apiroot + '/polygonAggregateLatestApi-OCM3/model/OCM3/element/100/level/W00/aggregate/avg?latlng={latlng}&apikey=%s' % apikey,
    },
    'NWW3_WRF': {
        'grid_url': apiroot + '/pointValueLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/002/level/W00/latitude/{latitude}/longitude/{longitude}/q?apikey=%s' % apikey,
        'poly_url': apiroot + '/polygonAggregateLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/002/level/W00/aggregate/avg?latlng={latlng}&apikey=%s' % apikey,
    }
}


class LatLngURLCreator(object):
    def __init__(self, table_name, latitude, longitude):
        self.table_name = table_name
        self.latitude = latitude
        self.longitude = longitude

    def has_url(self):
        return url_meta.get(self.table_name, False)

    def get_url(self):
        url_format = url_meta[self.table_name]['grid_url']
        return url_format.format(latitude=self.latitude, longitude=self.longitude)


class PolygenURLCreator(object):
    def __init__(self, table_name, latlng):
        self.table_name = table_name
        self.latlng = latlng

    def has_url(self):
        return url_meta.get(self.table_name, False)

    def get_url(self):
        url_format = url_meta[self.table_name]['poly_url']
        return url_format.format(latlng=self.latlng)

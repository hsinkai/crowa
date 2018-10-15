# -*- coding: utf-8 -*-

import petl
import dbman
import requests

# tt = petl.fromcsv(u'C:/Users/albin/Desktop/鄉鎮經緯度.csv')
    # responses.append(res.json())
# t2 = petl.wrap(petl.fromdicts(errors))
# petl.tocsv(t2, r'C:\Users\albin\Desktop\error_towns.csv')

token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IndlYmFwaWFkbSIsImV4cCI6MTUzOTMzMDA2OC4wfQ.uHTimkSpRoLOXQYJKfrLT682YdxMgTSl9u47V8U2n2E'
def db_setting(pattern):
    info = dict()
    if pattern == "AQI":
        proxy = dbman.RWProxy(db_label='61.60.103.175/CRSdb')
        table = proxy.fromdb("""SELECT * FROM AQI """)
        url = 'http://61.60.103.175:33333/api/v1/singlepoints/?token=' + token
        info['table'] = table
        info['url'] = url

    elif pattern == "AQFN":
        proxy = dbman.RWProxy(db_label='61.60.103.175/CRSdb')
        table = proxy.fromdb("""SELECT DISTINCT area FROM AQFN """)
        url = 'http://61.60.103.175:33333/api/v1/singlepoints/?token=' + token
        info['table'] = table
        info['url'] = url

    elif pattern == "education":
        proxy = dbman.RWProxy(db_label='61.60.103.175/CRSdb')
        table = proxy.fromdb("""SELECT t1.*, info_town.`code` AS town_code
                                FROM (
                                            SELECT education.*, info_city.id AS city_id
                                            FROM education, info_city
                                            WHERE education.city = info_city.cname
                                ) AS t1
                                LEFT JOIN info_town
                                    ON t1.city = info_town.city_cname AND t1.town = info_town.cname
                            """)
        url = 'http://61.60.103.175:33333/api/v1/views/?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IndlYl9kZXZlbCIsImV4cCI6MTUzOTE1Nzk0MC4wfQ.L16eHbbhegm1mAqJ8Px18usEufQGAEICGV_nLphzKiQ'
        info['table'] = table
        info['url'] = url

    return info


def data_views(data, pattern):
    views = dict()
    if pattern == "AQI":
        views['point_id'] = data['site_name']
        views['dataset'] = 'http://61.60.103.175:33333/api/v1/datasets/AQI/'
        views['name'] = None
        views['lat'] = None if not data['lat'] else data['lat']
        views['lng'] = None if not data['lon'] else data['lon']

    elif pattern == "AQFN":
        views['point_id'] = data['area']
        views['dataset'] = 'http://61.60.103.175:33333/api/v1/datasets/AQFN/'
        views['name'] = None

    elif pattern == "education":
        views['app'] = 'http://61.60.103.175:33333/api/v1/apps/School/'
        views['label'] = data['town_code']
        views['category'] = None if data['education_stage'].strip() == '' else data['education_stage']
        views['name'] = data['location_name']
        views['location_name'] = data['address']
        views['city'] = None
        views['town'] = data['town_code']
        views['lat'] = data['lat']
        views['lng'] = data['lon']
        views['latlng'] = None

    # print 'views: ', views
    return views


def import_data(pattern):
    info = db_setting(pattern)  # pattern='AQI'
    responses = []
    for data in info['table'].dicts():
        views = data_views(data, pattern)
        res = requests.post(info['url'], json=views)
        print res.status_code, res.json()
        # break
        if res.status_code != 201:
            print res.status_code, res.json()
            raise Exception(data)


if __name__ == '__main__':

    import_data("AQI")
    import_data("AQFN")
    import_data("education")


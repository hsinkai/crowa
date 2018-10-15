import os
import sys
import time
import datetime
import MySQLdb
import requests

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, os.path.dirname(dir))

apikey = "dbJKVicktSCyQzg6GNUQOn9yUKV473Wv"
invalidvalue = -9999
missingvalue = None
# db connection
db = MySQLdb.connect(host=
"localhost",
    user="crsopr", passwd="cwb+123", db="CRSdb", charset='utf8')
cursor = db.cursor()

def generate_read_jwt():
    from rest_framework_jwt.settings import api_settings
    payload = {
        'id': None,
        'username': None,
        'exp': time.mktime((datetime.datetime.now() + api_settings.JWT_EXPIRATION_DELTA).timetuple()),
    }
    return api_settings.JWT_ENCODE_HANDLER(payload)


def http_get_latlng(url):
    response = requests.get(url)
    if response.status_code == 429:
        print response.status_code
        time.sleep(61)
        response = requests.get(url)
    if not response.json()['data']:
        return None
    else:
        for data in response.json()['data']:
            latlng_dict = {"lat": data['lat'], "lng": data['lng']}
            return latlng_dict


def http_get_url(url):
    point_dict = dict()
    response = requests.get(url)
    if response.status_code == 429:
        print response.status_code
        time.sleep(61)
        response = requests.get(url)
    # dict data is empty
    if not response.json()['data']:
        return None
    else:
        for data in response.json()['data']:
            for dts in data['dts']:
                dt = datetime.datetime.strptime(dts['dt'], '%Y-%m-%d %H:%M:%S')
                print "dt: " + dt.isoformat()
                print "length of tau(3 taus intervals): " + str(len(dts['taus']))
                # range is 3
                if len(dts['taus']) < 25:
                    api_portal_list = []
                    normal_tau_list = list(range(00, 73, 3))
                    for taus in dts['taus']:
                        api_portal_list.append(int(taus['tau'][2:]))
                    differ_tau_list = list(set(normal_tau_list) - set(api_portal_list))
                    # if tau not exist
                    for taus in differ_tau_list:
                        hour = int(taus)
                        time_for = dt + datetime.timedelta(hours=hour)
                        point_dict.update({str(time_for): missingvalue})
                # if tau is exist
                for taus in dts['taus']:
                    hour = int(taus['tau'][2:])
                    time_for = dt + datetime.timedelta(hours=hour)
                    if taus['val'] == str(invalidvalue):
                        point_dict.update({str(time_for): invalidvalue})
                    else:
                        point_dict.update({str(time_for): float(taus['val'])})
        return point_dict

datapoint_dict = dict()
u_dict = dict()
v_dict = dict()
speed_dict = dict()
dir_dict = dict()

selectqry = "SELECT id, lat, lng FROM manage_mapper WHERE dataset_id=12"
cursor.execute(selectqry)
datapoints_latlng = cursor.fetchall()

for id, lat, lng in datapoints_latlng:
    datapoint_list = []
    print "mapper_id: " + str(id)
    print "start: " + str(float(lat)) + ", " + str(float(lng))
    dir_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/002/level/W00/"
    hs_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/001/level/W00/"
    fd_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/F02/level/W00/"
    fhs_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-MMC_NWW3_WRF_WAVE/model/WWRF/element/F01/level/W00/"

    ignore_data_dir_url = dir_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    ignore_data_hs_url = hs_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    ignore_data_fd_url = fd_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    ignore_data_fhs_url = fhs_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    data_dir_url = dir_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    data_hs_url = hs_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    data_fd_url = fd_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
    data_fhs_url = fhs_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)

    dir_dict = http_get_url(data_dir_url) if http_get_url(ignore_data_dir_url) is None else http_get_url(ignore_data_dir_url)
    hs_dict = http_get_url(data_hs_url) if http_get_url(ignore_data_hs_url) is None else http_get_url(ignore_data_hs_url)
    fd_dict = http_get_url(data_fd_url) if http_get_url(ignore_data_fd_url) is None else http_get_url(ignore_data_fd_url)
    fhs_dict = http_get_url(data_fhs_url) if http_get_url(ignore_data_fhs_url) is None else http_get_url(ignore_data_fhs_url)
    latlng_dict = http_get_latlng(data_dir_url) if http_get_latlng(ignore_data_dir_url) is None else http_get_latlng(ignore_data_dir_url)

    for dt in set(dir_dict) & set(hs_dict) & set(fd_dict) & set(fhs_dict):
        datapoint_dict = (dict(mapper_id=id, time=dt, lat=latlng_dict['lat'],
                               lon=latlng_dict['lng'], dir=dir_dict.get(dt, 0), hs=hs_dict.get(dt, 0),
                               fd=fd_dict.get(dt, 0), fhs=fhs_dict.get(dt, 0)))
        datapoint_list.append(datapoint_dict)

    # insert db
    datalist = []
    for index in range(len(datapoint_list)):
        keys = ', '.join(datapoint_list[index].keys())
        values = ', '.join(['%s']*len(datapoint_list[index].keys()))
        tup = datapoint_list[index].values()
        datalist.append(tup)
    qry = "INSERT INTO NWW3_WRF (%s) VALUES (%s) ON DUPLICATE KEY UPDATE " \
          "lat = VALUES(lat), lon=VALUES (lon), dir=VALUES (dir), hs=VALUES(hs), " \
          "fd=VALUES(fd), fhs=VALUES(fhs)"% (keys, values)
    cursor.executemany(qry, datalist)
    print "------------- END------------"
    db.commit()
db.close()

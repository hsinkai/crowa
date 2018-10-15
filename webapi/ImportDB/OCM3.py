import os
import sys
import time
import datetime
import MySQLdb
import math
import requests

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, os.path.dirname(dir))

apikey = "dbJKVicktSCyQzg6GNUQOn9yUKV473Wv"
invalidvalue = -9999
missingvalue = None

# db connection
db = MySQLdb.connect(host="localhost",
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
                print "length of tau: " + str(len(dts['taus']))
                if len(dts['taus']) < 73:
                    api_portal_list = []
                    normal_tau_list = list(range(00, 73))
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


depth_define_list = [1, 5, 10]
datapoint_dict = dict()
u_dict = dict()
v_dict = dict()
speed_dict = dict()
dir_dict = dict()

selectqry = "SELECT id, lat, lng FROM manage_mapper WHERE dataset_id=9"
cursor.execute(selectqry)
datapoints_latlng = cursor.fetchall()

for id, lat, lng in datapoints_latlng:
    for depth in depth_define_list:
        datapoint_list = []
        print "mapper_id: " + str(id)
        print "start: " + str(float(lat)) + ", " + str(float(lng))
        print "depth: " + str(depth)

        temp_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-OCM3/model/OCM3/element/100/level/W%02d/" % (
        depth)
        u_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-OCM3/model/OCM3/element/200/level/W%02d/" % (
        depth)
        v_point_url = "http://wddpapigate.cwb.gov.tw/API/pointValueLatestApi-OCM3/model/OCM3/element/210/level/W%02d/" % (
        depth)
        data_temp_url = temp_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
        data_u_url = u_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
        data_v_url = v_point_url + 'latitude/%s/longitude/%s/q?apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
        ignore_data_temp_url = temp_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
        ignore_data_u_url = u_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)
        ignore_data_v_url = v_point_url + 'latitude/%s/longitude/%s/q?ignore=-9999&apikey=%s' % (str(float(lat)), str(float(lng)), apikey)

        temp_dict = http_get_url(data_temp_url) if http_get_url(ignore_data_temp_url) is None else http_get_url(ignore_data_temp_url)
        u_dict = http_get_url(data_u_url) if http_get_url(ignore_data_u_url) is None else http_get_url(ignore_data_u_url)
        v_dict = http_get_url(data_v_url) if http_get_url(ignore_data_v_url) is None else http_get_url(ignore_data_v_url)
        latlng_dict = http_get_latlng(data_temp_url) if http_get_latlng(ignore_data_temp_url) is None else http_get_latlng(ignore_data_temp_url)

        for k in set(u_dict) & set(v_dict):
            if u_dict.get(k, 0) == invalidvalue or v_dict.get(k, 0) == invalidvalue:
                speed = {k: invalidvalue}
                direction = {k: invalidvalue}
            elif u_dict.get(k, 0) == missingvalue or v_dict.get(k, 0) == missingvalue:
                speed = {k: missingvalue}
                direction = {k: missingvalue}
            else:
                speed = {k: math.sqrt(math.pow(u_dict.get(k, 0), 2) + math.pow(v_dict.get(k, 0), 2))}

                if (math.atan2(u_dict.get(k, 0), v_dict.get(k, 0)) / 0.0174) < 0:
                    direction = {k: (math.atan2(u_dict.get(k, 0), v_dict.get(k, 0)) / 0.0174) + 360}
                else:
                    direction = {k: math.atan2(u_dict.get(k, 0), v_dict.get(k, 0)) / 0.0174}
            dir_dict.update(direction)
            speed_dict.update(speed)
        # print "speed: " + str(speed_dict)
        # print"direction: " + str(dir_dict)
        # print "temperature: " + str(temp_dict)
        for dt in set(speed_dict) & set(dir_dict) & set(temp_dict):
            datapoint_dict = (dict(mapper_id=id, time=dt, depth="-" + str(depth), lat=latlng_dict['lat'],
                                   lon=latlng_dict['lng'], temp=temp_dict.get(dt, 0), speed=speed_dict.get(dt, 0),
                                   dir=dir_dict.get(dt, 0)))
            datapoint_list.append(datapoint_dict)
        # insert db
        datalist = []
        for index in range(len(datapoint_list)):
            keys = ', '.join(datapoint_list[index].keys())
            values = ', '.join(['%s']*len(datapoint_list[index].keys()))
            tup = datapoint_list[index].values()
            datalist.append(tup)
        qry = "INSERT INTO OCM3 (%s) VALUES (%s) ON DUPLICATE KEY UPDATE lat = VALUES(lat), lon=VALUES (lon),temp=VALUES (temp), speed=VALUES(speed), dir=VALUES(dir)"\
              % (keys, values)
        cursor.executemany(qry, datalist)
        print "------------- END------------"
        db.commit()
db.close()

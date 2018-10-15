import json
import os
import sys

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, os.path.dirname(dir))

from ImportDB.util import http_get, http_post, setup_django_rentime_depend
setup_django_rentime_depend()

datapoints_url = "http://localhost:8000/DataTables/4/DataPoints/"
datatable_url = "http://localhost:8000/DataTables/?application=6"
dataset_url = "http://localhost:8000/DataSets/6/"

input_json_list = []

for point in http_get(datapoints_url):
    input_json = {}
    input_json['related_info'] = items = []
    input_json['application'] = dataset_url
    input_json['name'] = point['point_id']

    for table in http_get(datatable_url):
        table_url = table['url']
        item = {
            'dataset': table_url
        }
        if table['datapoint_strategy'] == 'Station':
            nears_point_url = table_url + 'DataPoints/lat/%s/lng/%s/' % (point['lat'], point['lng'])
            try:
                datapoint_url = http_get(nears_point_url)['url']
                item['datapoint'] = datapoint_url
                items.append(item)
                input_json_list.append(input_json)
            except:
                pass

        elif table['datapoint_strategy'] == 'Grid':
            item['lat'] = point['lat']
            item['lng'] = point['lng']
            items.append(item)
            input_json_list.append(input_json)

        elif table['datapoint_strategy'] == 'Region': pass

        elif table['datapoint_strategy'] == 'Polygon': pass

    print json.dumps(input_json, indent=2)
    # http_post('http://localhost:8000/Views/', input_json)

with open(__file__ + '.json', 'w') as fp:
    content = json.dumps(input_json_list, indent=2)
    fp.write(content)
import os
import sys

dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, dir)
sys.path.insert(0, os.path.dirname(dir))

from ImportDB.util import setup_django_rentime_depend
setup_django_rentime_depend()

from url_meta import LatLngURLGenerator
for uri in LatLngURLGenerator('OCM3', 23, 45):
    print uri
raise SystemExit

datapoints_url = "http://localhost:8000/DataTables/5/DataPoints/"
datatable_url = "http://localhost:8000/DataTables/?application=8"
dataset_url = "http://localhost:8000/DataSets/8/"

input_json_list = []

for point in http_get(datapoints_url):
    input_json = {}
    input_json['related_info'] = items = []
    input_json['application'] = dataset_url
    # http: // localhost:8000 / DataPoints / Regions / 1 /
    regex = re.compile(r'.*/(\d+)/')
    input_json['name'] = 'FM' + '%03d' % int(regex.match(point['url']).groups()[0])

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

        elif table['datapoint_strategy'] == 'Region':
            item['datapoint'] = point['url']
            items.append(item)
            input_json_list.append(input_json)

        elif table['datapoint_strategy'] == 'Polygon': pass

    # print json.dumps(input_json, indent=2)
    http_post('http://localhost:8000/Views/', input_json)

with open(__file__ + '.json', 'w') as fp:
    content = json.dumps(input_json_list, indent=2)
    fp.write(content)
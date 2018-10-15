import requests, json

def http_get(url):
    res = requests.get(url, cookies={'sessionid': "slzs5yooaszhnduzekuhc726o4mdxgiv"})
    return res.json()


def http_post(url, _json):
    res = requests.post(url, json=_json)
    print json.dumps(res.json())
    return json.dumps(res.json())

points = http_get("http://localhost:8000/DataTables/6/DataPoints/")
stations_url = "http://localhost:8000/DataPoint/Stations/"

for point in points:
    print point
    point['point_id'] = point['point_id'][:-1]
    point['datatable_id'] = 14
    point.pop('url')
    http_post(stations_url, point)

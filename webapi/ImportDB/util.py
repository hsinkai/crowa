import time
import json
import datetime

import requests


def setup_django_rentime_depend(settings="webapi.settings2"):
    import django
    import os
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    django.setup()


def generate_read_jwt():
    from rest_framework_jwt.settings import api_settings
    payload = {
        'id': None,
        'username': None,
        'exp': time.mktime((datetime.datetime.now() + api_settings.JWT_EXPIRATION_DELTA).timetuple()),
    }
    return api_settings.JWT_ENCODE_HANDLER(payload)


def generate_write_jwt():
    from rest_framework_jwt.settings import api_settings
    payload = {
        'id': 1,
        'username': 'developer',
        'exp': time.mktime((datetime.datetime.now() + api_settings.JWT_EXPIRATION_DELTA).timetuple()),
    }
    return api_settings.JWT_ENCODE_HANDLER(payload)


def http_get(url):
    header = {'Authorization': generate_read_jwt()}
    res = requests.get(url, headers=header)
    print 'GET: %s' % url, res
    return res.json()


def http_post(url, _json):
    header = {'Authorization': generate_write_jwt()}
    res = requests.post(url, headers=header, json=_json)
    print "POST '%s'" % url, res
    if res.status_code != 201:
        print "POST Fail: %s" % url, res.text
    return json.dumps(res.json())
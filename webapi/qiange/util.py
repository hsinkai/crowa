import re

import requests
from django.urls import resolve
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from qiange import err_logger


SERVER_URL_PATTERN = re.compile(r'(http://[\.\w]+(:\d+)?)?(/api/v\d+)?')


class InterceptedException(Exception):
    """
    raise this Exception if a request could not be handled or should be intercepted
    """
    def __init__(self, detail, status=500):
        self.detail = detail
        self.status = status

    def make_response(self):
        if isinstance(self.detail, dict):
            return Response(
               self.detail,
                status=self.status,
            )
        else:
            return Response(
                {'detail': [self.detail]},
                status=self.status,
            )


def extra_path_from_url(url):
    try:
        path = SERVER_URL_PATTERN.sub('', url)
    except Exception as e:
        err_logger.error(url + ' ' + unicode(e))
        raise ValidationError(["Invalid URL  '%s'" % url])
    return path


def instance_from_url(url):
    path = extra_path_from_url(url)
    try:
        func, args, kwargs = resolve(path)
        instance = func.cls.queryset.get(**kwargs)
    except Exception as e:
        err_logger.error(str(e))
        raise ValidationError(["does not exist URL '%s'" % url])
    return instance


def calculate_dis(lng1, lat1, lng2, lat2):
    """
        Calculate the great circle distance between two points
         on the earth (specified in decimal degrees)
         """
    from math import radians, cos, sin, asin, sqrt

    # convert decimal degrees to radians
    lng1, lat1, lng2, lat2 = map(radians, [lng1, lat1, lng2, lat2])
    # haversine formula
    dlon = lng2 - lng1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    km = 6367 * c
    return km


def extract_incoming(request, location=None):
    """
    :return a dictionary extract from QueryString or HTTP Body
    """
    location = location or 'data'
    incoming = request.query_params if request.method == 'GET' else getattr(request, location, dict())
    return incoming


def http_intercept_get(url):
    try:
        res = requests.get(url)
    except Exception as e:
        raise InterceptedException(detail="Gateway error: %s" % str(e), status=502)

    if res.status_code != 200:
        raise InterceptedException(detail=res.text, status=res.status_code)

    return res


def http_forward_get(url, request):
    try:
        res = requests.get(
                url,
                cookies={'sessionid': request.COOKIES['sessionid']} if 'sessionid' in request.COOKIES else {},
                headers={'Authorization': request.META.get('Authorization')},
        )
    except Exception as e:
        raise InterceptedException(detail="Gateway error: %s" % str(e), status=502)
    return res

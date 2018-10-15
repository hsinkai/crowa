from __future__ import unicode_literals

import traceback
import sys

from rest_framework_filters.backends import DjangoFilterBackend
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework import permissions, authentication, response, views, status

import qiange
from qiange.keys import QUERY_DICT, WITH_META, METADATA, DATA
from qiange.authentications import JWTokenAuthentication
from qiange import err_logger as logger
from qiange.util import InterceptedException


class CustFilterBackend(DjangoFilterBackend):
    def filter_queryset(self, request, queryset, view):
        with self.patched_filter_class(request):
            filter_class = self.get_filter_class(view, queryset)
            if filter_class:
                filter = filter_class(request.query_params, queryset=queryset, request=request)
                queryset = filter.qs
                setattr(view, QUERY_DICT, getattr(filter, QUERY_DICT, {}))
                return queryset
            return queryset


class ListView(qiange.ListLog, qiange.LogFacade, mixins.ListModelMixin, GenericViewSet):
    authentication_classes = (JWTokenAuthentication, authentication.SessionAuthentication, )
    permission_classes = (permissions.IsAuthenticated, permissions.DjangoModelPermissions, )
    filter_backends = (CustFilterBackend, )

    # def list(self, request, *args, **kwargs):
    #     tick = time.time()
    #     res = super(CustListView, self).list(request, *args, **kwargs)
    #
    #     res.data = {
    #         DATA: res.data,
    #     }
    #     if request.query_params.get(WITH_META, 'true').upper() == 'TRUE':
    #         res.data[METADATA] = getattr(self, QUERY_DICT, {})
    #         res.data[METADATA].update(cost=time.time() - tick,)
    #     return res


def error_handler(exc, context):
    # raise exc
    res = views.exception_handler(exc, context)
    if res is not None:
        return res

    if isinstance(exc, InterceptedException):
        return exc.make_response()

    if isinstance(exc, KeyError):
        logger.error(traceback.format_exc().decode(sys.getfilesystemencoding()))
        return response.Response({"detail": [u"KeyError: %s." % exc]}, status.HTTP_400_BAD_REQUEST)

    logger.error(traceback.format_exc().decode(sys.getfilesystemencoding()))
    return response.Response({"detail": [unicode(exc), u"A server error occurred."]}, status.HTTP_500_INTERNAL_SERVER_ERROR)

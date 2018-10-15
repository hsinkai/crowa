
from rest_framework.routers import DefaultRouter, APIRootView


class ServerRootView(APIRootView):
    def get(self, request, *args, **kwargs):
        res = super(ServerRootView, self).get(request, *args, **kwargs)
        ret = res.data
        view_url = ret['views']
        server_url = view_url.replace('views/', '')
        ret['query'] = server_url + 'datastore/query/view_id/19/dataset_name/GT/'
        ret['auth/token'] = server_url + 'auth/token/'
        ret['closestpoint'] = server_url + 'closestpoint/dataset_name/GT/?lat=23.5&lng=120'
        return res


class BaseRouter(DefaultRouter):
    APIRootView = ServerRootView
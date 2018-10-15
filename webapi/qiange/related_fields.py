from django.urls import reverse as django_reverse
from rest_framework import serializers

from Manage.models import dataset_qs, Dataset

gate_way_domain = False # and 'http://2384.323/aaap/ddd'
is_absolute_uri = True


def _reverse(viewname, args=None, kwargs=None, request=None, format=None, **extra):
    """
    Same as `django.urls.reverse`, but optionally takes request and is_absolute_uri;
    returns a fully qualified URL if is_absolute_uri is True, using the gate_way_domain
    or request to get the base URL.
    """
    if format is not None:
        kwargs = kwargs or {}
        kwargs['format'] = format
    url = django_reverse(viewname, args=args, kwargs=kwargs, **extra)
    if request and is_absolute_uri:
        if gate_way_domain:
            url = gate_way_domain + url
        else:
            url = request.build_absolute_uri(url)
    return url


class _URLMixin(object):
    def get_url(self, obj, view_name, request, format):
        """
        Given an object, return the URL that hyperlinks to the object.

        May raise a `NoReverseMatch` if the `view_name` and `lookup_field`
        attributes are not configured to correctly match the URL conf.
        """
        # Unsaved objects will not yet have a valid URL.
        if hasattr(obj, 'pk') and obj.pk in (None, ''):
            return None

        lookup_value = getattr(obj, self.lookup_field)
        kwargs = {self.lookup_url_kwarg: lookup_value}
        url = _reverse(view_name, kwargs=kwargs, request=request, format=format)
        return url


def make_hyperlinked_identity_field(**kwargs):
    class Field(_URLMixin, serializers.HyperlinkedIdentityField): pass
    return Field(**kwargs)


def make_hyperlinked_related_field(**kwargs):
    class Field(_URLMixin, serializers.HyperlinkedRelatedField): pass
    return Field(**kwargs)


def application_related_context(with_queryset=True):
    context = {
        'view_name': 'application-detail',
        'lookup_field': 'id'
    }
    if with_queryset:
        from Manage.models import Application
        context['queryset'] = Application.objects.all()
    return context


def dataset_related_context(with_queryset=True):
    context = {
        'view_name': 'dataset-detail',
        'lookup_field': 'dataset_name'
    }
    if with_queryset:
        # context['queryset'] = dataset_qs.all()
        context['queryset'] = Dataset.objects.all()
    return context


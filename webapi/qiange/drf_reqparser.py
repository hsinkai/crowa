import copy
import inspect
import numbers
import datetime
import re

from rest_framework.exceptions import ValidationError
from dateutil import parser, tz

split_sep_pattern = re.compile(r'[,;]')
tz_taipei = tz.gettz('Asia/Taipei')
tz_utc = tz.tzutc()
tz_local = tz.tzlocal()
offset_timedelta = datetime.timedelta(hours=8)


def parse_uri_timestr(uri_timestr, ignoretz=False, **kwargs):
    uri_timestr = uri_timestr.replace(' ', '+')
    dt = parser.parse(uri_timestr, ignoretz=ignoretz, **kwargs)
    return dt


def str2localdt(timestr, **kwargs):
    dt = parse_uri_timestr(timestr, **kwargs)
    if dt.tzinfo:
        dt = dt.astimezone(tz.tzlocal())
        dt = dt.replace(tzinfo=None)
    return dt


def str2dtutc(timestr, **kwargs):
    dt = parse_uri_timestr(timestr, **kwargs)
    dt = dt.astimezone(tz.tzutc()) if dt.tzinfo else dt.replace(tzinfo=tz.tzutc())
    dt = dt.replace(tzinfo=None)
    return dt


def str2dt_tzutc(timestr, **kwargs):
    dt = parse_uri_timestr(timestr, **kwargs)
    return dt.astimezone(tz.tzutc()) if dt.tzinfo else dt.replace(tzinfo=tz.tzutc())


def str2dt_tztaipei(time_str):
    try:
        value = parse_uri_timestr(time_str, ignoretz=False)
        value = value.astimezone(tz_taipei) if value.tzinfo else value.replace(tzinfo=tz_taipei)
    except Exception as e:
        try:
            msg = [m for m in e]
            raise ValidationError(msg)
        except TypeError:
            raise ValidationError([str(e)])
    return value


def split_str(string, required=True):
    if required and not string:
        raise ValidationError({'detail': ["Can not split empty string"]})
    return split_sep_pattern.split(string)


def split_str_into_set(string, required=True):
    str_list = split_str(string, required)
    return set(str_list)


def str2bool(string):
    if isinstance(string, bool):
        return string
    if 'TRUE' == string.upper():
        return True
    return False


def split_and_convert_sortedlevel(opt_level_str):
    if not opt_level_str:
        return None
    levels = split_str(opt_level_str)
    levels = map(lambda x: int(x), levels)
    return sorted(levels)


def select(_callable, options, multiple=False):
    def decorator(*args, **kwargs):
        assert options, "This resource is not available"
        selected = _callable(*args, **kwargs)
        if selected is None:
            return selected
        if multiple:
            selected = set(selected)
            assert selected <= options, \
                u"Invalid values '%s', which should be a subset of set([%s])" % (
                    ','.join(selected - options), ','.join(options)
                )
        else:
            assert selected in options, \
                u"Invalid value '%s', which should be an item of set([%s])" % (
                    selected, ','.join(options)
                )
        return selected
    return decorator


class RequestParser(object):
    """validate/parse a request's Content or QueryString and convert to a ``dict`` object ."""

    def __init__(self):
        self.schema = dict()

    def copy(self):
        return copy.deepcopy(self)

    def add_argument(self, name, dest=None, type=unicode, required=False, default=None, action='store'):
        self.schema[name] = (dest or name, type, required, default, action)

    def remove_argument(self, name, ):
        del self.schema[name]

    def parse_args(self, raw_args, strict=False):
        incoming = dict()
        for name, (_dest, _type, required, default, action) in self.schema.items():
            if required:                   # required argument
                try:
                    value = raw_args[name]
                except KeyError:
                    raise ValidationError({name: [u"Parameter was not present"]})
            else:                          # optional argument
                value = raw_args.get(name)
                if not value:
                    incoming[_dest] = default
                    continue

            if action == 'append' and (value is not None):
                _list = []
                for item in value:
                    item = self.__convert_or_verify_type(name, _type, item, required, default)
                    _list.append(item)
                incoming[_dest] = _list
            elif action == 'store':
                value = self.__convert_or_verify_type(name, _type, value, required, default)
                incoming[_dest] = value
            else:
                return RuntimeError("Given action is invalid: %s" % name)
        if strict:
            name_set = set(raw_args.keys()) - (set(incoming.keys()) | set(self.schema.keys()))
            if name_set:
                raise ValidationError({name_set.pop(): [u"Unknow Parameter"]})
        return incoming

    @staticmethod
    def __convert_or_verify_type(name, _type, value, required, default):
        if not required and value is None:
            return default
        if inspect.isclass(_type) and (not issubclass(_type, numbers.Number)) and (not isinstance(value, _type)):
            raise ValidationError({name: ["Parameter type error, it's should be %s" % _type.__name__]})
        try:
            value = _type(value)
        except AssertionError as e:
            raise ValidationError({'detail': [unicode(e)]})
        except Exception as e:
            raise ValidationError({name: [u"Parameter can not be parsed, %s." % unicode(e)]})
        return value

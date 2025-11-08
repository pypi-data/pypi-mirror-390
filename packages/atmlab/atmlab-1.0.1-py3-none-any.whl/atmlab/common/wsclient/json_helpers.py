import json
from datetime import datetime, timedelta
from types import SimpleNamespace

import aniso8601

from gamme import Quantity as PyQuantity
from gamme import Units as PyUnits

try:
    from gamme.jcore import Quantity as JQuantity
    enable_java = True
except ModuleNotFoundError:
    enable_java = False


class DefaultEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, PyQuantity):
            return str(o)
        elif isinstance(o, timedelta):
            return self.default(PyQuantity(o.seconds, PyUnits.second))
        elif enable_java and isinstance(o, JQuantity):
            return str(o)
        elif isinstance(o, datetime):
            return o.strftime('%Y-%m-%dT%H:%M:%SZ')
        elif isinstance(o, bool):
            return super().encode(o)
        else:
            return { k: v for k, v in o.__dict__.items() if v is not None }


def to_simple_namespace(response):
    obj = json.loads(response, object_hook=lambda d: SimpleNamespace(**d))
    return __to_simple_namespace(obj)


def __to_simple_namespace(obj):
    if isinstance(obj, list):
        for e in obj:
            __to_simple_namespace(e)
        return obj
    elif isinstance(obj, SimpleNamespace):
        for attr, value in obj.__dict__.items():
            obj.__dict__[attr] = __to_simple_namespace(value)
        return obj
    elif isinstance(obj, str):
        # Try as a Quantity
        try:
            return PyQuantity(obj)
        except ValueError:
            pass
        # Try as an ISO8601 datetime
        try:
            return aniso8601.parse_datetime(obj.replace(' ', 'T', 1))
        except ValueError:
            pass
        # Return the original string
        return obj
    else:
        return obj

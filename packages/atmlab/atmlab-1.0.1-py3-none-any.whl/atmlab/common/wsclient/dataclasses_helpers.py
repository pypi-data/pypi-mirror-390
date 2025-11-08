import datetime
from typing import Any, Mapping

import dataclasses_json
from dataclasses_json.stringcase import camelcase
from gamme.units import Quantity
import marshmallow



def __encode_datetime(d, format):
    if d is None:
        return None
    return d.strftime(format)


def __decode_datetime(d, format):
    try:
        return datetime.datetime.strptime(d, format)
    except ValueError:
        return datetime.datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%fZ')


class UTCDateTimeField(marshmallow.fields.Field):
    def __init__(self, format: str = '%Y-%m-%dT%H:%M:%SZ', **kwargs) -> None:
        super().__init__(**kwargs)
        self.__format = format
    def _deserialize(self, value, attr, data, **kwargs):
        try:
            return datetime.datetime.strptime(value, self.__format)
        except ValueError:
            return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%fZ')
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return value.strftime(self.__format)


def datetime_metadata(field_name=None, format='%Y-%m-%dT%H:%M:%SZ'):
    return dataclasses_json.config(
        # 'encoder': datetime.isoformat,
        # 'decoder': datetime.fromisoformat,
        # 'mm_field': fields.DateTime(format='iso', allow_none=True)
        field_name=field_name,
        encoder = lambda d: __encode_datetime(d, format=format),
        decoder = lambda d: __decode_datetime(d, format=format),
        # exclude=lambda f: f is None,
        # mm_field=None
        mm_field=UTCDateTimeField(data_key=field_name, format=format),
        # letter_case=dataclasses_json.LetterCase.CAMEL
    )

class QuantityField(marshmallow.fields.Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def _deserialize(self, value, attr, data, **kwargs):
        return Quantity.value_of(value)
    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return str(value)


def quantity_metadata(field_name=None):
    return dataclasses_json.config(
        encoder=Quantity.to_json,
        decoder=Quantity.value_of,
        mm_field=QuantityField(data_key=field_name)
    )


from peewee import *
from ...copier import *
from ...eloquent import *
from ..timeo import resolve
from .user_details import *
from typing import Self, Any
from datetime import datetime
from peewee import Model as PeeweeModel
from ...util import json_property, MetaObject


def serializer(obj):
    data = obj.__data__
    for key, _ in data.items():
        value = getattr(obj, key)
        if isinstance(value, Model):
            data[key] = serializer(value)
    return data


@json_property(serializer=serializer)
@request_param_filter(name="id", operator=RequestParamFilter.Operator.NONE)
@request_param_filter(name="created_at", operator=RequestParamFilter.Operator.RANGE)
@request_param_filter(name="updated_at", operator=RequestParamFilter.Operator.RANGE)
class Model(PeeweeModel):
    
    id: BigAutoField = BigAutoField(unique=True, primary_key=True, null=True)
    created_at: DateTimeField = DateTimeField(default=datetime.now())
    updated_at: DateTimeField = DateTimeField(default=datetime.now())
    
    def resolve(self: Self, base_request: 'Request', query_armoury: QueryArmoury = None, user_details: UserDetails = None) -> Self:
        Copier.copy(self, base_request)
        resolve(self)
        return self


class Request(MetaObject):
    
    ___BARMOURY_UPDATE_ENTITY_ID___: Any = None
    
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)
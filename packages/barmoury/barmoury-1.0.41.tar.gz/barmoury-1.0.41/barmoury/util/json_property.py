
from enum import Enum
from ..globals import *
from . import field_util
from typing import Dict, Any
from typing import Dict, Callable
from ..api.exception import InvalidArgumentException


class JsonPropertyAccess(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    READ_WRITE = "READ_WRITE"


class JsonProperty(field_util.MetaObject):
    key: str = None
    name: str = None
    options: Dict = None
    serializer: Callable[[Any], Any] = None
    deserializer: Callable[[Any], Any] = None
    access: JsonPropertyAccess = JsonPropertyAccess.READ_WRITE


def json_property(**args_options: Dict[str, Any]):
    options = JsonProperty(args_options)
    
    def json_property_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @json_property decorator can only be applied to a class")
        _register_field_json_property(obj, options)
        return obj
    
    return json_property_impl


def _register_field_json_property(clazz: Any, json_property: JsonProperty):
    key = clazz.__qualname__
    name = json_property.name

    if key not in JsonPropertyMap:
        JsonPropertyMap[key] = {}
    if name != None and name not in JsonPropertyMap[key]:
        JsonPropertyMap[key][name] = json_property
    else:
        JsonPropertyMap[key]["__self__"] = json_property
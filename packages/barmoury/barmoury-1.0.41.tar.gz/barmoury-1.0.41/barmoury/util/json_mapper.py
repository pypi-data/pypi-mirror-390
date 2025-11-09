
import json
from .util import *
from ..globals import *
from .field_util import *
from .json_property import *
from datetime import datetime

def to_json(value: Any, to_obj: bool = False, default: Any = str, stringify_types: List[Any] = [datetime], _name: str = None, _json_properties: Dict[str, JsonProperty] = {}) -> str:
    key: str = _name
    dictionary: Any = None
    json_property: JsonProperty = None
    json_properties = _json_properties or {}
    if not (type(value) == list or type(value) == dict) and is_class(value, deep=True):
        json_properties = merge_objects(False, find_type_json_properties(type(value)))
        if "__self__" in json_properties:
            json_property = json_properties["__self__"]
        else:
            value = value.__dict__
    if _name in json_properties :
        json_property = json_properties[_name]
    if json_property != None:
        if json_property.key != None:
            key = json_property.key
        if json_property.serializer != None:
            value = json_property.serializer(value)
        if json_property.access == JsonPropertyAccess.WRITE:
            return (key, "___barmoury_write_only___")
    if type(value) == list:
        dictionary = []
        for entry in value:
            entry_result = to_json(entry, True, default, _json_properties=json_properties)
            if entry_result != "___barmoury_write_only___":
                dictionary.append(entry_result)
        value = dictionary
    elif type(value) == dict:
        dictionary = {}
        for entry_key, entry in value.items():
            entry_result = to_json(entry, True, default, _name=entry_key, _json_properties=json_properties)
            if entry_result[1] != "___barmoury_write_only___":
                dictionary[entry_result[0]] = entry_result[1]
        value = dictionary
    should_stringify = type(value) in stringify_types
    if to_obj and not should_stringify:
        if _name == None:
            return value
        return (key, value)
    result = json.dumps(value, default=default)
    result = result.strip('"') if result.endswith('"') and should_stringify else result
    if _name == None:
        return result
    return (key, result)


def from_json(value: str, to_obj: bool = False) -> Any:
    json_un_marshal = json.loads(value)
    if type(json_un_marshal) == list:
        dictionary = []
        for entry in json_un_marshal:
            if type(entry) == dict and to_obj:
                dictionary.append(dict_to_instance(entry))
            else:
                dictionary.append(entry)
        return dictionary
    if type(json_un_marshal) == dict and to_obj:
        return dict_to_instance(json_un_marshal)
    return json_un_marshal


def find_type_json_properties(clazz: Any) -> Dict[str, Any]:
    json_properties = {}
    name = clazz.__qualname__
    if name in JsonPropertyMap:
        json_properties = merge_objects(False, json_properties, JsonPropertyMap[name])
    bases = parent_classes(clazz)
    for base in bases:
        json_properties = merge_objects(False, json_properties, find_type_json_properties(base))
    return None if len(json_properties) == 0 else json_properties
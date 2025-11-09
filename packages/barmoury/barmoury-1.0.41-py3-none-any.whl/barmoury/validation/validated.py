
from peewee import Database
from ..util import field_util, util
from typing import Dict, Any, Callable, List, Self
from ..api.exception import ClassUnexpectedException


ControllersValidationMap: Dict[str, Any] = {}
ValidatedDecoratorMap: Dict[str, 'Validated'] = {}


class Validation:
    message: str = None
    property_key: str = None
    validate: Callable[[Database, Any, Dict[str, Any]], bool] = None
    
    def __init__(self: Self, message: str = "", property_key: str = "", validate: Callable[[Database, Any, Dict[str, Any]], bool] = None):
        self.message = message
        self.validate = validate
        self.property_key = property_key


class Validated(field_util.MetaObject):
    kind: Any = None
    model: Any = None
    groups: List[str] = ["CREATE"]
    

def validated(**args_options: Dict[str, Any]):
    options = Validated(args_options)
    
    def validated_impl(obj):
        if field_util.is_class(obj):
            raise ClassUnexpectedException("The @validated decorator can only be applied to a method")
        ValidatedDecoratorMap[obj.__qualname__] = options
        return obj
        
    return validated_impl


def prepare_object_schema(key: str, schema: Dict[str, Any], group: str):
    if key not in ControllersValidationMap:
        ControllersValidationMap[key] = {}
    if "body" not in ControllersValidationMap[key]:
        ControllersValidationMap[key]["body"] = {}
    if group not in ControllersValidationMap[key]["body"]:
        ControllersValidationMap[key]["body"][group] = {}
        
    ControllersValidationMap[key]["body"][group] = util.merge_objects(True, ControllersValidationMap[key]["body"][group], schema)
    if "required" not in ControllersValidationMap[key]["body"][group]:
        ControllersValidationMap[key]["body"][group]["required"] = []
    if "properties" not in ControllersValidationMap[key]["body"][group]:
        ControllersValidationMap[key]["body"][group]["properties"] = {}
        

def prepare_validation_map(key: str, group: str):
    if key not in ControllersValidationMap:
        ControllersValidationMap[key] = {}
    if "__barmoury__validation_queries__" not in ControllersValidationMap[key]:
        ControllersValidationMap[key]["__barmoury__validation_queries__"] = {}
    if group not in ControllersValidationMap[key]["__barmoury__validation_queries__"]:
        ControllersValidationMap[key]["__barmoury__validation_queries__"][group] = []
        

def prepare_validation_schema(key: str, property_key: str, tipe: Any, group: str):
    prepare_object_schema(key, {}, group)
    if property_key == None:
        return
    if property_key != None and property_key not in ControllersValidationMap[key]["body"][group]["properties"]:
        ControllersValidationMap[key]["body"][group]["properties"][property_key] = {}
    if tipe != None and "type" not in ControllersValidationMap[key]["body"][group]["properties"][property_key]:
        ControllersValidationMap[key]["body"][group]["properties"][property_key]["type"] = tipe
        

def update_object_property_schema(key: str, property_key: str, tipe: Any, group: str, schema: Any):
    if property_key == None:
        return
    prepare_validation_schema(key, property_key, tipe, group)
    ControllersValidationMap[key]["body"][group]["properties"][property_key] = util.merge_objects(True, ControllersValidationMap[key]["body"][group]["properties"][property_key], schema)
        

def register_validation(key: str, group: str, validation: Validation):
    prepare_validation_map(key, group)
    ControllersValidationMap[key]["__barmoury__validation_queries__"][group].append(validation)
        

def switch_validation_schema_kind(key: str, group: str, kind: Any, body_validation_dict: Dict[str, Any] = None):
    prepare_validation_map(key, group)
    cached_validation = body_validation_dict or ControllersValidationMap[key]["body"][group]
    previously_array = cached_validation["type"] == True if "type" in cached_validation else False
    if not previously_array and kind == "array":
        cached_validation = {
            "type": "array",
            "items": cached_validation
        }
    if kind == "object":
        if previously_array:
            cached_validation = {
                "properties": cached_validation
            }
    cached_validation["type"] = kind
    if not body_validation_dict:
        ControllersValidationMap[key]["body"][group] = cached_validation
    return cached_validation
    

def get_stored_validation(group: str, obj: str):
    item = ControllersValidationMap[obj.__name__] if obj.__name__ in ControllersValidationMap else {}
    body = item["body"] if "body" in item else {}
    schema = body[group] if group in body else {}
    if len(schema) != 0:
        schema["type"] = "object"
    return schema

from ..util import field_util, util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import prepare_validation_schema, ControllersValidationMap


class ValidateEnum(field_util.MetaObject):
    name: str = None
    value: Any = None
    message: str = None
    only: List[str] = None
    excludes: List[str] = None
    groups: List[str] = ["CREATE"]
    

def validate_enum(**args_options: Dict[str, Any]):
    options = ValidateEnum(args_options)
    
    def validate_enum_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @validate_enum decorator can only be applied to a class")
        enums = []
        types = []
        key = obj.__name__
        name = options.name
        only = options.only
        value = options.value
        groups = options.groups
        excludes = options.excludes
        for ekey, value in field_util.get_enum_attributes(value).items():
            if only and (ekey not in only):
                continue
            if excludes and (ekey in excludes):
                continue
            enums.append(ekey)
            typee = util.py_type_to_schema_type(type(value.value))
            if typee not in types:
                types.append(typee)
        for group in groups:
            prepare_validation_schema(key, name, None, group)
            old_type = ControllersValidationMap[key]["body"][group]["properties"][name]["type"] if "type" in ControllersValidationMap[key]["body"][group]["properties"][name] else []
            old_enums = ControllersValidationMap[key]["body"][group]["properties"][name]["enum"] if "enum" in ControllersValidationMap[key]["body"][group]["properties"][name] else []
            ControllersValidationMap[key]["body"][group]["properties"][name]["type"] = util.merge_arrays(old_type, types)
            ControllersValidationMap[key]["body"][group]["properties"][name]["enum"] = util.merge_arrays(old_enums, enums)
        return obj
        
    return validate_enum_impl
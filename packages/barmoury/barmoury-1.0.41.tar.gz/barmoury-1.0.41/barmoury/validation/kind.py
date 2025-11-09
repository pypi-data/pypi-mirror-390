
from ..util import field_util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import prepare_validation_schema, switch_validation_schema_kind, ControllersValidationMap


class Kind(field_util.MetaObject):
    name: str = None
    value: Any = None
    message: str = None
    groups: List[str] = ["CREATE"]
    

def kind(**args_options: Dict[str, Any]):
    options = Kind(args_options)
    
    def kind_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @kind decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        value = options.value
        groups = options.groups
        for group in groups:
            prepare_validation_schema(key, name, None, group)
            if name != None:
                ControllersValidationMap[key]["body"][group]["properties"][name]["type"] = value
            else:
                switch_validation_schema_kind(key, group, value)
        return obj
        
    return kind_impl
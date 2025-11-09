
from ..util import field_util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import update_object_property_schema


class Valid(field_util.MetaObject):
    name: str = None
    value: Any = None
    message: str = None
    groups: List[str] = ["CREATE"]
    

def valid(**args_options: Dict[str, Any]):
    options = Valid(args_options)
    
    def valid_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @valid decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        value = options.value
        groups = options.groups
        for group in groups:
            update_object_property_schema(key, name, None, group, value)
        return obj
        
    return valid_impl
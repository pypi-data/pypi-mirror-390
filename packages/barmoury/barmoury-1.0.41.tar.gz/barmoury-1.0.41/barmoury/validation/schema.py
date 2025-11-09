
from ..util import field_util
from typing import Dict, Any, List
from .validated import prepare_object_schema
from ..api.exception import InvalidArgumentException


class Schema(field_util.MetaObject):
    value: Dict[str, Any] = None
    groups: List[str] = ["CREATE"]
    

def schema(**args_options: Dict[str, Any]):
    options = Schema(args_options)
    
    def validated_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @schema decorator can only be applied to a class")
        key = obj.__name__
        groups = options.groups
        schema = options.value
        for group in groups:
            prepare_object_schema(key, schema, group)
        return obj
        
    return validated_impl
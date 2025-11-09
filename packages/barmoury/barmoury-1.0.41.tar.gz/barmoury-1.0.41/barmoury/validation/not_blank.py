
from ..util import field_util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import prepare_validation_schema, ControllersValidationMap


class NotBlank(field_util.MetaObject):
    name: str = None
    message: str = None
    groups: List[str] = ["CREATE"]
    

def not_blank(**args_options: Dict[str, Any]):
    options = NotBlank(args_options)
    
    def not_blank_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @not_blank decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        groups = options.groups
        for group in groups:
            prepare_validation_schema(key, name, None, group)
            ControllersValidationMap[key]["body"][group]["properties"][name]["minLength"] = 1
        return obj
        
    return not_blank_impl
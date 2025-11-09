
from ..util import field_util
from typing import Dict, Any, List
from ..api.exception import InvalidArgumentException
from .validated import prepare_validation_schema, ControllersValidationMap


class Required(field_util.MetaObject):
    name: str = None
    kind: Any = None
    message: str = None
    groups: List[str] = ["CREATE"]
    

def required(**args_options: Dict[str, Any]):
    options = Required(args_options)
    
    def required_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @required decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        tipe = options.kind
        groups = options.groups
        for group in groups:
            prepare_validation_schema(key, name, tipe, group)
            ControllersValidationMap[key]["body"][group]["required"].append(name)
        return obj
        
    return required_impl
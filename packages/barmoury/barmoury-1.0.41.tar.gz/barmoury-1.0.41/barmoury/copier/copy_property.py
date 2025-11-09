
from typing import Dict, Any
from ..util import field_util
from ..api.exception import InvalidArgumentException


CopyPropertyMap: Dict[str, 'CopyProperty'] = {}


class CopyProperty(field_util.MetaObject):
    use_zero_value: bool = False
    exclude_privates: bool = True
    enforce_type_check: bool = False
    enable_dictionary_lookup: bool = False


def copy_property(**args_options: Dict[str, Any]):
    options = CopyProperty(args_options)
    
    def copy_property_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The entity decorator is only applicable to a class")
        CopyPropertyMap[obj.__name__] = options
        return obj
        
    return copy_property_impl
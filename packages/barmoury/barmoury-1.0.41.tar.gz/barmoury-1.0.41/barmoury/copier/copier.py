
from ..util import field_util
from typing import Sequence, Any, Tuple
from .copy_property import CopyPropertyMap, CopyProperty

class Copier:
    
    @staticmethod
    def copy[T](target: T, *sources: Sequence[T], copy_property: CopyProperty = None) -> T:
        target_name = type(target).__name__
        copy_property = CopyPropertyMap[target_name] if target_name in CopyPropertyMap else (copy_property or CopyProperty())
        attributes = field_util.get_instance_attributes(target, copy_property.exclude_privates)
        for attribute in attributes:
            Copier.copy_field(copy_property, attribute, target, *sources)
        return target
    
    @staticmethod
    def copy_field[T](copy_property: CopyProperty, attribute: Tuple[str, Any], target: T, *sources: Sequence[T]):
        name = attribute[0]
        original_value = attribute[1]
        value = Copier.find_usable_value(copy_property, attribute, *sources)
        if original_value != None and value == None:
            return
        if value == None and not (not attribute[0].__doc__ and attribute[0].__doc__.index("use_zero_value")) and not copy_property.use_zero_value:
            return
        try:
            field_util.set_class_attribute_value(target, name, value)
        except:
            pass
        
    @staticmethod
    def find_usable_value[T](copy_property: CopyProperty, attribute: Tuple[str, Any], *sources: Sequence[T]) -> Tuple[str, Any]:
        value = None
        name = attribute[0]
        latest_value = value
        original_value = attribute[1]
        for source in sources:
            if source == None or not (field_util.has_class_attribute(source,  name) or (copy_property.enable_dictionary_lookup and type(source) == dict and name in source)):
                continue
            sattribute = source[name] if type(source) == dict else field_util.get_class_attribute_value(source, name)
            if copy_property.enforce_type_check and type(original_value) != type(sattribute):
                continue
            latest_value = sattribute
            if latest_value != None:
                break
        return latest_value

import re
import inspect
from enum import Enum
from typing import Dict, Any, Tuple, List, Callable


class MetaObject:
    def __init__(self, d=None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)


def is_class(obj, deep=False):
    return inspect.isclass(type(obj) if deep else obj) and hasattr(obj, "__dict__")


def get_method_class(fun: Callable):
    for cls in inspect.getmro(fun.__class__):
        if fun.__name__ in cls.__dict__: 
            return cls
    return None


def has_class_attribute[T](instance: T, name: str) -> bool:
    return hasattr(instance, name)


def get_class_attribute_value[T](instance: T, name: str) -> Any:
    return getattr(instance, name)


def set_class_attribute_value[T](instance: T, name: str, value: Any):
    setattr(instance, name, value)


def get_value[T](instance: T, name: str, fallback: Any = None) -> bool:
    if is_class(instance):
        return get_class_attribute_value(instance, name)
    if type(instance) == dict and name in instance:
        return instance[name]
    return fallback


def dict_to_instance(dictionary: Dict):
    return MetaObject(dictionary)


def field_value_or(clazz, field, fallback = None):
    try:
        if not hasattr(clazz, field):
            return fallback
        return getattr(clazz, field)
    except:
        return fallback


def get_type_annotations[T](typee: T, exclude_privates: bool = False) -> List[Tuple[str, Any]]:
    attributes = set()
    __annotations__ = typee.__annotations__ if has_class_attribute(typee, "__annotations__") else {}
    for key, value in __annotations__.items():
        attributes.add((key, value))
    for base in typee.__bases__:
        if base == object: break
        attributes = attributes.union(get_type_annotations(base, exclude_privates))
    return list([a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__')) and (not exclude_privates or not a[0].startswith('_'))])


def get_type_attributes[T](instance: T, exclude_privates: bool = False) -> List[Tuple[str, Any]]:
    attributes = []
    for key, _ in get_type_annotations(type(instance), exclude_privates):
        attributes.append((key, field_value_or(instance, key)))
    return attributes


def get_instance_attributes[T](instance: T, exclude_privates: bool = False) -> List[Tuple[str, Any]]:
    attributes = []
    attributes_map = {}
    try:
        attributes = inspect.getmembers(instance, lambda a:not(inspect.isroutine(a)))
    except:
        __dict__ = instance.__dict__ if has_class_attribute(instance, "__dict__") else {}
        __data__ = __dict__['__data__'] if '__data__' in __dict__ else {}
        for key, value in __data__.items():
            attributes_map[key] = value
        for key, value in attributes_map.items():
            attributes.append((key, value))
    attributes += get_type_attributes(instance, exclude_privates)
    del attributes_map
    return [a for a in attributes if not(a[0].startswith('__') and a[0].endswith('__')) and (not exclude_privates or not a[0].startswith('_'))]


def get_instance_method(clazz: Any, fun_name: str):
    if not has_class_attribute(clazz, fun_name):
        return None
    fun = get_class_attribute_value(clazz, fun_name)
    if type(fun).__name__ != "method":
        return None
    return fun


def traverse_declared_methods(clazz: Any, fn: Callable[[str, Any], Any], sort: Callable[[List[str]], List[str]] = None):
    fun_names: List[str] = []
    for fun_name in dir(type(clazz)):
        if not fun_name.startswith('__'):
            fun_names.append(fun_name)
    if sort != None:
        fun_names = sort(fun_names)
    for fun_name in fun_names:
        value = getattr(clazz, fun_name)
        if type(value).__name__ != "method":
            continue
        fn(fun_name, value)
    

def method_signature(method: Callable):
    return inspect.signature(method)
    

def parent_classes(clazz: Callable):
    return clazz.__bases__


def get_enum_attributes(ehnum: Enum) -> Dict[str, Enum]:
    return ehnum.__dict__["_member_map_"]


def method_absolute_name(method: Callable):
    return str(method).strip()

def to_snake_case(name: str):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

def to_camel_case(name: str):
    name = 'snake_case_name'
    return ''.join(word.title() for word in name.split('_'))
    
def get_field_column_name(name: str, snake_case: bool):
    return to_snake_case(name) if snake_case else name
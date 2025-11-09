
from enum import Enum
from typing import Dict, Any, List
from ..util import field_util, util
from ..api.exception import InvalidArgumentException


FieldsRequestParamFilterMap: Dict[str, Dict[str, List['RequestParamFilter']]] = {}


class RequestParamFilterOperator(str, Enum):
    
    EQ = "EQ"
    GT = "GT"
    LT = "LT"
    NE = "NE"
    IN = "IN"
    NONE = "NONE"
    LIKE = "LIKE"
    ILIKE = "ILIKE"
    GT_EQ = "GT_EQ"
    LT_EQ = "LT_EQ"
    RANGE = "RANGE"
    NOT_IN = "NOT_IN"
    ENTITY = "ENTITY"
    BETWEEN = "BETWEEN"
    NOT_LIKE = "NOT_LIKE"
    CONTAINS = "CONTAINS"
    NOT_ILIKE = "NOT_ILIKE"
    OBJECT_EQ = "OBJECT_EQ"
    OBJECT_NE = "OBJECT_NE"
    ENDS_WITH = "ENDS_WITH"
    NOT_BETWEEN = "NOT_BETWEEN"
    STARTS_WITH = "STARTS_WITH"
    OBJECT_LIKE = "OBJECT_LIKE"
    NOT_CONTAINS = "NOT_CONTAINS"
    OBJECT_STR_EQ = "OBJECT_STR_EQ"
    OBJECT_STR_NE = "OBJECT_STR_NE"
    SENSITIVE_LIKE = "SENSITIVE_LIKE"
    OBJECT_NOT_LIKE = "OBJECT_NOT_LIKE"
    OBJECT_CONTAINS = "OBJECT_CONTAINS"
    OBJECT_ENDS_WITH = "OBJECT_ENDS_WITH"
    SENSITIVE_NOT_LIKE = "SENSITIVE_NOT_LIKE"
    OBJECT_STARTS_WITH = "OBJECT_STARTS_WITH"
    OBJECT_NOT_CONTAINS = "OBJECT_NOT_CONTAINS"
    OBJECT_STR_ENDS_WITH = "OBJECT_STR_ENDS_WITH"
    SENSITIVE_OBJECT_LIKE = "SENSITIVE_OBJECT_LIKE"
    OBJECT_STR_STARTS_WITH = "OBJECT_STR_STARTS_WITH"


class RequestParamFilter(field_util.MetaObject):
    name: str = None
    column: str = None
    aliases: List[str] = None
    always_query: bool = None
    boolean_to_int: bool = None
    accept_camel_case: bool = None
    column_is_camel_case: bool = None
    multi_filter_separator: str = None
    operator: 'RequestParamFilter.Operator' = None
    column_object_fields_is_camel_case: bool = None
    
    Operator: RequestParamFilterOperator = RequestParamFilterOperator


def request_param_filter(**args_options: Dict[str, Any]):
    options = RequestParamFilter(args_options)
    
    def request_param_filter_impl(obj):
        if not field_util.is_class(obj):
            raise InvalidArgumentException("The @request_param_filter decorator can only be applied to a class")
        key = obj.__name__
        name = options.name
        if key not in FieldsRequestParamFilterMap:
            FieldsRequestParamFilterMap[key] = {}
        existing_value = FieldsRequestParamFilterMap[key][name] if name in FieldsRequestParamFilterMap[key] else []
        existing_value.append(barmoury_object_internal_set_param_filter_attrs_defaults(options))
        FieldsRequestParamFilterMap[key][name] = util.merge_arrays(existing_value)
        return obj
        
    return request_param_filter_impl


def barmoury_object_internal_set_param_filter_attrs_defaults(attr: RequestParamFilter):
    if attr.always_query == None: attr.always_query = False
    if attr.boolean_to_int == None: attr.boolean_to_int = False
    if attr.accept_camel_case == None: attr.accept_camel_case = False
    if attr.column_is_camel_case == None: attr.column_is_camel_case = False
    if attr.operator == None: attr.operator = RequestParamFilter.Operator.EQ
    if attr.multi_filter_separator == None: attr.multi_filter_separator = "__"
    if attr.column_object_fields_is_camel_case == None: attr.column_object_fields_is_camel_case = False
    return attr


def find_request_param_filter(obj, name):
    request_param_filters = set()
    key = obj.__name__
    for base in obj.__bases__:
        if base == object: break
        request_param_filters = request_param_filters.union(find_request_param_filter(base, name))
    if key in FieldsRequestParamFilterMap and name in FieldsRequestParamFilterMap[key]:
        request_param_filters = request_param_filters.union(FieldsRequestParamFilterMap[key][name])
    return list(request_param_filters)
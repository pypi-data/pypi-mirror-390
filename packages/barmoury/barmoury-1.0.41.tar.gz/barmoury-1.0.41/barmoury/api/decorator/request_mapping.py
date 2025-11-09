
from ...util import field_util
from ..enum import RequestMethod
from ..model import Model, Request
from typing import Any, Dict, List


ControllersRequestMap: Dict[str, 'RequestMapping'] = {}


class RequestMapping(field_util.MetaObject):
    value: str = ""
    model: Model = None
    request: Request = None
    body_schema: Dict[str, Any] = None
    query_schema: Dict[str, Any] = None
    params_schema: Dict[str, Any] = None
    headers_schema: Dict[str, Any] = None
    method: RequestMethod | List[RequestMethod] = RequestMethod.GET


def request_mapping(**args_options: Dict[str, Any]):
    options = RequestMapping(args_options)
    
    def request_mapping_impl(obj):
        is_class = field_util.is_class(obj)
        ControllersRequestMap[obj.__name__ if is_class else obj.__qualname__] = options
        return obj
    
    return request_mapping_impl


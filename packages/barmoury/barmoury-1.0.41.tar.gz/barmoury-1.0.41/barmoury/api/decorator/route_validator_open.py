
from ...util import field_util
from typing import List, Dict, Any
from ..exception import InvalidArgumentException
from .request_mapping import ControllersRequestMap


BarmouryRouteValidatorOpenUrlPatternsKeyMap: Dict[str, str] = {}
BarmouryRouteValidatorOpenUrlPatternsMap: Dict[str, List[Any]] = {}
BarmouryGlobalRouteValidatorOpenUrlPatterns: str = "__barmoury_global_route_validator_open_url_patterns__"


def resolve_route_validator_open_route_route(key: str, value: Any):
    if key not in BarmouryRouteValidatorOpenUrlPatternsKeyMap:
        return
    id = BarmouryRouteValidatorOpenUrlPatternsKeyMap[key]
    del BarmouryRouteValidatorOpenUrlPatternsKeyMap[key]
    if id not in BarmouryRouteValidatorOpenUrlPatternsMap:
        BarmouryRouteValidatorOpenUrlPatternsMap[id] = []
    BarmouryRouteValidatorOpenUrlPatternsMap[id].append(value)


def register_route_validator_open_route(obj, id: str = BarmouryGlobalRouteValidatorOpenUrlPatterns):
    if field_util.is_class(obj):
        raise InvalidArgumentException("The @route_validator_open decorator can only be applied to a method")
    BarmouryRouteValidatorOpenUrlPatternsKeyMap[obj.__hash__()] = id
    return obj


def route_validator_open(id: str = BarmouryGlobalRouteValidatorOpenUrlPatterns):
    
    def route_validator_open_impl(obj):
        return register_route_validator_open_route(obj, id)
    
    return route_validator_open_impl
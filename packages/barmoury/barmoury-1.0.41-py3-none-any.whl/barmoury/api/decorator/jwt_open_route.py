
from ...util import field_util
from typing import List, Dict, Any
from ..exception import InvalidArgumentException


BarmouryJwtOpenUrlPatternsKeyMap: Dict[str, str] = {}
BarmouryJwtOpenUrlPatternsMap: Dict[str, List[Any]] = {}
BarmouryGlobalJwtOpenUrlPatterns: str = "__barmoury_global_jwt_open_url_patterns__"


def resolve_jwt_open_route_route(key: str, value: Any):
    if key not in BarmouryJwtOpenUrlPatternsKeyMap:
        return
    id = BarmouryJwtOpenUrlPatternsKeyMap[key]
    del BarmouryJwtOpenUrlPatternsKeyMap[key]
    if id not in BarmouryJwtOpenUrlPatternsMap:
        BarmouryJwtOpenUrlPatternsMap[id] = []
    BarmouryJwtOpenUrlPatternsMap[id].append(value)


def register_jwt_open_route(obj, id: str = BarmouryGlobalJwtOpenUrlPatterns):
    if field_util.is_class(obj):
        raise InvalidArgumentException("The @jwt_open decorator can only be applied to a method")
    BarmouryJwtOpenUrlPatternsKeyMap[obj.__hash__()] = id
    return obj


def jwt_open(id: str = BarmouryGlobalJwtOpenUrlPatterns):
    
    def jwt_open_impl(obj):
        return register_jwt_open_route(obj, id)
    
    return jwt_open_impl
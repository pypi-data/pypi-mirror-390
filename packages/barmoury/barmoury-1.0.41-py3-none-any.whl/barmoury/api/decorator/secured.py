

from typing import List, Dict

RequestHandlerSecuredAccessMap: Dict[str, List[str]] = {}

def secured(accesses: List[str]):
    def secured_impl(obj):
        RequestHandlerSecuredAccessMap[obj.__qualname__] = accesses
        return obj
    return secured_impl


from .iroute import *
from ...util import util
from ..exception import *
from ..enum import RequestMethod
from typing import Callable, Self, List
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette, Request as StarletteRequest
from ..decorator import BarmouryGlobalRouteValidatorOpenUrlPatterns, BarmouryRouteValidatorOpenUrlPatternsMap


_mapped_route_validators = {}


class RouteValidator:
    id: str = None
    prefix: str = ""
    routes: List[Route] = []
    valid: Callable[[StarletteRequest], bool] = None
    
    def __init__(self: Self, prefix: str = "", routes: List[Route] = [], valid: Callable[[StarletteRequest], bool] = None):
        self.valid = valid
        self.prefix = prefix
        self.routes = routes


class BarmouryRouteValidatorMiddleware(BaseHTTPMiddleware):

    # TODO check for path params request
    async def dispatch(self: Self, request: StarletteRequest, call_next: Callable):
        valid = None
        method = request.method
        route = request.url.path
        global _mapped_route_validators
        if f"{method}<=#=>{route}" in _mapped_route_validators:
            valid = _mapped_route_validators[f"{method}<=#=>{route}"]
        if valid == None and f"ANY<=#=>{route}" in _mapped_route_validators:
            valid = _mapped_route_validators[f"ANY<=#=>{route}"]
        if valid != None and not valid(request):
            raise RouteValidatorException("Validation failed for the request")
        return await call_next(request)


_registered_route_validators = False
def register_route_validators(app: Starlette, route_validators: List[RouteValidator]):
    global _registered_route_validators
    if _registered_route_validators:
        return
    _registered_route_validators = True
    for route_validator in route_validators:
        prefix = route_validator.prefix or ""
        if prefix.endswith("/"): prefix = prefix[:-1]
        if BarmouryGlobalRouteValidatorOpenUrlPatterns in BarmouryRouteValidatorOpenUrlPatternsMap:
            route_validator.routes = util.merge_arrays(route_validator.routes, BarmouryRouteValidatorOpenUrlPatternsMap[BarmouryGlobalRouteValidatorOpenUrlPatterns])
        if route_validator.id != None and route_validator.id in BarmouryRouteValidatorOpenUrlPatternsMap:
            route_validator.routes = util.merge_arrays(route_validator.routes, BarmouryRouteValidatorOpenUrlPatternsMap[route_validator.id])
        for route in route_validator.routes:
            router = Route(method=RequestMethod.ANY) if route == None else route
            path = util.replace_by_regex(f"{prefix}{router.route}", r"{([\w])+}", r"$1")
            key = f"{router.method.value}<=#=>{path}"
            _mapped_route_validators[key] = route_validator.valid
    app.add_middleware(BarmouryRouteValidatorMiddleware)


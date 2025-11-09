
import os
import jsonschema
from .route import Route
from ..controller import Controller
from ...util import field_util, util
from peewee import Database, MySQLDatabase
from typing import List, Any, Self, Dict, Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette, Request as StarletteRequest
from ..exception import ValidationException, ConstraintValidationException
from ...validation import ValidatedDecoratorMap, ControllersValidationMap, Validation, switch_validation_schema_kind
from ..decorator import RequestMapping, ControllersRequestMap, resolve_jwt_open_route_route, resolve_route_validator_open_route_route, BarmouryJwtOpenUrlPatternsKeyMap

_Db: Database = None
RouteEntries: List[str] = []
ControllersValidationSchemaMap: Dict[str, Dict[str, Any]] = {}
ControllersValidationQueriesMap: Dict[str, List[Validation]] = {}

# TODO defer to end
class ControllerValidationMiddleware(BaseHTTPMiddleware):
    
    async def dispatch(self: Self, request: StarletteRequest, call_next: Callable):
        key = util.str_format("{}__{}", request.method, request.url.path)
        schema_match = util.pattern_match_entry(ControllersValidationSchemaMap, key, "/")
        if schema_match != None:
            body = await request.json()
            schema = ControllersValidationSchemaMap[schema_match["match"]]
            validator = jsonschema.Draft7Validator(schema)
            errors: List[jsonschema.ValidationError] = validator.iter_errors(body)
            error_lines = ""
            for error in errors:
                error_lines += ((error.json_path + ": ") + str(error).split("\n")[0] + "\n")
            if error_lines != "":
                raise ValidationException(error_lines.strip())
        validation_match = util.pattern_match_entry(ControllersValidationQueriesMap, key, "/")
        if validation_match != None and len(validation_match["value"]) > 0:
            validation_queries = validation_match["value"]
            body = (await request.json()) or {}
            path_params = util.extract_pattern_values(validation_match["match"], key)
            id = path_params["id"] if "id" in path_params else None
            for validation_query in validation_queries:
                if (validation_query.property_key not in body or body[validation_query.property_key] == None) and validation_query.property_key != "__class__":
                    continue
                value = body if validation_query.property_key == "__class__" else body[validation_query.property_key]
                result = await validation_query.validate(_Db, value, { "body": body, "resource_id": id })
                if not result:
                    raise ConstraintValidationException(util.replace_by_regex((validation_query.message or ""), r"{value}+", str(value)))
        return await call_next(request)
        

class RouterOption:
    
    prefix: str = ""
    db: Database = None
    bacuator: Any = None
    init_db: bool = True
    app: Starlette = None
    log_level: Any = None
    
    def __init__(self: Self, prefix: str = "", db: Database = None, log_level: Any = None, bacuator: Any = None, init_db: bool = True):
        self.db = db
        self.prefix = prefix
        self.init_db = init_db
        self.bacuator = bacuator
        self.log_level = log_level


def register_controllers(app: Starlette, opts: RouterOption, controllers: List[Controller[Any, Any]]) -> RouterOption:
    global _Db
    opts.app = app
    if opts.prefix == None:
        opts.prefix = ""
    if opts.prefix.endswith("/"):
        opts.prefix = opts.prefix[:-1]
    if opts.db == None and opts.init_db:
        opts.db = _create_default_peewee_db_connection()
        opts.db.connect()
    _Db = opts.db
    if opts.bacuator != None:
        print("TO SETUP BACUATOR HERE", opts.bacuator)
    for controller in controllers:
        routes = []
        _routes = _registerController(opts, controller)
        for _route in _routes:
            if '{' not in _route["path"]:
                routes.insert(0, _route)
            else:
                routes.append(_route)
        for route in routes:
            app.add_route(path=route["path"], route=route["route"], methods=route["methods"])
    app.add_middleware(ControllerValidationMiddleware)
    return opts

def _registerController(opts: RouterOption, controller: Controller[Any, Any]) -> List[Dict[str, Any]]:
    controller_key = type(controller).__name__
    request_mapping = ControllersRequestMap[controller_key] if controller_key in ControllersRequestMap else RequestMapping()
    return _registerRoutes(opts, controller, request_mapping)

from starlette.responses import JSONResponse
async def homepage(request):
    return JSONResponse({'hello': 'world'})

def _registerRoutes(opts: RouterOption, controller: Controller[Any, Any], controller_request_mapping: RequestMapping) -> List[Dict[str, Any]]:
    routes = []
    routes_set = []
    controller_route = opts.prefix + (controller_request_mapping.value or "")
    
    controller_type = type(controller)
    setup = field_util.get_instance_method(controller, "setup")
    if setup != None:
        controller.setup(opts, controller_type.__name__.replace("Controller", ""), controller_request_mapping.model, controller_request_mapping.request)

    def walk_method(fun_name, func):
        if fun_name == "setup":
            return
        method_key = func.__qualname__
        method_hash = field_util.get_class_attribute_value(controller_type, fun_name).__hash__()
        if method_key not in ControllersRequestMap:
            return
        request_mapping = ControllersRequestMap[method_key]
        method = request_mapping.method
        route = controller_route + (request_mapping.value or "")
        route_path = util.str_format("{}__{}", method.value, route)
        if route_path in routes_set:
            return
        RouteEntries.append(route)
        routes_set.append(route_path)
        if method_key in ValidatedDecoratorMap:
            body_validation_dict = {}
            validated = ValidatedDecoratorMap[method_key]
            key = (validated.model or request_mapping.request or controller_request_mapping.request).__name__
            if key in ControllersValidationMap:
                for group in validated.groups:
                    if group not in ControllersValidationMap[key]["body"]:
                        continue
                    schema = ControllersValidationMap[key]["body"][group]
                    body_validation_dict = util.merge_objects(True, body_validation_dict, schema)
                if "__barmoury__validation_queries__" in ControllersValidationMap[key]:
                    if route_path not in ControllersValidationQueriesMap:
                        ControllersValidationQueriesMap[route_path] = []
                    for group in validated.groups:
                        if group not in ControllersValidationMap[key]["__barmoury__validation_queries__"]:
                            continue
                        validation_queries = ControllersValidationMap[key]["__barmoury__validation_queries__"][group]
                        ControllersValidationQueriesMap[route_path] = util.merge_arrays(ControllersValidationQueriesMap[route_path], validation_queries)
            if request_mapping.body_schema != None:
               body_validation_dict =  util.merge_objects(True, body_validation_dict, request_mapping.body_schema)
            if validated.kind != None and "type" not in body_validation_dict:
                body_validation_dict = switch_validation_schema_kind(key, group, validated.kind, body_validation_dict)
            ControllersValidationSchemaMap[route_path] = body_validation_dict
        route_obj = Route(method=method, route=route[len(opts.prefix):])
        resolve_jwt_open_route_route(method_hash, route_obj)
        resolve_route_validator_open_route_route(method_hash, route_obj)
        async def wrapped_relay_func(request: StarletteRequest):
            return await func(request)
        routes.append({ "path": route, "methods": method if (type(method) == list) else [method], "route": wrapped_relay_func})
        
    field_util.traverse_declared_methods(controller, walk_method)
    return routes


def _create_default_peewee_db_connection():
   return MySQLDatabase(os.getenv("DATABASE_SCHEMA"), 
                         user=os.getenv("DATABASE_USERNAME"), 
                         password=os.getenv("DATABASE_PASSWORD"), 
                         host=os.getenv("DATABASE_HOST"), 
                         port=int(os.getenv("DATABASE_PORT") or "3306"))
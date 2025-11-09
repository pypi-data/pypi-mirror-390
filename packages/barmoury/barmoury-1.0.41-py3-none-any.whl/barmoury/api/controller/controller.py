

from ...util import *
from enum import Enum
from ..exception import *
from ...eloquent import *
from typing import Self, Any, List
from ...validation import validated
from ..model import Model, Request, ApiResponse
from ..decorator import request_mapping, RequestMethod
from starlette.applications import Starlette, Request as StarletteRequest

class Controller[T1, T2]:

    _model: Model = None
    app: Starlette = None
    pageable: bool = False
    fine_name: str = "model"
    _request: Request = None
    query_armoury: QueryArmoury = None
    store_asynchronously: bool = False
    update_asynchronously: bool = False
    delete_asynchronously: bool = False

    NO_RESOURCE_FORMAT_STRING = "No {} found with the specified id {}"
    ACCESS_DENIED = "Access denied. You do not have the required role to access this endpoint"

    def setup(self: Self, opts: Any, name: str = "", model: Model = None, request: Request = None):
        self.app = opts.app
        self._model = model
        self._request = request
        self.query_armoury = QueryArmoury(opts.db)
        self.fine_name = name or type(T1).__name__
        
    async def pre_response(self: Self, entity: T1):
        pass
        
    async def pre_responses(self: Self, entities: List[T1]):
        for entity in entities:
            await self.pre_response(entity)
            
    async def resolve_sub_entities(self: Self) -> bool:
        return True
            
    async def skip_recursive_sub_entities(self: Self) -> bool:
        return True
            
    async def pre_query(self: Self, request: StarletteRequest, authentication: Any) -> StarletteRequest:
        return request
            
    async def pre_create(self: Self, request: StarletteRequest, authentication: Any, entity: T1, entity_request: T2):
        pass
            
    async def post_create(self: Self, request: StarletteRequest, authentication: Any, entity: T1):
        pass
            
    async def pre_update(self: Self, request: StarletteRequest, authentication: Any, entity: T1, entity_request: T2):
        pass
            
    async def post_update(self: Self, request: StarletteRequest, authentication: Any, previous_entity: T1, entity: T1):
        pass
            
    async def pre_delete(self: Self, request: StarletteRequest, authentication: Any, entity: T1, id: Any):
        pass
            
    async def post_delete(self: Self, request: StarletteRequest, authentication: Any, entity: T1):
        pass
            
    async def on_asynchronous_error(self: Self, type: str, entity: Any, exception: Any):
        pass
            
    async def handle_sql_injection_query(self: Self, request: StarletteRequest, authentication: Any):
        raise AccessDeniedException("SQL injection attack detected")
            
    async def sanitize_and_get_request_parameters(self: Self, request: StarletteRequest, authentication: Any):
        if QueryArmoury.BARMOURY_RAW_SQL_PARAMETER_KEY in request.query_params:
            await self.handle_sql_injection_query(request, authentication)
        return request
            
    async def process_response[T](self: Self, status_code: int = 200, data: T = None, message: str = "", secondary_data: Any = None, api_response: ApiResponse = None):
        if api_response == None:
            api_response = ApiResponse(message=message, data=data, secondary_data=secondary_data)
        return ApiResponse.to_json_response(api_response, status_code)
            
    async def get_resource_by_id(self: Self, id: Any, authentication: Any = None) -> T1:
        return await self.query_armoury.get_resource_by_id(self._model, id, util.str_format(self.NO_RESOURCE_FORMAT_STRING, self.fine_name, id))
            
    async def post_get_resource_by_id(self: Self, request: StarletteRequest, authentication: Any, entity: T1):
        pass
            
    async def validate_before_commit(self: Self, entity: T1) -> str:
        if entity == None:
            return "Invalid entity"
        return None
            
    async def should_not_honour_method(self: Self, route_method: 'RouteMethod') -> bool:
        return route_method == None
            
    async def get_route_method_roles(self: Self, route_method: 'RouteMethod') -> List[str]:
        return []
            
    async def validate_route_access(self: Self, request: StarletteRequest, route_method: 'RouteMethod', err_message: str):
        if await self.should_not_honour_method(route_method):
            raise RouteMethodNotSupportedException(err_message)
        roles = await self.get_route_method_roles(route_method)
        if len(roles) > 0 and set(request.state.authorities_values).isdisjoint(roles):
            raise AccessDeniedException(Controller.ACCESS_DENIED)
            
    async def inject_update_field_id(self: Self, request: StarletteRequest, resource_request: T2) -> T2:
        if not (request.method == "POST" or request.method == "PUT" or request.method == "PATCH"):
            return resource_request
        id = request.path_params.get("id")
        resource_request.___BARMOURY_UPDATE_ENTITY_ID___ = id
        return resource_request
            
    async def resolve_request_payload(self: Self, authentication: Any, resource_request: T2) -> T1:
        result = self._model().resolve(resource_request, self.query_armoury, authentication)
        return result
    
    def get_request_user(_: Self, request: StarletteRequest):
        if hasattr(request.state, "user"):
            return request.state.user
        return None
    
    @request_mapping(value="/stat", method=RequestMethod.GET)
    async def stat(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.STAT, "The GET '**/stat' route is not supported for this resource")
        return await self.process_response(200, "Hello stat world!!!")
    
    @request_mapping(method=RequestMethod.GET)
    async def index(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.INDEX, "The GET '**/' route is not supported for this resource")
        authentication = self.get_request_user(request)
        request = await self.pre_query(await self.sanitize_and_get_request_parameters(request, authentication), authentication)
        resources = await self.query_armoury.page_query(request, self._model, await self.resolve_sub_entities(), self.pageable)
        await self.pre_responses(resources["content"] if "content" in resources else resources)
        return await self.process_response(200, resources, f"{self.fine_name} list fetched successfully")
    
    @validated(kind="object")
    @request_mapping(method=RequestMethod.POST)
    async def store(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.STORE, "The POST '**/' route is not supported for this resource")
        authentication = self.get_request_user(request)
        request_payload: Request = self._request(await request.json())
        resource: Model = await self.resolve_request_payload(authentication, request_payload)
        await self.pre_create(request, authentication, resource, request_payload)
        msg = await self.validate_before_commit(resource)
        if msg != None:
            raise InvalidArgumentException(msg)
        if self.store_asynchronously:
            def async_procedure():
                try:
                    resource.save()
                    self.post_create(request, authentication, resource)
                except Exception as ex:
                    self.on_asynchronous_error("Store", resource, ex)
            util.execute_in_thread(async_procedure)
            return await self.process_response(202, None, f"{self.fine_name} is being created")
        resource.save()
        await self.post_create(request, authentication, resource)
        await self.pre_response(resource)
        return await self.process_response(200, resource, f"{self.fine_name} created successfully")
    
    @validated(kind="array")
    @request_mapping(value="/multiple", method=RequestMethod.POST)
    async def store_multiple(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.STORE_MULTIPLE, "The POST '**/multiple' route is not supported for this resource")
        resources = []
        authentication = self.get_request_user(request)
        for request_payload in (await request.json()):
            request_payload: Request = self._request(request_payload)
            resource: Model = await self.resolve_request_payload(authentication, request_payload)
            await self.pre_create(request, authentication, resource, request_payload)
            msg = await self.validate_before_commit(resource)
            if msg != None:
                raise InvalidArgumentException(msg)
            if self.store_asynchronously:
                def async_procedure():
                    try:
                        resource.save()
                        self.post_create(request, authentication, resource)
                    except Exception as ex:
                        self.on_asynchronous_error("Store", resource, ex)
                util.execute_in_thread(async_procedure)
                continue
            resource.save(resource)
            await self.post_create(request, authentication, resource)
            await self.pre_response(resource)
            resources.append(resource)
        if self.store_asynchronously:
            return await self.process_response(202, None, f"{self.fine_name}s are being created")
        return await self.process_response(200, resources, f"{self.fine_name}s created successfully")
    
    @request_mapping(value="/{id}", method=RequestMethod.GET)
    async def show(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.SHOW, "The GET '**/:id' route is not supported for this resource")
        id = request.path_params["id"]
        authentication = self.get_request_user(request)
        resource: Model = await self.get_resource_by_id(id, authentication)
        await self.post_get_resource_by_id(request, authentication, resource)
        await self.pre_response(resource)
        return await self.process_response(200, resource, f"{self.fine_name} fetch successfully")
    
    @validated(groups=["UPDATE"])
    @request_mapping(value="/{id}", method=RequestMethod.PATCH)
    async def update(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.UPDATE, "The PATCH '**/:id' route is not supported for this resource")
        id = request.path_params["id"]
        authentication = self.get_request_user(request)
        request_payload: Request = self._request(await request.json())
        prev_resource: Model = await self.get_resource_by_id(id, authentication)
        await self.post_get_resource_by_id(request, authentication, prev_resource)
        resource = prev_resource.resolve(request_payload, self.query_armoury, authentication)
        await self.pre_update(request, authentication, resource, request_payload)
        msg = await self.validate_before_commit(resource)
        if msg != None:
            raise InvalidArgumentException(msg)
        if self.update_asynchronously:
            def async_procedure():
                try:
                    resource.save()
                    self.post_update(request, authentication, prev_resource, resource)
                except Exception as ex:
                    self.on_asynchronous_error("Update", resource, ex)
            util.execute_in_thread(async_procedure)
            return await self.process_response(202, None, f"{self.fine_name} is being updated")
        resource.save()
        await self.post_update(request, authentication, prev_resource, resource)
        await self.pre_response(resource)
        return await self.process_response(200, resource, f"{self.fine_name} updated successfully")
    
    @request_mapping(value="/{id}", method=RequestMethod.DELETE)
    async def destroy(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.DESTROY, "The DELETE '**/:id' route is not supported for this resource")
        id = request.path_params["id"]
        authentication = self.get_request_user(request)
        resource: Model = await self.get_resource_by_id(id, authentication)
        await self.post_get_resource_by_id(request, authentication, resource)
        await self.pre_delete(request, authentication, resource, id)
        if self.delete_asynchronously:
            def async_procedure():
                try:
                    resource.delete_instance()
                    self.post_delete(request, authentication, resource)
                except Exception as ex:
                    self.on_asynchronous_error("Delete", resource, ex)
            util.execute_in_thread(async_procedure)
            return await self.process_response(202, None, f"{self.fine_name} is being deleted")
        resource.delete_instance()
        await self.post_delete(request, authentication, resource)
        await self.pre_response(resource)
        return ApiResponse.no_content()
    
    @validated()
    @request_mapping(value="/multiple", method=RequestMethod.DELETE, body_schema={ "type": "array" })
    async def destroy_multiple(self: Self, request: StarletteRequest):
        await self.validate_route_access(request, RouteMethod.DESTROY_MULTIPLE, "The DELETE '**/multiple' route is not supported for this resource")
        authentication = self.get_request_user(request)
        resources: List[Model] = []
        for id in (await request.json()):
            resources.append(await self.get_resource_by_id(id, authentication))
        for resource in resources:
            await self.post_get_resource_by_id(request, authentication, resource)
            await self.pre_delete(request, authentication, resource, id)
            if self.delete_asynchronously:
                def async_procedure():
                    try:
                        resource.delete_instance()
                        self.post_delete(request, authentication, resource)
                    except Exception as ex:
                        self.on_asynchronous_error("Delete", resource, ex)
                util.execute_in_thread(async_procedure)
                continue
            resource.delete_instance()
            await self.post_delete(request, authentication, resource)
            await self.pre_response(resource)
        if self.delete_asynchronously:
            return await self.process_response(202, None, f"{self.fine_name}s are being deleted")
        return ApiResponse.no_content()
    

class RouteMethod(str, Enum):
    STAT = "STAT"
    SHOW = "SHOW"
    INDEX = "INDEX"
    STORE = "STORE"
    UPDATE = "UPDATE"
    DESTROY = "DESTROY"
    STORE_MULTIPLE = "STORE_MULTIPLE"
    DESTROY_MULTIPLE = "DESTROY_MULTIPLE"
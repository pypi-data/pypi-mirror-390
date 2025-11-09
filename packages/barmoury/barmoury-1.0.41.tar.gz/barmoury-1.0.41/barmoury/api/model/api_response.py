
from ...util import *
from typing import List, Self, Any
from starlette.responses import Response, JSONResponse

class ApiResponse[T]:
    data: T = None
    message: str = ""
    success: bool = True
    errors: List[str] = None
    secondary_data: Any = None
    
    def __init__(self: Self, data: T = None, message: str = "", success: bool = True, errors: List[str] = None, secondary_data: Any = None):
        self.data = data
        self.errors = errors
        self.success = success
        self.message = message
        self.secondary_data = secondary_data
        
    @staticmethod
    def to_json_response(api_response: 'ApiResponse', status_code: int = 200):
        dictionary = { "success": api_response.success, "message": api_response.message }
        if api_response.data != None:
            dictionary["data"] = json_mapper.to_json(api_response.data, True)
        if api_response.errors != None:
            dictionary["errors"] = json_mapper.to_json(api_response.errors, True)
        if api_response.secondary_data != None:
            dictionary["secondary_data"] = json_mapper.to_json(api_response.secondary_data, True)
        return JSONResponse(dictionary, status_code=status_code)

    @staticmethod
    def build(status_code: int = 200, data: T = None, message: str = "", success: bool = True, secondary_data: Any = None) -> JSONResponse:
        return ApiResponse.to_json_response(ApiResponse(data=data, success=success, message=message, secondary_data=secondary_data), status_code)
        
    @staticmethod
    def buildError(status_code: int = 500, message: str = "", success: bool = False, errors: List[str] = [], secondary_data: Any = None) -> JSONResponse:
        if message == "" or message == None and len(errors) > 0:
            message = errors[0]
        return ApiResponse.to_json_response(ApiResponse(errors=errors, success=success, message=message, secondary_data=secondary_data), status_code)
        
    @staticmethod
    def no_content():
        return Response(status_code=204)

from typing import Self
from starlette.exceptions import HTTPException
from starlette.responses import JSONResponse, HTMLResponse
from starlette.applications import Starlette, Request
from barmoury.api import request_mapping, register_error_advisers, error_advice
from barmoury.api import register_controllers, RouterOption, Controller, ErrorAdviserOption, ErrorAdviser

@request_mapping(value="/user")
class TestController(Controller):

    @request_mapping(value="/index/{id}")
    def sindex(self: Self, request: Request):
        return JSONResponse({'hello': 'worlder'})
    
class CustomErrorAdviser:
    
    @error_advice(status_code=500, error_names=["___UnknownError___"])
    def internal_server_error(exception: Exception, opts):
        return JSONResponse({'hello': str(exception)})

app = Starlette(debug=False, routes=[])
register_error_advisers(app, ErrorAdviserOption(), [
    ErrorAdviser(),
    CustomErrorAdviser()
])
register_controllers(app, RouterOption(), [
    TestController()
])


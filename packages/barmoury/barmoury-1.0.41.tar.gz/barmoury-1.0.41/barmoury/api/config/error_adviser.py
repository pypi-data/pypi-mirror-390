
from peewee import *
from ..exception import *
from jwt.exceptions import *
from ...util import field_util
from ..model import ApiResponse
from jsonschema.exceptions import *
from json.decoder import JSONDecodeError
from typing import Callable, Any, Self, Dict, Sequence, List, Type
from starlette.applications import Starlette, Request as StarletteRequest


ErrorAdviserMap: Dict[str, 'ErrorAdvise'] = {}


class ErrorAdvise(field_util.MetaObject):
    status_code: int = 500
    error_names: List[str] = []
    errors: List[Exception] = []


def error_advice(**options: Dict[str, Any]):
    err_advice = ErrorAdvise(options)
    
    def error_advice_impl(obj: Callable[[Exception, ErrorAdviserOption], Any]):
        signature = field_util.method_signature(obj)
        if len(signature.parameters) < 2:
            raise MethodSignatureException("The error advice method must have too parameter. (Exception, ErrorAdviserOption)")
        response = {
            "fn": obj,
            "status_code": err_advice.status_code,
            "is_method": len(signature.parameters) > 2
        }
        if field_util.is_class(obj):
            print("THE FILIN OBJ", obj)
            raise ClassUnexpectedException("The @error_advice decorator can only be applied to a method")
        if err_advice.error_names != None:
            for error_name in err_advice.error_names:
                if error_name not in ErrorAdviserMap:
                    ErrorAdviserMap[error_name] = response

        if err_advice.errors != None:
            for error in err_advice.errors:
                if error not in ErrorAdviserMap:
                    ErrorAdviserMap[error] = response

        return obj
    
    return error_advice_impl


class ErrorAdviserOption:
    logger: Type = None
    
    def __init__(self: Self, logger: Callable[[Sequence[Any]], None] = None):
        self.logger = logger


def register_error_advisers(app: Starlette, opts: ErrorAdviserOption, advisers: List[Type]):
    for adviser in advisers:
        if field_util.has_class_attribute(adviser, "setup"):
            adviser.setup(opts)
    app.add_exception_handler(404, adviser_handle_error(opts))
    app.add_exception_handler(Exception, adviser_handle_error(opts))


def adviser_handle_error(opts: ErrorAdviserOption):
    def impl(_: StarletteRequest, exception: Exception):
        error_type = type(exception)
        error_advise = ErrorAdviserMap[error_type] if error_type in ErrorAdviserMap else None
        if error_advise == None:
            error_advise = ErrorAdviserMap[error_type.__name__] if error_type.__name__ in ErrorAdviserMap else None
        if error_advise == None:
            error_advise = ErrorAdviserMap[str(exception)] if str(exception) in ErrorAdviserMap else None
        if error_advise == None:
            error_advise = ErrorAdviserMap["___UnknownError___"] if "___UnknownError___" in ErrorAdviserMap else None
        if error_advise == None:
            raise exception
        response = None
        is_method = error_advise["is_method"]
        if is_method:
            response = error_advise["fn"](error_advise["fn"].__class__(), exception, opts)
        else:
            response = error_advise["fn"](exception, opts)
        response.status_code = error_advise["status_code"]
        return response
    return impl


class ErrorAdviser:
    
    @staticmethod
    def process_response(exception: Exception, errors: List[str], logger: Type = None):
        if logger and logger.error:
            logger.error(f"[barmoury.ErrorAdviser] {errors[0]}", exception)
        if errors != None and len(errors) == 1 and "\n" in errors[0]:
            if type(exception) == ValidationError:
                errors = errors[0].split("\n")[:1]
            else:
                errors = errors[0].split("\n")
        return ApiResponse.buildError(errors=errors)
    
    @error_advice(status_code=400, errors=[JSONDecodeError])
    def request_parse_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, ["Unable to decode data to json"], opts.logger)
    
    @error_advice(status_code=400, errors=[InvalidArgumentException, IntegrityError, ConstraintValidationException])
    def bad_request_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=400, errors=[ValidationError, ValidationException])
    def validation_error_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=404, error_names=["404: Not Found"], errors=[EntityNotFoundException])
    def not_found_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=403, errors=[AccessDeniedException])
    def access_denied_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=405, errors=[RouteMethodNotSupportedException])
    def access_denied_handler(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=401, errors=[MissingTokenException])
    def missing_auth_token(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, [str(exception)], opts.logger)
    
    @error_advice(status_code=401, errors=[ExpiredSignatureError])
    def expired_token_errors(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, ["The authorization token has expired"], opts.logger)
    
    @error_advice(status_code=401, errors=[MissingRequiredClaimError, InvalidSignatureError, InvalidIssuedAtError, InvalidTokenError, DecodeError])
    def unauthorized_errors(exception: Exception, opts: ErrorAdviserOption):
        return ErrorAdviser.process_response(exception, ["Invalid Authorization token"], opts.logger)

import jwt
from .iroute import *
from ..model import *
from ..exception import *
from jwt.exceptions import *
from ...crypto import IEncryptor
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable, Any, Self, Dict, List, Coroutine
from starlette.applications import Starlette, Request as StarletteRequest
from ..decorator import BarmouryGlobalJwtOpenUrlPatterns, BarmouryJwtOpenUrlPatternsMap

class JwtManagerOption:
    id: str = None
    prefix: str = ""
    algorithm: str = "HS512"
    authority_prefix: str = ""
    secrets: Dict[str, str] = {}
    encryptor: IEncryptor[Any] = None
    open_url_patterns: List[Route] = []
    validate: Callable[[StarletteRequest, str, UserDetails[Any]], Coroutine[Any, Any, bool]] = None
    
    def __init__(self: Self, prefix: str = "", authority_prefix: str = "", secrets: Dict[str, str] = {},
                 encryptor: IEncryptor[Any] = None, open_url_patterns: List[Route] = [], validate: Callable[[StarletteRequest, str, UserDetails[Any]], bool] = None):
        self.prefix = prefix
        self.secrets = secrets
        self.validate = validate
        self.encryptor = encryptor
        self.authority_prefix = authority_prefix
        self.open_url_patterns = open_url_patterns


class BarmouryJwtManagerMiddleware(BaseHTTPMiddleware):
    opts: JwtManagerOption = None
    
    async def dispatch(self: Self, request: StarletteRequest, call_next: Callable):
        opts = BarmouryJwtManagerMiddleware.opts
        if len(opts.open_url_patterns) > 0 and should_not_filter(request, opts.prefix, opts.open_url_patterns):
            return await call_next(request)
        authorization = (request.headers.get("authorization") or "").split(" ")
        if len(authorization) < 2:
            raise MissingTokenException("Authorization token is missing")
        result = find_active_token(authorization[1], opts.secrets, opts.algorithm)
        group = result["key"]
        claims = result["payload"]
        if opts.encryptor != None:
            for key, value in claims.items():
                if type(value) != str:
                    continue
                claims[key] = opts.encryptor.decrypt(value)
        if "sub" in claims and "_BJD_" in claims:
            user_details = UserDetails(id=claims["sub"], authority_prefix=opts.authority_prefix, data=claims["_BJD_"])
            if "_BJA_" in claims:
                user_details.authorities_values = claims["_BJA_"]
            if opts.validate != None and not (await opts.validate(request, group, user_details)):
                raise AccessDeniedException("User details validation failed")
            request.state.user = user_details
            request.state.authorities_values = user_details.authorities_values
        else:
            request.state.user = claims
        return await call_next(request)


def register_jwt(app: Starlette, opts: JwtManagerOption):
    if len(opts.secrets) == 0:
        raise InvalidArgumentException("The jwt secrets cannot be empty")
    if BarmouryGlobalJwtOpenUrlPatterns in BarmouryJwtOpenUrlPatternsMap:
        opts.open_url_patterns = util.merge_arrays(opts.open_url_patterns, BarmouryJwtOpenUrlPatternsMap[BarmouryGlobalJwtOpenUrlPatterns])
    if opts.id != None and opts.id in BarmouryJwtOpenUrlPatternsMap:
        opts.open_url_patterns = util.merge_arrays(opts.open_url_patterns, BarmouryJwtOpenUrlPatternsMap[opts.id])
    BarmouryJwtManagerMiddleware.opts = opts
    app.add_middleware(BarmouryJwtManagerMiddleware)


def find_active_token(auth_token: str, secrets: Dict[str, str], algorithm: str) -> Dict[str, str]:
    index = 0
    length = len(secrets)
    for key, value in secrets.items():
        try:
            return {
                "key": key,
                "payload": jwt.decode(auth_token, value, algorithm)
            }
        except MissingRequiredClaimError as e:
            raise e
        except ExpiredSignatureError as e:
            raise e
        except InvalidIssuedAtError as e:
            raise e
        except Exception as e:
            if index == (length - 1):
                raise e
        index += 1
    return None
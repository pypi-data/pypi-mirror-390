
import functools
from .iroute import *
from ...util import *
from ...trace import *
from ...audit import *
from typing import Callable, Self, List, Any
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.applications import Starlette, Request as StarletteRequest


class RequestAuditorAdapterOptions:
    prefix: str = ""
    exclude_url_patterns: List[Route] = []
    get_ip_data: Callable[[str], IpData] = None
    before_auditable: Callable[[Any], Any] = None
    get_auditor: Callable[[], Auditor[Any]] = None
    header_sanitizer: Callable[[str, Any], Any] = None
    resolve: Callable[[StarletteRequest, Audit], Audit] = None

    def __init__(self: Self, prefix: str = "", exclude_url_patterns: List[Route] = [], get_ip_data: Callable[[str], IpData] = None,
                 before_auditable: Callable[[Any], Any] = None, get_auditor: Callable[[], Auditor[Any]] = None, resolve: Callable[[StarletteRequest, Audit], Audit] = None,
                 header_sanitizer: Callable[[str, Any], Any] = None):
        self.valid = prefix
        self.resolve = resolve
        self.get_ip_data = get_ip_data
        self.get_auditor = get_auditor
        self.before_auditable = before_auditable
        self.header_sanitizer = header_sanitizer
        self.exclude_url_patterns = exclude_url_patterns


class BarmouryRequestAuditorMiddleware(BaseHTTPMiddleware):
    opts: RequestAuditorAdapterOptions = None
    
    @staticmethod
    def header_sanitizer(header_name: str, value: Any):
        if "authorization" in header_name or "key" in header_name:
            return "**********"
        return value

    async def dispatch(self: Self, request: StarletteRequest, call_next: Callable):
        opts = BarmouryRequestAuditorMiddleware.opts

        if opts.header_sanitizer == None:
            opts.header_sanitizer = BarmouryRequestAuditorMiddleware.header_sanitizer
        def reduce_headers(headers, key):
            headers[key] = opts.header_sanitizer(key, request.headers.get(key))
            return headers

        if len(opts.exclude_url_patterns) > 0 and should_not_filter(request, opts.prefix, opts.exclude_url_patterns):
            return await call_next(request)
        ip_address = util.ip_address_from_request(request)
        ip_data = opts.get_ip_data(ip_address) if opts.get_ip_data != None else IpData()
        extra_data = {
            "parameters": request.query_params._dict,
            "headers": functools.reduce(reduce_headers, request.headers.keys(), {})
        }
        body = await request.body()
        body = body.decode("utf-8", "ignore") if body != None else None
        audit = Audit(extra_data=extra_data, isp=ip_data.isp, type="HTTP.REQUEST", ip_address=ip_address,
                      action=request.method, location=ip_data.location, source=request.url.path, device=Device.build(request.headers.get("user-agent")),
                      auditable=(opts.before_auditable(body) if opts.before_auditable != None else body))
        opts.get_auditor().audit(opts.resolve(audit) if opts.resolve != None else audit)
        return await call_next(request)


def register_request_auditor_adapter(app: Starlette, opts: RequestAuditorAdapterOptions):
    BarmouryRequestAuditorMiddleware.opts = opts
    app.add_middleware(BarmouryRequestAuditorMiddleware)
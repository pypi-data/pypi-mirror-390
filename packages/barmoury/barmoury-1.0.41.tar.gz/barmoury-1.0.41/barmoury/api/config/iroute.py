
from ...util import *
from typing import List
from .route import Route
from ..config import RouteEntries
from starlette.applications import Request as StarletteRequest
    

def should_not_filter(request: StarletteRequest, prefix: str, open_url_patterns: List[Route]) -> bool:
    if not request.url or not request.url.path:
        return
    method = request.method
    route = ("/" if prefix else "") + request.url.path.replace(prefix or "", "")
    for open_url_pattern in open_url_patterns:
        if (open_url_pattern.method == None or open_url_pattern.method.value == method) and util.pattern_to_regex(open_url_pattern.route).match(route):
            if '{' in open_url_pattern.route and request.url.path in RouteEntries:
                continue
            return True
    return False
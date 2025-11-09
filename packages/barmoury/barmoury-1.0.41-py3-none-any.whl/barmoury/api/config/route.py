
from typing import Self
from ..enum import RequestMethod

class Route:
    route: str = ""
    method: RequestMethod = None
    
    def __init__(self: Self, route: str = "", method: RequestMethod = None):
        self.route = route
        self.method = method
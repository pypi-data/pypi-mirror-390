
from .isp import *
from .location import *
from typing import Self

class IpData:
    isp: Isp = None
    location: Location = None
    
    def __init__(self: Self, isp: Isp = None, location: Location = None):
        self.isp = isp
        self.location = location
 
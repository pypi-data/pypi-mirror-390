
from typing import Self

class Isp:
    name: str = ""
    carrier: str = ""
    
    def __init__(self: Self, name: str = "", carrier: str = ""):
        self.name = name
        self.carrier = carrier
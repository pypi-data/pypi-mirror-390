
from typing import Self

class Location:
    state: str = ""
    country: str = ""
    address: str = ""
    latitude: float = 0.0
    longitude: float = 0.0
    
    def __init__(self: Self, state: str = "", country: str = "", address: str = "", latitude: float = 0.0, longitude: float = 0.0):
        self.state = state
        self.country = country
        self.address = address
        self.latitude = latitude
        self.longitude = longitude
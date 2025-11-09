
from typing import List, Self

class UserDetails[T]:
    id: str = ""
    data: T = None
    authority_prefix: str = ""
    authorities_values: List[str] = []
    
    def __init__(self: Self, id: str = "", data: T = None, authority_prefix: str = "", authorities_values: List[str] = []):
        self.id = id
        self.data = data
        self.authority_prefix = authority_prefix
        self.authorities_values = authorities_values

from .cache import *
from typing import Self

class ListCacheImpl[T](Cache):
    
    cached: List[T] = None
    _max_buffer_size: int = 150
    
    def __init__(self: Self, max_buffer_size: int = 150):
        self.cached = []
        self._max_buffer_size = max_buffer_size
        
    def max_buffer_size(self: Self) -> int:
        return self._max_buffer_size
    
    def cache(self: Self, t: T):
        self.cached.append(t)
    
    def get_cached(self: Self) -> List[T]:
        result_cached = self.cached
        self.cached = []
        return result_cached
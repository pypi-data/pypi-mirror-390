
import abc
from typing import List, Self

class Cache[T](metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def cache(self: Self, t: T):
        """Cache a data"""
    
    @abc.abstractmethod
    def get_cached(self: Self) -> List[T]:
        """Return the cached data"""
        
    def max_buffer_size(self: Self) -> int:
        return 150
        
    def interval_before_flush(self: Self) -> int:
        return 20
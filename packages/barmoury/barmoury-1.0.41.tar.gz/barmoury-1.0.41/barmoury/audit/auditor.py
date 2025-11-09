
import abc
from .audit import *
from ..cache import *
from ..util import util
from typing import Self, Any
from datetime import datetime

class Auditor[T](metaclass=abc.ABCMeta):
    
    buffer_size: int = 0
    date_last_flushed: int = datetime.now()
    
    @abc.abstractmethod
    def flush(self: Self):
        """Flush the audits to a different location"""
    
    @abc.abstractmethod
    def pre_audit(self: Self, audit: Audit):
        """Update the audit before caching"""
    
    @abc.abstractmethod
    def get_cache(self: Self) -> Cache[Any]:
        """Retrieve the audits from the cache"""
        
    def audit(self: Self, audit: Audit):
        self.pre_audit(audit)
        self.buffer_size += 1
        if util.cache_write_along(self.buffer_size, self.date_last_flushed, self.get_cache(), audit):
            self.buffer_size = 0
            self.date_last_flushed = datetime.now()
            self.flush()
        


import sys
import abc
from .log import *
from ..cache import *
from ..util import util
from typing import Self, Any
from datetime import datetime

class Logger(metaclass=abc.ABCMeta):
    
    buffer_size: int = 0
    date_last_flushed: int = datetime.now()
    
    @abc.abstractmethod
    def flush(self: Self):
        """Flush the logs to a different location"""
    
    @abc.abstractmethod
    def pre_log(self: Self, log: Log):
        """Update the log before caching"""
    
    @abc.abstractmethod
    def get_cache(self: Self) -> Cache[Log]:
        """Retrieve the logs from the cache"""
        
    def log(self: Self, log: Log):
        self.pre_log(log)
        self.buffer_size += 1
        if util.cache_write_along(self.buffer_size, self.date_last_flushed, self.get_cache(), log):
            self.buffer_size = 0
            self.date_last_flushed = datetime.now()
            self.flush()
            
    def format_content(self: Self, fmt: str, *args: Any) -> str:
        return util.str_format(fmt, *args)
    
    def verbose(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.VERBOSE
        log.content = self.format_content(fmt, *args)
        self.log(log)
    
    def info(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.INFO
        log.content = self.format_content(fmt, *args)
        self.log(log)
    
    def warn(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.WARN
        log.content = self.format_content(fmt, *args)
        self.log(log)
    
    def trace(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.TRACE
        log.content = self.format_content(fmt, *args)
        self.log(log)
    
    def error(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.ERROR
        log.content = self.format_content(fmt, *args) + "\n" + util.stack_trace_as_string(3)
        self.log(log)
    
    def fatal(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.FATAL
        log.content = self.format_content(fmt, *args) + "\n" + util.stack_trace_as_string(3)
        self.log(log)
        sys.exit(-1199810)
    
    def panic(self: Self, fmt: str, *args: Any):
        log = Log()
        log.level = Level.PANIC
        log.content = self.format_content(fmt, *args) + "\n" + util.stack_trace_as_string(3)
        self.log(log)
        sys.exit(-1199811)
        
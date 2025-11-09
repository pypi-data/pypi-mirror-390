
from enum import Enum
from typing import Self
from ..api.model import Model

class Level(str, Enum):
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    TRACE = "TRACE"
    FATAL = "FATAL"
    PANIC = "PANIC"
    VERBOSE = "VERBOSE"
    

class Log(Model):
    group: str = ""
    source: str = ""
    span_id: str = ""
    content: str = ""
    trace_id: str = ""
    level: Level = Level.INFO
    
    def __init__(self: Self, group: str = "", source: str = "", span_id: str = "", content: str = "", trace_id: str = "", level: Level = Level.INFO):
        self.level = level
        self.group = group
        self.source = source
        self.span_id = span_id
        self.content = content
        self.trace_id = trace_id
    

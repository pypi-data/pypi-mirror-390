
from ..trace import *
from typing import Self, Any
from ..api.model import Model

class Audit[T](Model):
    
    type: str = ""
    isp: Isp = None
    group: str = ""
    status: str = ""
    source: str = ""
    action: str = ""
    audit_id: str = ""
    actor_id: str = ""
    actor_type: str = ""
    ip_address: str = ""
    environment: str = ""
    auditable: Any = None
    device: Device = None
    extra_data: Any = None
    location: Location = None
    
    def __init__(self: Self, type: str = "", isp: Isp = None, group: str = "", status: str = "", 
                source: str = "", action: str = "", audit_id: str = "", actor_type: str = "", ip_address: str = "",
                environment: str = "", auditable: Any = None, device: Device = None, extra_data: Any = None, location: Location = None):
        self.isp = isp
        self.type = type
        self.group = group
        self.device = device
        self.status = status
        self.source = source
        self.action = action
        self.location = location
        self.audit_id = audit_id
        self.auditable = auditable
        self.extra_data = extra_data
        self.actor_type = actor_type
        self.ip_address = ip_address
        self.environment = environment

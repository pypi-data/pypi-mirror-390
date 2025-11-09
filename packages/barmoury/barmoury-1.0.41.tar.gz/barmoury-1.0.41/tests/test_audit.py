
import unittest
from barmoury.audit import *
from barmoury.cache import *

class AuditorImpl(Auditor):
    environment = "local"
    cache = ListCacheImpl()
    service_name = "barmoury"
    
    def pre_audit(self: Self, audit: Audit):
        audit.group = self.service_name
        audit.environment = self.environment
        print("PRE AUDIT", audit.audit_id, audit.group, audit.environment)
    
    def get_cache(self: Self) -> Cache[Audit]:
        return self.cache
    
    def flush(self: Self):
        audits = self.get_cache().get_cached()
        print(audits)

class TestAudit(unittest.TestCase):

    def test_auditor(self):
        auditor = AuditorImpl()
        auditor.audit(Audit(audit_id="audit-1"))
        auditor.audit(Audit(audit_id="audit-2"))
        auditor.audit(Audit(audit_id="audit-3"))
        auditor.audit(Audit(audit_id="audit-4"))
        auditor.audit(Audit(audit_id="audit-5"))
        auditor.audit(Audit(audit_id="audit-6"))

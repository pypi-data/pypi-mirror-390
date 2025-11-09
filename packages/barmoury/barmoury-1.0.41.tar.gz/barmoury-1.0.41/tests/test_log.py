
import unittest
from barmoury.log import *
from barmoury.cache import *

class LoggerImpl(Logger):
    environment = "local"
    cache = ListCacheImpl()
    service_name = "barmoury"
    
    def pre_log(self: Self, log: Log):
        log.group = self.service_name
        print("PRE LOG", log.content)
    
    def get_cache(self: Self) -> Cache[Log]:
        return self.cache
    
    def flush(self: Self):
        logs = self.get_cache().get_cached()
        print(logs)


class TestLog(unittest.TestCase):

    def test_log_levels(self):
        self.assertEqual(log.Level.INFO.value, "INFO")
        self.assertEqual(log.Level.WARN.value, "WARN")
        self.assertEqual(log.Level.ERROR.value, "ERROR")
        self.assertEqual(log.Level.TRACE.value, "TRACE")
        self.assertEqual(log.Level.FATAL.value, "FATAL")
        self.assertEqual(log.Level.PANIC.value, "PANIC")
        self.assertEqual(log.Level.VERBOSE.value, "VERBOSE")

    def test_logger(self):
        logger = LoggerImpl()
        logger.log(Log(content="Pure log test"))
        logger.info("This is the log for the level {}", "info")
        logger.warn("This is the log for the level {}", "warn")
        logger.trace("This is the log for the level {}", "trace")
        #logger.fatal("This is the log for the level {}", "fatal")
        #logger.panic("This is the log for the level {}", "panic")
        logger.verbose("This is the log for the level {}", "verbose")
        #logger.error("This is the log for the level {} {}", "error", NameError("missing jet"))

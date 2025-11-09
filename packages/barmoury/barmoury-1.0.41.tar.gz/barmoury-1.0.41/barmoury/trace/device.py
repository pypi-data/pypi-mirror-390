
import httpagentparser
from typing import Self

class Device:
    os_name: str = ""
    os_version: str = ""
    engine_name: str = ""
    device_name: str = ""
    device_type: str = ""
    device_class: str = ""
    browser_name: str = ""
    engine_version: str = ""
    browser_version: str = ""
    
    def __init__(self: Self, os_name: str = "", os_version: str = "", engine_name: str = "", device_name: str = "", device_type: str = "",
                 device_class: str = "", browser_name: str = "", engine_version: str = "", browser_version: str = ""):
        self.os_name = os_name
        self.os_version = os_version
        self.engine_name = engine_name
        self.device_name = device_name
        self.device_name = device_name
        self.device_type = device_type
        self.device_class = device_class
        self.browser_name = browser_name
        self.engine_version = engine_version
        self.browser_version = browser_version
    
    @staticmethod
    def build(user_agent: str) -> 'Device':
        ua = httpagentparser.detect(user_agent)
        device = Device()
        if "platform" in ua:
            if "name" in ua["platform"]: device.device_name = ua["platform"]["name"]
            if "version" in ua["platform"]: device.os_version = ua["platform"]["version"]
        if "os" in ua:
            if "name" in ua["os"]: device.os_name = ua["os"]["name"]
            if "version" in ua["os"]: device.os_version = ua["os"]["version"]
        if "browser" in ua:
            if "name" in ua["browser"]: device.browser_name = ua["browser"]["name"]
            if "version" in ua["browser"]: device.browser_version = ua["browser"]["version"]
        return device
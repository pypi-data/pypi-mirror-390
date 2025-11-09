
import unittest
from barmoury.trace import *

class TestTrace(unittest.TestCase):

    def test_ip_data(self):
        ip_data = IpData()
        ip_data.isp = Isp()
        ip_data.location = Location()
        self.assertEqual(ip_data.isp.name, "")
        self.assertEqual(ip_data.location.address, Location().address)

    def test_isp(self):
        isp = Isp()
        isp.name = "Glo"
        isp.carrier = "Globacom"
        self.assertEqual(isp.name, "Glo")
        self.assertEqual(isp.carrier, "Globacom")

    def test_location(self):
        location = Location()
        location.latitude = 1.8
        location.longitude = 1.5
        location.state = "State"
        location.country = "Country"
        location.address = "Address"
        self.assertEqual(location.latitude, 1.8)


    def test_domain(self):
        domain = Domain()
        domain.name = "test.com"
        self.assertEqual(domain.name, "test.com")


    def test_device(self):
        d1 = Device.build("Mozilla/5.0 (Linux; U; Android 2.3.5; en-in; HTC_DesireS_S510e Build/GRJ90) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1")
        self.assertEqual(d1.os_name, "Linux")
        self.assertEqual(d1.os_version, "2.3.5")
        self.assertEqual(d1.device_name, "Android")
        self.assertEqual(d1.browser_name, "AndroidBrowser")
    

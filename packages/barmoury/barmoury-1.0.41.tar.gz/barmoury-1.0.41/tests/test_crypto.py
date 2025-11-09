
import unittest
from barmoury.log import *
from barmoury.crypto import *

class TestCrypto(unittest.TestCase):

    def test_crypto(self):
        encryptor = ZlibCompressor[Log]()
        encrypted = encryptor.encrypt([Log(content="The content",source="API",group="barmoury")])
        log = encryptor.decrypt(encrypted)
        self.assertEqual("API", log[0].source)
        self.assertEqual("barmoury", log[0].group)
        self.assertEqual(Level.INFO, log[0].level)
    


import unittest
from datetime import datetime
from barmoury.api import timeo

class TestUtil(unittest.TestCase):

    def test_date_diff_in_minutes(self):
        d1 = datetime.now()
        d2 = datetime.now()
        print(timeo.date_diff_in_minutes(d1, d2))
        self.assertEqual(timeo.date_diff_in_minutes(datetime.now(), datetime.now()), 0)
    

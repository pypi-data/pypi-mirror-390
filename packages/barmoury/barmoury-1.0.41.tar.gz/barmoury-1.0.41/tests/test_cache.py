
import unittest
from barmoury.cache import *

class TestCache(unittest.TestCase):

    def test_cache(self):
        list_cache = ListCacheImpl()
        list_cache.cache(1)
        list_cache.cache(2)
        list_cache.cache(3)
        
        self.assertEqual(len(list_cache.cached), 3)
        cached_values = list_cache.get_cached()
        
        self.assertEqual(len(cached_values), 3)
        self.assertEqual(len(list_cache.cached), 0)
        self.assertNotEqual(cached_values, len(list_cache.cached))
        cached_values.append(10)
        
        self.assertEqual(len(cached_values), 4)
        self.assertEqual(150, list_cache.max_buffer_size())
        self.assertEqual(20, list_cache.interval_before_flush())
    


import unittest
from barmoury.copier import *

class C1:
    age: int = 0.0
    name: str = ""

class TestCopier(unittest.TestCase):

    def test_copier(self):
        c1 = C1()
        c2 = C1()
        c3 = C1()
        c4 = C1()
        
        c2.age = 3.0
        c2.name = "The name"
        c4.name = None
        self.assertEqual(Copier.copy(c1, c2).age, c2.age)
        self.assertEqual(c1.name, c2.name)
        self.assertEqual(c1.name, c2.name)
        self.assertEqual(Copier.copy(c3, c4).age, c4.age)
        self.assertEqual(c3.name, "")
        self.assertNotEqual(c3.name, c4.name)
    

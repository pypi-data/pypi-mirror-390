
import unittest
from barmoury.api import secured, request_mapping
from barmoury.api import RequestMethod, ControllersRequestMap, RequestHandlerSecuredAccessMap

@request_mapping(value="/test")
class TestController1:
    name: str = "Test Controller 1"
    
    @request_mapping(value="/:id")
    @secured(["ROLE_ADD_TEST", "ROLE_EDIT_TEST"])
    def index(self):
        pass

class TestDecorator(unittest.TestCase):

    def test_request_method(self):
        self.assertEqual("PUT", RequestMethod.PUT)
        self.assertEqual("GET", RequestMethod.GET)
        self.assertEqual("HEAD", RequestMethod.HEAD)
        self.assertEqual("POST", RequestMethod.POST)
        self.assertEqual("PATCH", RequestMethod.PATCH)
        self.assertEqual("TRACE", RequestMethod.TRACE)
        self.assertEqual("DELETE", RequestMethod.DELETE)
        self.assertEqual("OPTIONS", RequestMethod.OPTIONS)

    def test_request_mapping_class(self):
        test_controller1 = TestController1()
        self.assertEqual("Test Controller 1", test_controller1.name)
        self.assertNotEqual(None, ControllersRequestMap["TestController1"])
        self.assertNotEqual(None, ControllersRequestMap[TestController1.__name__])
        self.assertEqual("/test", ControllersRequestMap[TestController1.__name__].value)
        self.assertEqual(RequestMethod.GET, ControllersRequestMap[TestController1.__name__].method)
        
    def test_request_mapping_method(self):
        test_controller1 = TestController1()
        self.assertEqual("TestController1.index", test_controller1.index.__qualname__)
        self.assertNotEqual(None, ControllersRequestMap["TestController1.index"])
        self.assertNotEqual(None, ControllersRequestMap[TestController1.index.__qualname__])
        self.assertEqual("/:id", ControllersRequestMap[TestController1.index.__qualname__].value)
        self.assertEqual(RequestMethod.GET, ControllersRequestMap[TestController1.index.__qualname__].method)
        
    def test_secured_method(self):
        TestController1()
        self.assertNotEqual(None, RequestHandlerSecuredAccessMap["TestController1.index"])
        self.assertEqual(2, len(RequestHandlerSecuredAccessMap[TestController1.index.__qualname__]))
        self.assertNotEqual(None, RequestHandlerSecuredAccessMap[TestController1.index.__qualname__])
        self.assertEqual("ROLE_ADD_TEST", RequestHandlerSecuredAccessMap[TestController1.index.__qualname__][0])
        self.assertEqual("ROLE_EDIT_TEST", RequestHandlerSecuredAccessMap[TestController1.index.__qualname__][1])
    

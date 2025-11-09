
from enum import Enum

class RequestMethod(str, Enum):

    ANY = "ANY"
    PUT = "PUT"
    GET = "GET"
    HEAD = "HEAD"
    POST = "POST"
    PATCH = "PATCH"
    TRACE = "TRACE"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"
    

import zlib
import base64
from .encryptor import *
from ..util import json_mapper

class ZlibCompressor[T](IEncryptor[T]):
    
    def encrypt(self: Self, payload: T) -> str:
        compressed = zlib.compress(str.encode(json_mapper.to_json(payload)))
        return base64.b64encode(compressed).decode("utf-8", "ignore")
    
    def decrypt(self: Self, payload: str) -> T:
        b64decoded = base64.b64decode(str.encode(payload))
        decompressed = zlib.decompress(b64decoded)
        return json_mapper.from_json(decompressed.decode("utf-8", "ignore"), True)
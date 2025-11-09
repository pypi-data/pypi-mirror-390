
import abc
from typing import Self

class IEncryptor[T](metaclass=abc.ABCMeta):
    
    @abc.abstractmethod
    def encrypt(self: Self, payload: T) -> str:
        """Encrypt a payload"""
    
    @abc.abstractmethod
    def decrypt(self: Self, payload: str) -> T:
        """Decrypt a payload"""

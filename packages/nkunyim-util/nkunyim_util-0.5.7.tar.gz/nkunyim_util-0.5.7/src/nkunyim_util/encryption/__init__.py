import base64
from enum import Enum
import hashlib


class Base64Util:
    @staticmethod
    def encode(input_string: str) -> str:
        string_bytes = input_string.encode('utf-8')
        encoded_bytes = base64.b64encode(string_bytes)
        return encoded_bytes.decode('utf-8')

    @staticmethod
    def decode(encoded_string: str) -> str:
        encoded_bytes = encoded_string.encode('utf-8')
        decoded_bytes = base64.b64decode(encoded_bytes)
        return decoded_bytes.decode('utf-8')


class HashingAlgo(str, Enum):
    S256 = "S256"
    S384 = "S384"
    S512 = "S512"


class Hashing:
    
    def __init__(self, input_string: str) -> None:
        self.input_bytes = input_string.encode('utf-8')
        self.hash = hashlib.sha256()
    
    def _make(self) -> str:
        self.hash.update(self.input_bytes)
        digest = self.hash.digest()
        return base64.urlsafe_b64encode(digest).decode('utf-8').replace('=', '')
    
    def sha256(self) -> str:
        return self._make()
        
    def sha384(self) -> str:
        self.hash = hashlib.sha384()
        return self._make()
    
    def sha512(self) -> str:
        self.hash = hashlib.sha512()
        return self._make()
    
    def make(self, algo: HashingAlgo) -> str:
        if algo == HashingAlgo.S256:
            return self.sha256()
        elif algo == HashingAlgo.S384:
            return self.sha384()
        elif algo == HashingAlgo.S512:
            return self.sha512()
        else:
            raise Exception(f"HashingAlgo [{algo}] is either invalid or not supported.")


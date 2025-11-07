import base64


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
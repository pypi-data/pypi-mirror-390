import base64
import requests
from django.conf import settings
from django.http import HttpRequest

from nkunyim_util.encryption.rsa_encryption import RSAEncryption
from nkunyim_util.services.session_service import SessionService


class NkunyimApiClient:
    def __init__(self, req: HttpRequest, name: str) -> None:
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        self.req = req
        self.name = name.upper()
        self._init_base_url()
        self._init_headers()


    def _init_base_url(self) -> None:
        try:
            base_url = str(settings.NKUNYIM_SERVICES[self.name])
            self.base_url = base_url.rstrip('/')
        except KeyError:
            raise Exception(f"Service configuration '{self.name}' is not defined in settings.")


    def _init_headers(self) -> None:
        encryption = RSAEncryption()
        encrypted = encryption.encrypt(plain_text=self.name, name=self.name)
        token = base64.b64encode(encrypted).decode('utf-8')
        self.headers['Xan-Authorization'] = token

        session_service = SessionService(req=self.req)
        if session_service.has_lifetime:
            token_model = session_service.get_token()
            if token_model:
                self.headers['Authorization'] = f'JWT {token_model.access_token}'


    def _build_url(self, path: str) -> str:
        base = self.base_url
        if not base.endswith('/api'):
            base += '/api'

        if not path.startswith('/'):
            path = '/' + path

        return base + path
    


    def get(self, path: str):
        response = requests.get(self._build_url(path), headers=self.headers)
        return response


    def post(self, path: str, data: dict):
        url = self._build_url(path)
        if not url.endswith('/'):
            url += '/'
        response = requests.post(url, data=data, headers=self.headers)
        return response


    def put(self, path: str, data: dict):
        response = requests.put(self._build_url(path), data=data, headers=self.headers)
        return response


    def patch(self, path: str, data: dict):
        response = requests.patch(self._build_url(path), data=data, headers=self.headers)
        return response


    def delete(self, path: str):
        response = requests.delete(self._build_url(path), headers=self.headers)
        return response

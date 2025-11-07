
from pydantic import BaseModel


class OAuth2Model(BaseModel):
    next: str = "/home/"
    state: str
    nonce: str
    code: str
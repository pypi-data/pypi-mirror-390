
from pydantic import BaseModel


class OAuth2Model(BaseModel):
    state: str
    nonce: str
    code: str
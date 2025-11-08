from datetime import datetime
from pydantic import BaseModel


class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: datetime
    scope: str

from pydantic import BaseModel
from typing import Optional

from nkunyim_util.models.user_model import UserModel
from nkunyim_util.models.token_model import TokenModel



class SessionModel(BaseModel):
    token: Optional[TokenModel]
    user: Optional[UserModel]
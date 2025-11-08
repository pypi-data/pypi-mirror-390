from pydantic import BaseModel


class UserinfoModel(BaseModel):
    code: str
    state: str
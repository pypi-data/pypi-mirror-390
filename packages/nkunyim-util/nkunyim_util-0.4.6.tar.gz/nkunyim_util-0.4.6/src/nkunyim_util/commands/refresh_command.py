from pydantic import BaseModel


class RefreshCommand(BaseModel):
    grant_type: str
    code: str
    redirect_uri: str
    client_id: str
    client_secret: str


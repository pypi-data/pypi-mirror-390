from pydantic import BaseModel


class AuthorizeCommand(BaseModel):
    client_id: str
    client_scope: str
    redirect_uri: str
    response_type: str = "code"

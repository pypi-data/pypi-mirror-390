from pydantic import BaseModel

    
class TokenCommand(BaseModel):
    grant_type: str = "authorization_code"
    code: str = ""
    redirect_uri: str
    client_id: str
    client_secret: str
    

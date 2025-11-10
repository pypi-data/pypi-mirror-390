from pydantic import BaseModel

from nkunyim_util.encryption import HashingAlgo


class AuthorizeCommand(BaseModel):
    client_id: str
    client_scope: str
    redirect_uri: str
    response_type: str = "code"
    hash_algo: HashingAlgo = HashingAlgo.S256

from enum import Enum
from pydantic import BaseModel


class MessageLevel(str, Enum):
    INFO = "info"
    SUCCESS =  "success"
    WARNING = "warning"
    ERROR =  "error"

        
class MessageModel(BaseModel):
    level: MessageLevel = MessageLevel.ERROR
    message: str


from enum import Enum
from pydantic import BaseModel, ConfigDict


class MessageLevel(str, Enum):
    INFO = "info"
    SUCCESS =  "success"
    WARNING = "warning"
    ERROR =  "error"

        
class MessageModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    level: MessageLevel = MessageLevel.ERROR
    message: str


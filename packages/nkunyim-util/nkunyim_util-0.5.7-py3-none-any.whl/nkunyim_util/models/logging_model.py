from uuid import UUID
from pydantic import BaseModel


class LoggingModel(BaseModel):
    app_id: UUID
    app_name: str
    label: str
    nation_code: str
    city: str
    user_ip: str
    user_agent: str
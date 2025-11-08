from pydantic import BaseModel

from nkunyim_util.models.message_model import MessageModel


class ViewBag(BaseModel):
    ok: bool = False
    data: dict = {}
    messages: list[MessageModel] = []
    page_url: str = ""
    next_url: str = ""

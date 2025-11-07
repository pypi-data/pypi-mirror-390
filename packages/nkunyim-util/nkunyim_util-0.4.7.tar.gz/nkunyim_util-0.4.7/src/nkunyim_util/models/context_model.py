from typing import Optional, List
from pydantic import BaseModel

from .application_model import ProjectModel
from .location_model import LocationModel
from .nation_model import NationModel
from .account_model import NavModel
from .page_model import PageModel
from .user_model import UserModel


class ContextModel(BaseModel):
    name: str
    title: str
    caption: str
    description: str
    keywords: str
    image_url: str
    logo_url: str
    logo_light_url: str
    logo_dark_url: str
    icon_url: str
    icon_light_url: str
    icon_dark_url: str
    tags: str
    colour: str
    location: LocationModel
    nation: NationModel
    user: Optional[UserModel] = None
    page: PageModel
    navs: Optional[List[NavModel]]
    uix: dict
    root: str
    
    
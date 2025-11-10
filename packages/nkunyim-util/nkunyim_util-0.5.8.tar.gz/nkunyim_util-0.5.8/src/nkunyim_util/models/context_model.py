from typing import Optional, List
from pydantic import BaseModel

from nkunyim_util.models.account_model import NavModel
from nkunyim_util.models.location_model import LocationModel
from nkunyim_util.models.nation_model import NationModel
from nkunyim_util.models.page_model import PageModel
from nkunyim_util.models.user_agent_model import UserAgentModel
from nkunyim_util.models.user_model import UserModel


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
    user_agent: UserAgentModel
    user: Optional[UserModel] = None
    page: PageModel
    navs: Optional[List[NavModel]]
    uix: dict
    root: str
    
    
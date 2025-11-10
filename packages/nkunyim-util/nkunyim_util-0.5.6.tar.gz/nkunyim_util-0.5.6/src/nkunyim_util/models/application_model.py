from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID

from nkunyim_util.encryption import HashingAlgo


class ModuleModel(BaseModel):
    id: UUID
    name: str
    title: str
    version: str


class ProjectModel(BaseModel):
    id: UUID
    name: str
    caption: str
    description: str
    logo_url: str
    is_locked: bool
    tags: str


class AppModel(BaseModel):
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
    

class ApplicationModel(AppModel):
    id: UUID
    mode: str
    domain: str
    client_id: str
    client_secret: str
    client_scope: str
    redirect_uri: str
    response_type: str
    grant_type: str
    hash_algo: HashingAlgo
    is_active: bool
    project: ProjectModel
    modules: Optional[List[ModuleModel]]
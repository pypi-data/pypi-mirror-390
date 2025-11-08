from typing import Optional
from django.conf import settings
from django.http import HttpRequest

from nkunyim_util.models.message_model import MessageLevel, MessageModel
from nkunyim_util.models.nation_model import NationModel
from nkunyim_util.caches.nation_cache import NationCache
from nkunyim_util.api.nkunyim_api_client import NkunyimApiClient


from .signals import nation_data_updated


class NationService:

    def __init__(self, req: HttpRequest, session_key: str, code: str) -> None:
        self.cache = NationCache(key=f"nat.{session_key}")
        self.req = req
        self.code = code
        self.messages: list[MessageModel] = []


    def _get_from_api(self) -> Optional[NationModel]:
        try:
            client = NkunyimApiClient(req=self.req, name=settings.PLACE_SERVICE)
            response = client.get(path=f"/nations/?code={self.code.upper()}")
            if not response.ok:
                self.messages.append(MessageModel(level=MessageLevel.WARNING, message="Failed to retrieve nation data from API."))
                # log error
                return None
            
            json_data = response.json()
            result_data = dict(json_data).get("results", [None])
            model_data = result_data[0]
            
            if not model_data:
                return None

            nation_model = NationModel(**model_data)
            self.cache.set(model=nation_model, timeout=60 * 60 * 24)
            
            # Inform interested parties
            nation_data_updated.send(sender=NationModel, instance=nation_model)
            
            return nation_model
        except Exception as ex:
            raise ex
            
    
    def get(self) -> Optional[NationModel]:
        return self.cache.get() or self._get_from_api()
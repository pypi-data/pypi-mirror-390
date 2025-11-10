from django.http import HttpRequest

from nkunyim_util.models.logging_model import LoggingModel
from nkunyim_util.services.application_service import ApplicationService
from nkunyim_util.services.location_service import LocationService
from nkunyim_util.services.page_service import PageService
from nkunyim_util.services.user_agent_service import UserAgentService


class LoggingService:
    
    def __init__(self, req: HttpRequest) -> None:
        self.req = req


    def get(self) -> LoggingModel:
        page_model = PageService(req=self.req)
        page_data = page_model.get()
        
        application_model = ApplicationService(req=self.req, session_key=page_data.root)
        application_data = application_model.get()
        
        location_model = LocationService(req=self.req, session_key=page_data.root)
        location_data = location_model.get()
        
        user_agent_model = UserAgentService(req=self.req, session_key=page_data.root)
        user_agent_data = user_agent_model.get()
        user_agent = user_agent_data.browser_name + ' ' + user_agent_data.browser_version
        
        logging_model = LoggingModel(
            app_id=application_data.id,
            app_name=application_data.name,
            label='Nkunyim Studio',
            nation_code=location_data.country_code,
            city=location_data.city,
            user_ip=location_data.user_ip,
            user_agent=user_agent
        )
        
        return logging_model
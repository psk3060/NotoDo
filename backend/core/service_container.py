# container를 활용하는 이유는 lifespan에서 변수를 공유하고자 하기 때문(로컬 변수의 한계)

from service.notion_service import NotionApiServiceImpl

class ServiceContainer:
    notion : "NotionApiServiceImpl | None" = None
    
service_container = ServiceContainer()
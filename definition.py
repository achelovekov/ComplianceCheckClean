from pydantic import BaseModel
from typing import Any, Optional, Tuple, List, Dict, Union

class Service(BaseModel):
    serviceName: str
    footprintDefinition: Optional[str]
    streeDefinition: Optional[str]
    ttpTemplates: Optional[List[str]]
    subServices: Optional[List['Service']]

Service.update_forward_refs()





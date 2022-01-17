from pydantic import BaseModel
from typing import Any, Optional, Tuple, List, Dict, Union

class ServiceDefinition(BaseModel):
    serviceName: str
    footprintDefinition: Optional[str]
    streeDefinition: Optional[str]
    ttpTemplates: Optional[List[str]]
    subServices: Optional[List['ServiceDefinition']]

ServiceDefinition.update_forward_refs()





from pydantic import BaseModel
from typing import Any, Optional, Tuple, List, Dict, Union

class ServiceDefinition(BaseModel):
    serviceName: str
    footprintDefinition: Optional[str]
    streeDefinition: Optional[str]
    ttpTemplates: Optional[List[str]]
    subServices: Optional[List['ServiceDefinition']]

ServiceDefinition.update_forward_refs()

class KeyDefinition(BaseModel):
    footprintKey: str
    SoTKey: str

class KeysDefinition(BaseModel):
    __root__: List[KeyDefinition] = []

    def append(self, keyDefinition:KeyDefinition):
        self.__root__.append(keyDefinition)
    
    def __iter__(self):
        return iter(self.__root__)

class ServiceItem(BaseModel):
    serviceName: str
    keys: KeysDefinition

class ServiceDescription(BaseModel):
    siteID: str
    configsFolder: str
    SOTDB: str
    serviceItems: List[ServiceItem]
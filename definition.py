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
    SoTKey: str = ''

class KeysDefinition(BaseModel):
    __root__: List[KeyDefinition] = []

    def append(self, keyDefinition:KeyDefinition):
        self.__root__.append(keyDefinition)
    
    def __iter__(self):
        return iter(self.__root__)

class ServiceItemProcessed(BaseModel):
    serviceName: str
    keys: KeysDefinition = []

class ServiceDescriptionProcessed(BaseModel):
    siteID: str
    configsFolder: str
    SOTDB: str
    serviceItems: List[ServiceItemProcessed] = []

class ServiceItem(BaseModel):
    serviceName: str
    footprintKeysType: str #static|dynamic
    footprintKeys: Optional[List[str]]
    SoTKeysType: str #general|specific

class ServiceItems(BaseModel):
    __root__: List[ServiceItem] = []

    def append(self, serviceItem:ServiceItem):
        self.__root__.append(serviceItem)
    
    def __iter__(self):
        return iter(self.__root__)

def getServiceDefinitionByName(serviceName) -> ServiceDefinition:
    try:
        with open(f"services/serviceDefinitions/{serviceName}.json", encoding = 'utf-8') as f:
            return ServiceDefinition.parse_raw(f.read())
    except FileNotFoundError as e:
        print(f"{e}")

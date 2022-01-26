from __future__ import annotations

from typing import Dict, List, Optional, Union
from pydantic import BaseModel


class Var(BaseModel):
    type: str  
    path: Optional[str] 
    value: Optional[str]
    values: Optional[List[str]]

class SoTDBItem(BaseModel):
    serviceName: str
    siteId: str
    serviceId: str
    templateType: str
    vars: Dict[str, Var]

class SoTDB(BaseModel):
    __root__: List[SoTDBItem] 

    def append(self, soTDBItem:SoTDBItem):
        self.__root__.append(soTDBItem)
  
    def __iter__(self):
        return iter(self.__root__)

    def getSoTDBItem(self, serviceName, siteId, SoTKey) -> Dict:
        for item in self:
            if (item.serviceName == serviceName and
                item.siteId == siteId and
                item.serviceId == SoTKey):
                return item
        print(f"Can't get SoT for: {serviceName}, {siteId}, {SoTKey}")
        return None

""" SoTDBFile = 'SoTDB.json'
soTDB = SoTDB.parse_file(SoTDBFile)

print(soTDB.getSoTDBItem('l3vni','VTB','PROD-SRV-APP')) """

var = Var(type='a', value='b')

print(var.json())
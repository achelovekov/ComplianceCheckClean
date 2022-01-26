from pydantic import BaseModel
from typing import Any, Tuple, List, Dict, Union

class AuxilaryDBItem(BaseModel):
    serviceName: str
    siteId: str
    deviceName: str
    footprintKeys: List[str]

class AuxilaryDB(BaseModel):
    __root__: List[AuxilaryDBItem] = []

    def append(self, auxilaryDBItem:AuxilaryDBItem):
        self.__root__.append(auxilaryDBItem)

    def __iter__(self):
        return iter(self.__root__)

    def getDynamicKeys(self, serviceName: str, siteId: str, deviceName: str) -> List[str]:
        for serviceItem in self:
            if (serviceItem.serviceName == serviceName and
               serviceItem.siteId == siteId and
               serviceItem.deviceName == deviceName):
               return serviceItem.footprintKeys   
        print(f"Can't get footprint keys for: {serviceName} {siteId} {deviceName}")
        return None
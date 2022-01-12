from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import BaseModel


class Var(BaseModel):
    type: str  
    path: Optional[str] 
    value: str  

class SiteVar(BaseModel):
    serviceType: Optional[Var]
    id: Optional[Var]
    idNum: Optional[Var]
    vni: Optional[Var]
    sviId: Optional[Var]
    asNum: Optional[Var]
    description: Optional[Var]
    vrfName: Optional[Var]
    sourceVar: Optional[Var]
    redistributeDirectRMap: Optional[Var]
    stalePathTime: Optional[Var]
    multipathRelax: Optional[Var]
    routerId: Optional[Var]
    redistributeDirectRMapSeq: Optional[Var]

class ServiceVar(BaseModel):
    siteID: str
    siteVars: List[SiteVar]


class ServiceItem(BaseModel):
    serviceName: str
    serviceVars: List[ServiceVar]


class ServiceSoT(BaseModel):
    __root__: List[ServiceItem]

    def append(self, serviceItem:ServiceItem):
        self.__root__.append(serviceItem)
  
    def __iter__(self):
        return iter(self.__root__)

    def getService(self, serviceName):
        for serviceItem in self:
            if serviceItem.serviceName == serviceName: 
                return serviceItem
        return None
    
    def getSite(self, serviceItem, siteID):
        for siteItem in serviceItem.serviceVars:
            if siteItem.siteID == siteID:
                return siteItem
        return None
    
    def getKey(self, siteItem, key):
        for keyItem in siteItem.siteVars:
            if keyItem.id.value == key:
                return keyItem
        return None

    def getVarsByKey(self, serviceName, siteID, key) -> Dict:
        if serviceItem := self.getService(serviceName):
            if siteItem := self.getSite(serviceItem, siteID):
                if keyItem := self.getKey(siteItem, key):
                    return keyItem.dict()
                else:
                    return None
            else:
                return None
        else:
            return None

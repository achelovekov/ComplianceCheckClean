from ast import Str
from pstats import SortKey
from xxlimited import foo
from pydantic import BaseModel
from typing import Any, Tuple, List, Dict, Union

import modeling
import definition
import templating
import sot
import json
import auxilary

class ComplianceReportItem(BaseModel):
  footprint: Union[Dict, List, str] = dict()
  original: str = ''
  templated: str = ''
  deviceName: str


  @classmethod
  def generate(cls, referenceValues: modeling.ReferenceValues, soTDBItem: sot.SoTDBItem, deviceName, footprint, serviceDefinition, rawCollection):

    vars = templating.processVariables(soTDBItem, footprint)
    referenceValues.updateVarsWithId(vars)

    print(f"vars: {json.dumps(vars, sort_keys=True, indent=4)}")


    sTreeService = templating.STreeService.parse_file(serviceDefinition.streeDefinition)
    sTreeServiceProcessed = sTreeService.process(vars)
    rootNode = templating.streeFromConfig(rawCollection[deviceName])
    result = []
    templating.genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)
    original = '\n'.join(result)
    print(f"original:")
    print(f"{original}")

    templated = templating.TemplatedAuxilary.generateTemplated(vars, soTDBItem.serviceName, soTDBItem.templateType)

    
    print(f"templated {templated}")
    
    return original, templated



  def update(self, footprint, original, templated):
    if isinstance(self.footprint, Dict):
      self.footprint = []
      self.footprint.append(footprint)
      self.original += '\n' + original
      self.templated += templated
      return
    if isinstance(self.footprint, List):
      self.footprint.append(footprint)
      self.original += '\n' + original
      self.templated += templated
      return

class ComplianceReport(BaseModel):
  __root__: List[ComplianceReportItem] = []

  def append(self, complianceReportItem:ComplianceReportItem):
    self.__root__.append(complianceReportItem)
  
  def __iter__(self):
    return iter(self.__root__)

  def getComplianceReportItemByDeviceName(self, deviceName):
    for item in self:
      print(item.deviceName, deviceName)
      if item.deviceName == deviceName:
        return item
    return None

  def generate(self, serviceName, keys: definition.KeysDefinition, siteID, configsFolder, SOTDB, serviceDefinition):
    for key in keys:

      print(f"go for key: {key.footprintKey}")

      referenceValues = modeling.ReferenceValues()
      referenceValues.append(modeling.ReferenceValue(id='id', value=key.footprintKey))

      varsFromSot = sot.getVarsFromSoT(SOTDB, siteID, serviceName, key.SoTKey)
      if varsFromSot:
        referenceValues = modeling.getDirectVarsValues(referenceValues, varsFromSot)

      rawCollectionConfigs, rawCollectionFootprints = modeling.generateFootprintDB(serviceDefinition, configsFolder, referenceValues)

      for device, footprint in rawCollectionFootprints.items():
        if footprint:
          complianceReportItem = ComplianceReportItem.generate(serviceName, referenceValues, varsFromSot, device, footprint, serviceDefinition, rawCollectionConfigs, rawCollectionFootprints)
          self.update(complianceReportItem)

class ConsistencyReport(BaseModel):
  @classmethod
  def generate(cls, serviceName, serviceKey, siteID, configsFolder, SOTDB):
    serviceDefinition = definition.ServiceDefinition.parse_file(f"services/serviceDefinitions/{serviceName}.json")

    varsFromSot = sot.getVarsFromSoT(SOTDB, siteID, serviceName, serviceKey)
    if not varsFromSot:
      print(f"can't get SoT values for {serviceName} {serviceKey} for folder {configsFolder}")
      referenceValues = modeling.ReferenceValues()
      referenceValues.append(modeling.ReferenceValue(id='id', value=serviceKey))
    else:
      print(f"varsFromSot: {json.dumps(varsFromSot, sort_keys=True, indent=4)}")
      referenceValues = modeling.getDirectVarsValues(varsFromSot)

    print(f"referenceValues: {referenceValues.json()}")

    _, rawCollectionFootprints = modeling.generateFootprintDB(serviceDefinition, configsFolder, referenceValues)

    return modeling.generateConsistencyDB(rawCollectionFootprints)

class TTPDB(BaseModel):
  @classmethod
  def generate(cls, serviceName, configsFolder):
    modeling.generateTTPDB(serviceName, configsFolder)

#####################
class Key(BaseModel):
  footprintKey: str
  SoTKey: str

class Service(BaseModel):
  serviceName: str
  serviceKeys: List[Key] = []

class ComplianceReferenceDBItem(BaseModel):
  deviceName: str
  services: List[Service] = []

class ComplianceReferenceDB(BaseModel):
  __root__: List[ComplianceReferenceDBItem] = []

  def append(self, complianceReferenceDBItem:ComplianceReferenceDBItem):
    self.__root__.append(complianceReferenceDBItem)

  def __iter__(self):
    return iter(self.__root__)

def generateComplianceReferenceDB(
  serviceItems: definition.ServiceItems, 
  auxilaryDB: auxilary.AuxilaryDB,
  siteId: str,
  deviceNames: List[str]):

  complianceReferenceDB = ComplianceReferenceDB()

  for deviceName in deviceNames:
    complianceReferenceDBItem = ComplianceReferenceDBItem(deviceName=deviceName)
    for serviceItem in serviceItems:
      service = Service(serviceName=serviceItem.serviceName)
      if serviceItem.footprintKeysType == 'static':
        footprintKeys = serviceItem.footprintKeys
      if serviceItem.footprintKeysType == 'dynamic':
        footprintKeys = auxilaryDB.getDynamicKeys(serviceItem.serviceName, siteId, deviceName)
        print(f"footprintKeys: {footprintKeys}")
      if serviceItem.footprintKeysType == 'none':
        footprintKeys = ["none"]
      for footprintKey in footprintKeys:
        if serviceItem.SoTKeysType == 'general':
          key = Key(footprintKey=footprintKey, SoTKey='general')
        if serviceItem.SoTKeysType == 'specific':
          key = Key(footprintKey=footprintKey, SoTKey=footprintKey)
        service.serviceKeys.append(key)
      complianceReferenceDBItem.services.append(service)
  
    complianceReferenceDB.append(complianceReferenceDBItem)
  
  return complianceReferenceDB
#####################

def combinedCompianceReport(
  configsFolder: str, 
  serviceItems: definition.ServiceItems, 
  auxilaryDB: auxilary.AuxilaryDB, 
  siteId: str,
  SoTDB: sot.SoTDB
  ) -> ComplianceReport:

  rawCollection = modeling.generateRawCollection(configsFolder)

  complianceReferenceDB = generateComplianceReferenceDB(serviceItems, auxilaryDB, siteId, rawCollection.keys())

  print(complianceReferenceDB.json())
 
  complianceReport = ComplianceReport()

  for complianceReferenceDBItem in complianceReferenceDB:
    print(f"go for {complianceReferenceDBItem.deviceName}")
    complianceReportItem = ComplianceReportItem(deviceName=complianceReferenceDBItem.deviceName)
    for service in complianceReferenceDBItem.services:
      serviceDefinition = definition.getServiceDefinitionByName(service.serviceName)

      for serviceKey in service.serviceKeys:
        referenceValues = modeling.ReferenceValues()
        referenceValues.append(modeling.ReferenceValue(id='id', value=serviceKey.footprintKey))

        soTDBItem = SoTDB.getSoTDBItem(service.serviceName, siteId, serviceKey.SoTKey)
        if soTDBItem:
          referenceValues = modeling.getDirectVarsValues(referenceValues, soTDBItem)
        else:
          raise NotImplementedError(f"not implemented SoT for service {service.serviceName}")
        print(referenceValues.json())

        if footprint := modeling.generateFootprint(serviceDefinition, rawCollection[complianceReferenceDBItem.deviceName], referenceValues):

          print(f"footprint for {complianceReferenceDBItem.deviceName}: {json.dumps(footprint, sort_keys=True, indent=4)}")

          original, templated = ComplianceReportItem.generate(referenceValues, soTDBItem, complianceReferenceDBItem.deviceName, footprint, serviceDefinition, rawCollection)

          complianceReportItem.update(footprint, original, templated)
    if complianceReportItem.footprint:
      complianceReport.append(complianceReportItem)
  
  return complianceReport







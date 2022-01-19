from ast import Str
from pydantic import BaseModel
from typing import Any, Tuple, List, Dict, Union

import modeling
import definition
import templating
import sot
import json

class ComplianceReportItem(BaseModel):
  key: str
  footprint: Union[Dict, List, str]
  original: str
  templated: str
  deviceName: str


  @classmethod
  def updateVarsWithId(cls, referenceValues, vars):
    for referenceValue in referenceValues:
      if referenceValue.id == 'id':
        vars['id'] = referenceValue.value

  @classmethod
  def generate(cls, serviceName, referenceValues, serviceSotKey, varsFromSot, device, footprint, serviceDefinition, rawCollectionConfigs, rawCollectionFootprints):

    print(f"footprint: {footprint}")
    print(f"referenceValues: {referenceValues.json()}")

    vars = templating.processVariables(varsFromSot, footprint)
    ComplianceReportItem.updateVarsWithId(referenceValues, vars)
    print(f"vars: {json.dumps(vars, sort_keys=True, indent=4)}")
    
    sTreeService = templating.STreeService.parse_file(serviceDefinition.streeDefinition)
    sTreeServiceProcessed = sTreeService.process(vars)
    rootNode = templating.streeFromConfig(rawCollectionConfigs[device])
    result = []
    templating.genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)
    original = '\n'.join(result)
    print(f"original: {original}")

    templated = templating.TemplatedAuxilary.generateTemplated(vars, serviceName, varsFromSot['serviceType']['value'])
    print(f"templated: {templated}")
    
    complianceReportItem = ComplianceReportItem(key=serviceSotKey, original=original, templated=templated, deviceName=device, footprint=rawCollectionFootprints[device])
    return complianceReportItem  

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

  def update(self, complianceReportItem:ComplianceReportItem):
    if complianceReportItemByDeviceName := self.getComplianceReportItemByDeviceName(complianceReportItem.deviceName):
      if isinstance(complianceReportItemByDeviceName.footprint, Dict):
        complianceReportItemByDeviceName.footprint = [complianceReportItemByDeviceName.footprint]
        complianceReportItemByDeviceName.footprint.append(complianceReportItem.footprint)
        complianceReportItemByDeviceName.original += '\n' + complianceReportItem.original
        complianceReportItemByDeviceName.templated += '\n' + complianceReportItem.templated
        return
      if isinstance(complianceReportItemByDeviceName.footprint, List):
        complianceReportItemByDeviceName.footprint.append(complianceReportItem.footprint)
        complianceReportItemByDeviceName.original += '\n' + complianceReportItem.original
        complianceReportItemByDeviceName.templated += '\n' + complianceReportItem.templated
        return
    else:
      self.append(complianceReportItem)

  def generate(self, serviceName, footprintKeys, serviceSotKey, siteID, configsFolder, SOTDB, serviceDefinition):
    for footprintKey in footprintKeys:

      print(f"go for key: {footprintKey}")

      varsFromSot = sot.getVarsFromSoT(SOTDB, siteID, serviceName, serviceSotKey)
      if not varsFromSot:
          print(f"can't get SoT values for {serviceName} {serviceSotKey} for folder {configsFolder}")
          referenceValues = modeling.ReferenceValues()
          referenceValues.append(modeling.ReferenceValue(id='id', value=footprintKey))
      else:
        print(f"vars from SoT: {json.dumps(varsFromSot, sort_keys=True, indent=4)}")
        referenceValues = modeling.ReferenceValues()
        referenceValues.append(modeling.ReferenceValue(id='id', value=footprintKey))
        referenceValues = modeling.getDirectVarsValues(referenceValues, varsFromSot)

      rawCollectionConfigs, rawCollectionFootprints = modeling.generateFootprintDB(serviceDefinition, configsFolder, referenceValues)

      for device, footprint in rawCollectionFootprints.items():
        if footprint:
          complianceReportItem = ComplianceReportItem.generate(serviceName, referenceValues, serviceSotKey, varsFromSot, device, footprint, serviceDefinition, rawCollectionConfigs, rawCollectionFootprints)
          #print(complianceReportItem.json())
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
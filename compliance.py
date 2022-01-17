from pydantic import BaseModel
from typing import Any, Tuple, List, Dict, Union

import modeling
import definition
import templating
import sot
import json

class ComplianceReportItem(BaseModel):
  key: str
  footprint: str
  original: str
  templated: str
  deviceName: str

  @classmethod
  def generate(cls, serviceName, serviceKey, varsFromSot, device, footprint, serviceDefinition, rawCollectionConfigs, rawCollectionFootprints):

    vars = templating.processVariables(varsFromSot, footprint[serviceName])
    #print(json.dumps(vars, sort_keys=True, indent=4))
    
    sTreeService = templating.STreeService.parse_file(serviceDefinition.streeDefinition)
    sTreeServiceProcessed = sTreeService.process(vars)
    rootNode = templating.streeFromConfig(rawCollectionConfigs[device])
    result = []
    templating.genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)
    original = '\n'.join(result)
    #print(f"original: {original}")

    templated = templating.TemplatedAuxilary.generateTemplated(vars, serviceName, varsFromSot['serviceType']['value'])
    #print(f"templated: {templated}")
    
    complianceReportItem = ComplianceReportItem(key=serviceKey, original=original, templated=templated, deviceName=device, footprint=json.dumps(rawCollectionFootprints[device][serviceName]))
    return complianceReportItem

class ComplianceReport(BaseModel):
  __root__: List[ComplianceReportItem] = []

  def append(self, complianceReportItem:ComplianceReportItem):
    self.__root__.append(complianceReportItem)
  
  def __iter__(self):
    return iter(self.__root__)

  @classmethod
  def generate(cls, serviceName, serviceKey, siteID, configsFolder, SOTDB):
    serviceDefinition = definition.ServiceDefinition.parse_file(f"services/serviceDefinitions/{serviceName}.json")

    varsFromSot = sot.getVarsFromSoT(SOTDB, siteID, serviceName, serviceKey)
    if not varsFromSot:
        print(f"can't get SoT values for {serviceName} {serviceKey} for folder {configsFolder}")
        referenceValues = modeling.ReferenceValues()
        referenceValues.append(modeling.ReferenceValue(id='id', value=serviceKey))
    else:
      referenceValues = modeling.getDirectVarsValues(varsFromSot)

    print(json.dumps(varsFromSot, sort_keys=True, indent=4))
    print(referenceValues.json())

"""     rawCollectionConfigs, rawCollectionFootprints = modeling.generateFootprintDB(serviceDefinition, configsFolder, referenceValues)

    complianceReport = ComplianceReport()  
    for device, footprint in rawCollectionFootprints.items():
        if footprint[serviceName]:
          complianceReportItem = ComplianceReportItem.generate(serviceName, serviceKey, varsFromSot, device, footprint, serviceDefinition, rawCollectionConfigs, rawCollectionFootprints)
          complianceReport.append(complianceReportItem)
    
    return complianceReport """

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

from typing import Any, Tuple, List, Dict, Union
from pydantic import BaseModel
import json
import templating 
from dict_hash import dict_hash, hashable, sha256
import definition
from ttpLib import TTPLib
import os
from copy import deepcopy
import sot

class NonRootKey(BaseModel):
  path: Tuple
  keys: List

class NodeReference(BaseModel):
  nodeName: str
  rootKeys: List
  nonRootKeys: List[NonRootKey]

class CheckItem(BaseModel):
  fieldNameToCheck: str
  referenceAliasToRead: str

class CheckReference(BaseModel):
  __root__: List[CheckItem] = []
  
  def append(self, checkItem:CheckItem):
    self.__root__.append(checkItem)
  
  def __iter__(self):
    return iter(self.__root__)

class SetItem(BaseModel):
  fieldNameToSet: Union[str, None]
  referenceAliasToWrite: Union[str, None]

class SetReference(BaseModel):
  __root__: List[SetItem] = []
  
  def append(self, setItem:SetItem):
    self.__root__.append(setItem)
  
  def __iter__(self):
    return iter(self.__root__)

  def __len__(self):
    return len(self.__root__)

class RootKey(BaseModel):
  parent: str
  checkReference: CheckReference
  setReference: SetReference

class RootKeys(BaseModel):
  __root__: List[RootKey]

  def __iter__(self):
    return iter(self.__root__)

  def getRootData(self, parent):
    for rootKey in self:
      if rootKey.parent == parent:
        return rootKey.checkReference, rootKey.setReference

class ReferenceValue(BaseModel):
  id: str
  value: str

class ReferenceValues(BaseModel):
  __root__: List[ReferenceValue] = []
  
  def append(self, referenceValue:ReferenceValue):
    self.__root__.append(referenceValue)
  
  def __iter__(self):
    return iter(self.__root__)
  
  def getReferenceValue(self, id):
    for referenceValue in self:
      if referenceValue.id == id:
        return referenceValue.value
  
  def setReferenceValue(self, object, setReference: SetReference):
    for setItem in setReference:
      value = templating.getDictValueByPath(object, templating.pathTransform(setItem.fieldNameToSet))
      self.append(ReferenceValue(id=setItem.referenceAliasToWrite, value=value))
      print(self.__root__)
    
  def checkObjectByCheckReference(self, object: List, checkReference: CheckReference):
    for item in object:
      ind = True
      for checkItem in checkReference:
        if checkItem.fieldNameToCheck in item:
          if item[checkItem.fieldNameToCheck] == self.getReferenceValue(checkItem.referenceAliasToRead):
            ind = ind and True
          else:
            ind = ind and False
      if ind:
        return item
    return None

  def updateReferenceValues(self, data: Dict):
    for key, value in data.items():
      self.append(ReferenceValue(id=key, value=value))
  
  def updateVarsWithId(self, vars):
    for referenceValue in self:
      if referenceValue.id == 'id':
        vars['id'] = referenceValue.value

class RootElement(BaseModel):
  path: List = []
  rootKeys: RootKeys
  nodesReference: List[NodeReference]

  def getNodeReference(self, nodeName: str):
    for nodeReference in self.nodesReference:
      if nodeReference.nodeName == nodeName:
        return nodeReference.rootKeys, nodeReference.nonRootKeys
    else:
      return None

class RootElements(BaseModel):
  __root__: List[RootElement] = []

  def append(self, rootElement:RootElement):
    self.__root__.append(rootElement)
  
  def __iter__(self):
    return iter(self.__root__)

def getNodeNestedData(object: Dict, keyIndex: int, key: NonRootKey, result: Dict):
  if keyIndex == len(key.path):
    try:
      for key in key.keys:
        if key in object:
          result[key] = object[key]
    except (TypeError, KeyError) as e:
      print(f"{e} with key: {key} result: {result} object: {object}")
    return
  if keyIndex < len(key.path):
    result[key.path[keyIndex]] = {}
    return getNodeNestedData(object[key.path[keyIndex]], keyIndex + 1, key, result[key.path[keyIndex]]) 

def getNodeData(object: Dict, keys: Tuple[Tuple, NonRootKey]):
  result = {}

  rootKeys, nonRootKeys = keys[0], keys[1]

  for rootKey in rootKeys:
    if rootKey in object:
      result[rootKey] = object[rootKey] 
  for nonRootKey in nonRootKeys: 
    getNodeNestedData(object, 0, nonRootKey, result)
  
  return result

def go(object: Dict, rootElement: RootElement, pathIndex: int, candidate: Dict, referenceValues: ReferenceValues):
  try:
    if pathIndex < len(rootElement.path):
      if isinstance(object[rootElement.path[pathIndex]], Dict):
        if pathIndex != len(rootElement.path) - 1:
          candidate[rootElement.path[pathIndex]] = {}
          if keys := rootElement.getNodeReference(rootElement.path[pathIndex]): 
            candidate[rootElement.path[pathIndex]] = getNodeData(object[rootElement.path[pathIndex]], keys)

        return go(object[rootElement.path[pathIndex]], rootElement, pathIndex + 1, candidate[rootElement.path[pathIndex]], referenceValues)

      if isinstance(object[rootElement.path[pathIndex]], List):
        checkReference, _ = rootElement.rootKeys.getRootData(rootElement.path[pathIndex])
        if item := referenceValues.checkObjectByCheckReference(object[rootElement.path[pathIndex]], checkReference):
          if keys := rootElement.getNodeReference(rootElement.path[pathIndex]): 
            candidate[rootElement.path[pathIndex]] = getNodeData(item, keys)
          else:
            candidate[rootElement.path[pathIndex]] = {}
          return go(item, rootElement, pathIndex + 1, candidate[rootElement.path[pathIndex]], referenceValues)

    if pathIndex == len(rootElement.path):
      if keys := rootElement.getNodeReference(rootElement.path[pathIndex-1]):
        candidate.update(getNodeData(object, keys))
        _, setReference = rootElement.rootKeys.getRootData(rootElement.path[pathIndex-1])
        if len(setReference) > 0:
          referenceValues.setReferenceValue(candidate, setReference)
      return True
  except KeyError as e:
    pass
    #print(f"{e}")

def goRef(object: Dict, rootElement: RootElement, candidate: Dict, referenceValues: ReferenceValues):
  if rootElement.path:
    currentNode = rootElement.path[0]

    if currentNode in object:
      if isinstance(object[currentNode], Dict):
        if keys := rootElement.getNodeReference(currentNode): 
          candidate[currentNode] = getNodeData(object[currentNode], keys)
        else:
          candidate[currentNode] = {}

        if len(rootElement.path) == 1:
          _, setReference = rootElement.rootKeys.getRootData(currentNode)
          if len(setReference) > 0:
            referenceValues.setReferenceValue(candidate, setReference)

        rootElement.path.remove(currentNode)
        return goRef(object[currentNode], rootElement, candidate[currentNode], referenceValues)

      if isinstance(object[currentNode], List):
        checkReference, _ = rootElement.rootKeys.getRootData(currentNode)

        if item := referenceValues.checkObjectByCheckReference(object[currentNode], checkReference):
          if keys := rootElement.getNodeReference(currentNode): 
            candidate[currentNode] = getNodeData(item, keys)
          else:
            candidate[currentNode] = {}

          if len(rootElement.path) == 1:
            _, setReference = rootElement.rootKeys.getRootData(currentNode)
            if len(setReference) > 0:
              referenceValues.setReferenceValue(item, setReference)

          rootElement.path.remove(currentNode)
          return goRef(item, rootElement, candidate[currentNode], referenceValues)
  else:
    pass

def getDirectVarsValues(referenceValues: ReferenceValues, soTDBItem: sot.SoTDBItem) -> ReferenceValues:

    processedData = {}
    for variable, definition in soTDBItem.vars.items():
      if definition:
        if definition.type == 'direct':
            processedData[variable] = definition.value 
    
    referenceValues.updateReferenceValues(processedData)
  
    return referenceValues

class Item(BaseModel):
    configHash: str
    config: Dict
    devices: List[str]

def checkEmptyFootprint(di):
    for k in list(di):
        if not di[k]:
            del di[k]
        else:
            if isinstance(di[k], Dict):
                checkEmptyFootprint(di[k])
                if not di[k]:
                    del di[k]

def candidateGenerate(referenceValues: ReferenceValues, parsedData: Dict, serviceDefinition: definition.ServiceDefinition):
    with open(serviceDefinition.footprintDefinition, encoding = 'utf-8') as fi:
        data = fi.read()
        rootElements = RootElements.parse_raw(data) 
    
    candidate = {}

    for rootElement in rootElements:
        #go(parsedData, rootElement, 0, candidate, referenceValues)
        goRef(parsedData, rootElement, candidate, referenceValues)
    
    checkEmptyFootprint(candidate)
    return candidate

def generateFootprint(serviceDefinition: definition.ServiceDefinition, rawConfig, referenceValues):

    parsedData = TTPLib.parser(rawConfig, serviceDefinition.ttpTemplates)
    #print(json.dumps(parsedData, sort_keys=True, indent=4))

    if serviceDefinition.footprintDefinition:
        footprint = candidateGenerate(referenceValues, parsedData, serviceDefinition)
        return footprint

def generateRawCollection(rawInventoryFolder: str) -> Dict:
    devices = [f.name for f in os.scandir(rawInventoryFolder) if f.is_dir()]

    rawCollection = {}

    for device in devices:
        try:
            with open(f"{rawInventoryFolder}/{device}/{device}-running.txt", encoding = 'utf-8') as f:
                rawConfig = f.read()
                rawCollection[device] = rawConfig

        except Exception as e:
            print(f"{e}")
            exit()
    
    return rawCollection
        
def processRawCollection(serviceDefinition: definition.ServiceDefinition, rawInventoryFolder: str, referenceValues: ReferenceValues) -> Tuple[Dict, Dict]:
    
    rawCollection = generateRawCollection(rawInventoryFolder)
    rawCollectionFootprints = {}

    for device, rawConfig in rawCollection.items():
        #print(f"go for device: {device}")
        referenceValuesOriginal = deepcopy(referenceValues)
        footprint = generateFootprint(serviceDefinition, rawConfig, referenceValuesOriginal)
        print(json.dumps(footprint, sort_keys=True, indent=4))
        rawCollectionFootprints[device] = footprint
    return (rawCollection, rawCollectionFootprints)

def generateFootprintDB(serviceDefinition: definition.ServiceDefinition, rawInventoryFolder: str, referenceValues: ReferenceValues) -> Tuple[Dict, Dict]:

    rawCollectionConfigs, rawCollectionFootprints = processRawCollection(serviceDefinition, rawInventoryFolder, referenceValues)
    
    return (rawCollectionConfigs, rawCollectionFootprints)

def generateConsistencyDB(rawCollectionFootprints: Dict) -> Dict:
    consistencyHashSet = {}
    for device, config in rawCollectionFootprints.items():
        configHash = sha256(config)
        if configHash not in consistencyHashSet:
            consistencyHashSet[configHash] = Item(configHash=configHash, config=config, devices = [device])
        else:
            item = consistencyHashSet[configHash]
            item.devices.append(device)
    return consistencyHashSet

def generateTTPDB(serviceName: str, rawInventoryFolder: str):
  serviceDefinition = definition.ServiceDefinition.parse_file(f"services/serviceDefinitions/{serviceName}.json")
  rawCollection = generateRawCollection(rawInventoryFolder)
  for device, rawConfig in rawCollection.items():
    parsedData = TTPLib.parser(rawConfig, serviceDefinition.ttpTemplates)
    print(f"Parsed data for device: {device}")
    print(json.dumps(parsedData, sort_keys=True, indent=4))


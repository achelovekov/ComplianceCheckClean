
from typing import Any, Tuple, List, Dict, Union
from pydantic import BaseModel

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
      self.append(ReferenceValue(id=setItem.referenceAliasToWrite, value=object[setItem.fieldNameToSet]))
    
  def checkObjectByCheckReference(self, object: List, checkReference: CheckReference):
    for item in object:
      ind = True
      for checkItem in checkReference:
        if item[checkItem.fieldNameToCheck] == self.getReferenceValue(checkItem.referenceAliasToRead):
          ind = ind and True
        else:
          ind = ind and False
      if ind:
        return item
    return None

class RootElement(BaseModel):
  path: Tuple = ()
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
    for key in key.keys:
      result[key] = object[key]
    return
  if keyIndex < len(key.path):
    result[key.path[keyIndex]] = {}
    return getNodeNestedData(object[key.path[keyIndex]], keyIndex + 1, key, result[key.path[keyIndex]]) 

def getNodeData(object: Dict, keys: Tuple[Tuple, NonRootKey]):
  result = {}

  rootKeys, nonRootKeys = keys[0], keys[1]
  
  for rootKey in rootKeys:
    result[rootKey] = object[rootKey] 
  for nonRootKey in nonRootKeys: 
    getNodeNestedData(object, 0, nonRootKey, result)
  
  return result

def go(object: Dict, rootElement: RootElement, pathIndex: int, candidate: Dict, referenceValues: ReferenceValues):
  if pathIndex < len(rootElement.path):
    try:
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
    except KeyError as e:
      pass  
    if pathIndex == len(rootElement.path):
      if keys := rootElement.getNodeReference(rootElement.path[pathIndex-1]):
        candidate.update(getNodeData(object, keys))
        _, setReference = rootElement.rootKeys.getRootData(rootElement.path[pathIndex-1])
        if len(setReference) > 0:
          referenceValues.setReferenceValue(candidate, setReference)
      return True


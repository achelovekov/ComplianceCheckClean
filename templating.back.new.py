import yaml
from typing import Any, Dict, List, Optional
import re 
from string import Template
import json
import jinja2
from stree import *
from pydantic import BaseModel
import sot


def getVarsFromSoT(filename, siteID, serviceName, key) -> Dict:

    serviceSoT = sot.ServiceSoT.parse_file(filename)
    return serviceSoT.getVarsByKey(serviceName, siteID, key)

def processVariables(data:Dict, originalData:Dict):

    def getDictValueByPath(data:Dict, path:List) -> Any:
        try:
            return getDictValueByPath(data[path[0]], path[1:]) if path else data
        except KeyError as e:
            return "$MUSTEXISTINSOURCEVAR"

    def pathTransform(data:str):
        return data.split('/')

    newData = {}
    regex = '\${([a-zA-Z]+)}'
    for variable, definition in data.items():
        if definition['type'] == 'direct' and 'value' in definition:
            newData[variable] = definition['value'] 
        if definition['type'] == 'direct' and 'values' in definition:
            newData[variable] = li = []
            for value in definition['values']:
                li.append(value)
        if definition['type'] == 'relative':
            mapping = {}
            template = Template(definition['value'])
            for item in re.finditer(regex, definition['value']):
                mapping[item.group(1)] = newData[item.group(1)]
            newData[variable] = template.substitute(**mapping)
        if definition['type'] == 'source':
            template = Template(definition['value'])
            mapping = {}
            for item in re.finditer(regex, definition['value']):
                if item.group(1) == 'var':
                    mapping[item.group(1)] = getDictValueByPath(originalData, pathTransform(definition['path']))
                else: 
                    mapping[item.group(1)] = newData[item.group(1)]
            newData[variable] = template.substitute(**mapping)

    return newData

class STreeServiceProcessedItem(BaseModel):
    prefix: str = ''
    path: Optional[List[str]] = []
    filter: Optional[List[str]] = []
    parent: Optional['STreeServiceProcessedItem']

STreeServiceProcessedItem.update_forward_refs()

class STreeServiceProcessed(BaseModel):
    __root__: List[STreeServiceProcessedItem] = []

    def append(self, sTreeServiceProcessedItem:STreeServiceProcessedItem):
        self.__root__.append(sTreeServiceProcessedItem)
  
    def __iter__(self):
        return iter(self.__root__)

    def __len__(self):
        return len(self.__root__)

class STreeServiceItem(BaseModel):
    prefix: str
    path: Optional[str]
    filter: Optional[List[str]]
    parent: Optional['STreeServiceItem']

STreeServiceItem.update_forward_refs()

class STreeService(BaseModel):
    __root__: List[STreeServiceItem] = []

    def append(self, sTreeServiceItem:STreeServiceItem):
        self.__root__.append(sTreeServiceItem)
  
    def __iter__(self):
        return iter(self.__root__)

    def processString(self, src, regex, vars):
        try:
            mapping = {}
            template = Template(src)
            for item in re.finditer(regex, src):
                mapping[item.group(1)] = vars[item.group(1)]

            return template.substitute(**mapping)
        except KeyError as e:
            print(f"{e}. Please check the vars definitions")

    def processItem(self, sTreeServiceItem: STreeServiceItem, regex: str, vars: Dict):
        sTreeServiceProcessedItem = STreeServiceProcessedItem()
        sTreeServiceProcessedItem.prefix = self.processString(sTreeServiceItem.prefix, regex, vars)
        if sTreeServiceItem.path:  
            sTreeServiceProcessedItem.path = self.processString(sTreeServiceItem.path, regex, vars).split()
        if sTreeServiceItem.filter: 
            sTreeServiceProcessedItem.filter = sTreeServiceItem.filter

        if sTreeServiceItem.parent:
            sTreeServiceProcessedItem.parent = self.processItem(sTreeServiceItem.parent, regex, vars)
        
        return sTreeServiceProcessedItem

    def process(self, vars):
        regex = '\${([a-zA-Z]+)}'
        sTreeServiceProcessed = STreeServiceProcessed()

        for sTreeServiceItem in self:
            sTreeServiceProcessedItem = self.processItem(sTreeServiceItem, regex, vars)
            sTreeServiceProcessed.append(sTreeServiceProcessedItem)
            
        return sTreeServiceProcessed

class PrintedStreeItem(BaseModel):
    prefix: str
    content: List[str] = None
    parent: Optional['PrintedStreeItem'] = None

PrintedStreeItem.update_forward_refs()

def processItem(rootNode: Node, sTreeServiceProcessedItem: STreeServiceProcessedItem, nonEmpty: bool) -> PrintedStreeItem:

    if sTreeServiceProcessedItem.path:
        printBuf = printPath(rootNode, sTreeServiceProcessedItem.path, sTreeServiceProcessedItem.filter)
    else:
        printBuf = []

    if printBuf:
        nonEmpty = nonEmpty or True
    
    if nonEmpty:

        printedStreeItem = PrintedStreeItem(prefix=sTreeServiceProcessedItem.prefix, content=printBuf)

        if sTreeServiceProcessedItem.parent:
            printedStreeItem.parent = processItem(rootNode, sTreeServiceProcessedItem.parent, nonEmpty)
        
        return printedStreeItem 

def indentList(li: List):
    for index, item in enumerate(li):
        li[index] = "  " + item

def printItemPart(bias: bool, printedStreeItem: PrintedStreeItem, buf: List):
    res = []
    res.append(printedStreeItem.prefix)

    for line in printedStreeItem.content:
        res.append(line)

    buf[:0] = res
    if bias:
        indentList(buf)

def printItem(printedStreeItem: PrintedStreeItem, buf: str):
    if printedStreeItem.parent:
        bias = True
    else:
        bias = False
    
    printItemPart(bias, printedStreeItem, buf)

    if printedStreeItem.parent:
        printItem(printedStreeItem.parent, buf)

def genereteStreeOriginal(sTreeServiceProcessed: STreeServiceProcessed, rootNode: Node, result: List):

    for _, sTreeServiceProcessedItem in enumerate(sTreeServiceProcessed):
        nonEmpty = False
        printedStreeItem = processItem(rootNode, sTreeServiceProcessedItem, nonEmpty) 
        if printedStreeItem: 
            buf = []    
            printItem(printedStreeItem, buf)
            result.extend(buf)

class ServiceTemplatePerType(BaseModel):
    serviceName: str
    serviceType: str
    serviceTemplate: str

class ServiceTemplatesPerType(BaseModel):
    __root__: List[ServiceTemplatePerType] = []

    def append(self, serviceTemplatePerType:ServiceTemplatePerType):
        self.__root__.append(serviceTemplatePerType)
  
    def __iter__(self):
        return iter(self.__root__)

    def __len__(self):
        return len(self.__root__)

class TemplatedAuxilary():

    serviceTemplatesPerType = ServiceTemplatesPerType()

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='L3VNI',
                    serviceType='type-1', 
                    serviceTemplate="""
vlan {{ vars['sviId'] }}
  name VRF_{{ vars['id'] }}
  vn-segment {{ vars['vni'] }}
vrf context {{ vars['id'] }}
  vni {{ vars['vni'] }}
  rd auto
  address-family ipv4 unicast
    route-target import {{ vars['asNum'] }}:{{ vars['vni'] }}
    route-target import {{ vars['asNum'] }}:{{ vars['vni'] }} evpn
    route-target export {{ vars['asNum'] }}:{{ vars['vni'] }}
    route-target export {{ vars['asNum'] }}:{{ vars['vni'] }} evpn
router bgp {{ vars['asNum'] }}
  vrf {{ vars['id'] }}
    address-family ipv4 unicast
      redistribute direct route-map {{ vars['redistributeDirectRMap'] }}
      maximum-paths ibgp 4
"""))


    @classmethod
    def getTemplateByServiceNameAndType(cls, serviceName: str, serviceType: str) -> str:
        for item in cls.serviceTemplatesPerType:
            if item.serviceName == serviceName and item.serviceType == serviceType:
                return item.serviceTemplate
        return None

    @classmethod
    def generateTemplated(cls, vars: Dict, serviceName: str, serviceType: str):
        template = cls.getTemplateByServiceNameAndType(serviceName, serviceType)
        j2_inventory_template = jinja2.Template(template)

        return j2_inventory_template.render(vars=vars)
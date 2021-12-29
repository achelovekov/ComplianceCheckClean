import yaml
from typing import Any, Dict, List
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
    path: List[str] = []
    filter: List[str] = []
    bias: bool = False

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
    path: str
    filter: List[str]
    bias: bool

class STreeService(BaseModel):
    __root__: List[STreeServiceItem] = []

    def append(self, sTreeServiceItem:STreeServiceItem):
        self.__root__.append(sTreeServiceItem)
  
    def __iter__(self):
        return iter(self.__root__)

    def process(self, vars):
        regex = '\${([a-zA-Z]+)}'

        def processString(src, regex):
            try:
                mapping = {}
                template = Template(src)
                for item in re.finditer(regex, src):
                    mapping[item.group(1)] = vars[item.group(1)]

                return template.substitute(**mapping)
            except KeyError as e:
                print(f"{e}. Please check the vars definitions")
        sTreeServiceProcessed = STreeServiceProcessed()

        for sTreeServiceItem in self:
            sTreeServiceProcessedItem = STreeServiceProcessedItem()
           
            sTreeServiceProcessedItem.prefix = processString(sTreeServiceItem.prefix, regex)
            sTreeServiceProcessedItem.path = processString(sTreeServiceItem.path, regex).split()
            sTreeServiceProcessedItem.filter = sTreeServiceItem.filter
            sTreeServiceProcessedItem.bias = sTreeServiceItem.bias

            sTreeServiceProcessed.append(sTreeServiceProcessedItem)
            
        return sTreeServiceProcessed

def indentBlock(step:int, bias:int, prefix:str, block:str):
    res = []
    prefix = " "*step*bias + prefix
    res.append(prefix)
    for line in block:
        line = " "*step*bias + line
        res.append(line)
    return '\n'.join(res)

def genereteStreeOriginal(sTreeServiceProcessed: STreeServiceProcessed, config: str):
        
    rootNode = streeFromConfig(config)

    result = ''
    for index, sTreeServiceProcessedItem in enumerate(sTreeServiceProcessed):
        printBuf = printPath(rootNode, sTreeServiceProcessedItem.path, sTreeServiceProcessedItem.filter)
        if printBuf:
            result += indentBlock(2, sTreeServiceProcessedItem.bias, sTreeServiceProcessedItem.prefix, printBuf)
            if index != len(sTreeServiceProcessed) - 1:
                result += '\n'

    return result


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
  graceful-restart stalepath-time 1800
  address-family ipv4 unicast
    redistribute direct route-map RM-REDIST-SUBNET-{{ vars['id'] }}
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
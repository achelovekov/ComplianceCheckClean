import yaml
from typing import Any, Dict, List, Optional
import re 
from string import Template
import json
import jinja2
from stree import *
from pydantic import BaseModel
import sot

def getDictValueByPath(data:Dict, path:List) -> Any:
    try:
        return getDictValueByPath(data[path[0]], path[1:]) if path else data
    except KeyError as e:
        return "$MUSTEXISTINSOURCEVAR"

def pathTransform(data:str):
    return data.split('/')

def processVariables(soTDBItem: sot.SoTDBItem, fooprint:Dict):

    newData = {}
    regex = '\${([a-zA-Z]+)}'
    for variable, definition in soTDBItem.vars.items():
        try:
            if definition:
                if definition.type == 'direct' and definition.value:
                    newData[variable] = definition.value
                if definition.type == 'direct' and definition.values:
                    newData[variable] = li = []
                    for value in definition.values:
                        li.append(value)
                if definition.type == 'relative':
                    mapping = {}
                    template = Template(definition.value)
                    for item in re.finditer(regex, definition.value):
                        mapping[item.group(1)] = newData[item.group(1)]
                    newData[variable] = template.substitute(**mapping)
                if definition.type == 'source':
                    template = Template(definition.value)
                    mapping = {}
                    for item in re.finditer(regex, definition.value):
                        if item.group(1) == 'var':
                            mapping[item.group(1)] = getDictValueByPath(fooprint, pathTransform(definition.path))
                        else: 
                            mapping[item.group(1)] = newData[item.group(1)]
                    newData[variable] = template.substitute(**mapping)
        except TypeError as e:
            print(f"may be ttpLib parsing error with {variable} {definition}")

    return newData

class STreeServiceProcessedItem(BaseModel):
    path: List[str] = []
    filter: Union[List[str], str] = []
    let:  Union[List[str], str] = []
    pathPrepend: Optional[bool] 
    children: Optional[List['STreeServiceProcessedItem']] = []

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
    path: str
    filter: Union[List[str], str]
    let:  Union[List[str], str]
    children: Optional[List['STreeServiceItem']]
    pathPrepend: Optional[bool] = False

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
        sTreeServiceProcessedItem.path = self.processString(sTreeServiceItem.path, regex, vars).split()

        sTreeServiceProcessedItem.filter = sTreeServiceItem.filter
        sTreeServiceProcessedItem.let = sTreeServiceItem.let
        if sTreeServiceItem.pathPrepend:
            sTreeServiceProcessedItem.pathPrepend = sTreeServiceItem.pathPrepend

        if sTreeServiceItem.children:
            for child in sTreeServiceItem.children:
                sTreeServiceProcessedItem.children.append(self.processItem(child, regex, vars))
        
        return sTreeServiceProcessedItem

    def process(self, vars):
        regex = '\${([a-zA-Z]+)}'
        sTreeServiceProcessed = STreeServiceProcessed()

        for sTreeServiceItem in self:
            sTreeServiceProcessedItem = self.processItem(sTreeServiceItem, regex, vars)
            sTreeServiceProcessed.append(sTreeServiceProcessedItem)
            
        return sTreeServiceProcessed

def printItem(prefix: str, content: List, bias: int):
    res = []
    if prefix:
        prefix = " "*2*bias + ' '.join(prefix)
        res.append(prefix)
    for line in content:
        line = " "*2*bias + line
        res.append(line)
    return '\n'.join(res)

def processItem(rootNode: Node, sTreeServiceProcessedItem: STreeServiceProcessedItem, bias: int, path: List, buf: List[str], indicator: Dict):
    path = path + sTreeServiceProcessedItem.path
    if "all" in sTreeServiceProcessedItem.filter:
        printBuf = []
    else:
        printBuf = printPath(rootNode, path, sTreeServiceProcessedItem.filter, sTreeServiceProcessedItem.let, sTreeServiceProcessedItem.pathPrepend)
    
    if (sTreeServiceProcessedItem.children or printBuf):
        if sTreeServiceProcessedItem.pathPrepend:
            buf.append(printItem(None, printBuf, bias))
        else: 
            buf.append(printItem(sTreeServiceProcessedItem.path, printBuf, bias))

    if sTreeServiceProcessedItem.children:
        for child in sTreeServiceProcessedItem.children:
            processItem(rootNode, child, bias+1, path, buf, indicator)
    if printBuf:
        indicator['hasResult'] = True

def genereteStreeOriginal(sTreeServiceProcessed: STreeServiceProcessed, rootNode: Node, result: List[str]):

    for _, sTreeServiceProcessedItem in enumerate(sTreeServiceProcessed):
        bias = 0
        path = []
        indicator = {'hasResult': False}
        buf = []
        processItem(rootNode, sTreeServiceProcessedItem, bias, path, buf, indicator)
        if indicator['hasResult']:
            result.append('\n'.join(buf))

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
                ServiceTemplatePerType(serviceName='l3vni',
                    serviceType='type-1', 
                    serviceTemplate="""
vlan {{ vars['sviId'] }}
  name L3_BLABLA{{ vars['idNum'] }}
  vn-segment {{ vars['vni'] }}
vrf context {{ vars['id'] }}
  vni {{ vars['vni'] }}
  rd auto
  address-family ipv4 unicast
    route-target both auto
    route-target both auto evpn
router bgp {{ vars['asNum'] }}
  vrf {{ vars['id'] }}
    address-family ipv4 unicast
      redistribute direct route-map {{ vars['redistributeDirectRMap'] }}
      maximum-paths 2
route-map {{ vars['redistributeDirectRMap'] }} permit {{ vars['redistributeDirectRMapSeq']}}
  match tag {{ vars['idNum']}}
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='l2vni',
                    serviceType='type-1', 
                    serviceTemplate="""
vlan 1202
  name NTNX-MGMT
  vn-segment 2751202
interface nve1
  no shutdown
  description VTEP [1][NVE]
  host-reachability protocol bgp
  source-interface loopback1
  member vni 227952
    suppress-arp
    mcast-group 239.255.0.20
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='L3VNSBER',
                    serviceType='type-1', 
                    serviceTemplate="""
vlan {{ vars['sviId'] }}
  name VRF_{{ vars['id'] }}
  vn-segment {{ vars['vni'] }}
vrf context {{ vars['id'] }}
  vni {{ vars['vni'] }}
  rd auto
  address-family ipv4 unicast
    route-target both auto
    route-target both auto evpn
router bgp {{ vars['asNum'] }}
  vrf {{ vars['id'] }}
    {% if vars['routerId'] != "none" -%}
    router-id {{ vars['routerId'] }}
    {% endif -%}
    graceful-restart stalepath-time {{ vars['stalePathTime'] }}
    {% if vars['multipathRelax'] -%}
    bestpath as-path multipath-relax
    {% endif -%}
    address-family ipv4 unicast
      redistribute direct route-map {{ vars['redistributeDirectRMap'] }}
      maximum-paths ibgp 4
route-map {{ vars['redistributeDirectRMap'] }} permit {{ vars['redistributeDirectRMapSeq']}}
  match tag {{ vars['idNum']}}
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='underlayInterface',
                    serviceType='type-1', 
                    serviceTemplate="""
interface {{ vars['id'] }}
  description {{ vars['description'] }}
  mtu 9216
  no ip redirects
  ip address {{ vars['ipAddress'] }}
  no ipv6 redirects
  ip ospf authentication message-digest
  ip ospf message-digest-key 1 md5 3 {{ vars['ospfMD5Key'] }}
  ip ospf network point-to-point
  no ip ospf passive-interface
  ip router ospf UNDERLAY area 0.0.0.0
  ip ospf bfd
  ip pim bfd-instance
  ip pim sparse-mode
  no shutdown
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='ospf',
                    serviceType='type-1', 
                    serviceTemplate="""
router ospf {{ vars['id'] }}
  bfd
  router-id {{ vars['routerId'] }}
  log-adjacency-changes
  timers throttle spf 10 100 5000
  timers lsa-group-pacing {{ vars['lsaGroupPacing'] }}
  timers lsa-arrival {{ vars['lsaArrival'] }}
  timers throttle lsa 10 100 5000
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='loopbackInterface',
                    serviceType='type-1', 
                    serviceTemplate="""
interface {{ vars['id'] }}
  description {{ vars['description'] }}
  ip address {{ vars['ipAddress'] }}
  ip router ospf UNDERLAY area 0.0.0.0
  ip pim sparse-mode
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='bfd',
                    serviceType='type-1', 
                    serviceTemplate="""
feature bfd
bfd interval 250 min_rx 250 multiplier 3
"""))

    serviceTemplatesPerType.append(
                ServiceTemplatePerType(serviceName='pim',
                    serviceType='type-1', 
                    serviceTemplate="""
feature pim
ip pim rp-address {{ vars['rpAddress'] }} group-list 239.255.0.0/24
ip pim ssm range 232.0.0.0/8
ip pim bfd
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
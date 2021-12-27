from dict_hash import dict_hash, hashable, sha256
from typing import Any, Dict, List
from pydantic import BaseModel
import hashlib
from modeling import *
from definition import Service
from ttpLib import TTPLib
import os

class Item(BaseModel):
    configHash: str
    config: Dict
    devices: List[str]

def candidateGenerate(referenceValues: ReferenceValues, parsedData: Dict, service: Service):
    with open(referenceValues, encoding = 'utf-8') as f:
        data = f.read()
        referenceValues = ReferenceValues.parse_raw(data) 
        
    with open(service.footprintDefinition, encoding = 'utf-8') as fi:
        data = fi.read()
        rootElements = RootElements.parse_raw(data) 
    
    candidate = {}

    for rootElement in rootElements:
        go(parsedData, rootElement, 0, candidate, referenceValues)
    
    #print(json.dumps(candidate, sort_keys=True, indent=4))
    return candidate

def generateFootprint(service: Service, footprint: Dict, rawConfig, referenceValues):
    if service.subServices:
        for subService in service.subServices:
            generateFootprint(subService, footprint, rawConfig, referenceValues)
    else:
        parsedData = TTPLib.parser(rawConfig, service.ttpTemplates)
        #print(json.dumps(parsedData, sort_keys=True, indent=4))

    if service.footprintDefinition:
        footprint[service.serviceName] = candidateGenerate(referenceValues, parsedData, service)

def parseRawCollection(rawInventoryFolder: str) -> Dict:
    devices = [f.name for f in os.scandir(rawInventoryFolder) if f.is_dir()]

    rawCollection = {}

    for device in devices:
        try:
            with open(f"{rawInventoryFolder}/{device}/{device}-running.txt", encoding = 'utf-8') as f:
                data = f.read()
                rawCollection[device] = data

        except Exception as e:
            print(f"{e}")
            exit()
    
    return rawCollection
        
def processRawCollection(service: Service, rawInventoryFolder: str) -> Tuple[Dict, Dict]:
    
    rawCollectionConfigs = parseRawCollection(rawInventoryFolder)
    rawCollectionFootprints = {}

    for device, rawConfig in rawCollectionConfigs.items():
        footprint = {}
        generateFootprint(service, footprint, rawConfig, 'referenceValues.json')
        #print(json.dumps(footprint, sort_keys=True, indent=4))
        rawCollectionFootprints[device] = footprint
    return (rawCollectionConfigs, rawCollectionFootprints)

def consistency(service: Service, rawInventoryFolder: str) -> Tuple[Dict, Dict, Dict]:

    rawCollectionConfigs, rawCollectionFootprints = processRawCollection(service, rawInventoryFolder)

    footprintHashSet = {}
    for device, config in rawCollectionFootprints.items():
        configHash = sha256(config)
        if configHash not in footprintHashSet:
            footprintHashSet[configHash] = Item(configHash=configHash, config=config, devices = [device])
        else:
            item = footprintHashSet[configHash]
            item.devices.append(device)
    
    return (rawCollectionConfigs, rawCollectionFootprints, footprintHashSet)


        

from ttpLib import TTPLib
import json
from modeling import *
from definition import Service
import os
from consistency import consistency

def generateFootprint(service: Service, result: Dict, rawConfig, referenceValues):
    if service.subServices:
        for subService in service.subServices:
            generateFootprint(subService, result, rawConfig, referenceValues)
    else:
        parsedData = TTPLib.parser(rawConfig, service.ttpTemplates)

    if service.footprintDefinition:
        with open(referenceValues, encoding = 'utf-8') as f:
            data = f.read()
            referenceValues = ReferenceValues.parse_raw(data) 
        
        with open(service.footprintDefinition, encoding = 'utf-8') as fi:
            data = fi.read()
            rootElements = RootElements.parse_raw(data) 
        
        candidate = {}
        for rootElement in rootElements:
            go(parsedData, rootElement, 0, candidate, referenceValues)
        result[service.serviceName] = candidate

def parseRawCollection(rawInventoryFolder):
    devices = [f.name for f in os.scandir(rawInventoryFolder) if f.is_dir()]

    di = {}

    for device in devices:
        try:
            with open(f"{rawInventoryFolder}/{device}/{device}-running.txt", encoding = 'utf-8') as f:
                data = f.read()
                di[device] = data

        except Exception as e:
            print(f"{e}")
            exit()
    
    return di
        
def processRawCollection(serviceName: str, rawInventoryFolder: str):
    
    rawCollection = parseRawCollection(rawInventoryFolder)
    result = {}

    service = Service.parse_file(f'services/{serviceName}/definition.json')

    for device, rawConfig in rawCollection.items():
        footprint = {}
        generateFootprint(service, footprint, rawConfig, 'referenceValues.json')
        
        result[device] = footprint
    return result

result = processRawCollection('VNI', 'RawConfigs/Site2')

re = consistency(result)

for k, v in re.items():
    print(k, v.devices)
    print(json.dumps(v.config, sort_keys=True, indent=4))
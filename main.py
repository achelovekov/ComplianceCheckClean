
from ttpLib import TTPLib
import json
from modeling import *
from definition import Service
import os
from consistency import *
from templating import *

serviceName = 'L3VNI'
service = Service.parse_file(f'services/serviceDefinitions/{serviceName}.json')
sTreeService = STreeService.parse_file(service.streeDefinition)

rawCollectionConfigs, rawCollectionFootprints, footprintHashSet = consistency(service, 'RawConfigs/Site6')
data = getVarsFromSoT('dataModel.json', '014', 'L3VNI', 'e14Z')

""" for k, v in footprintHashSet.items():
    print(k, v.devices)
    print(json.dumps(v.config, sort_keys=True, indent=4)) """

for device, footprint in rawCollectionFootprints.items():
    vars = processVariables(data, footprint[serviceName])
    sTreeServiceProcessed = sTreeService.process(vars)
    src = genereteStreeOriginal(sTreeServiceProcessed, f"RawConfigs/Site6/{device}/{device}-running.txt")
    dst = TemplatedAuxilary.generateTemplated(vars, serviceName)

    print(src)
    print(dst)
    print("============")
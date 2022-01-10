

from ttpLib import TTPLib
from modeling import *
from definition import Service
from consistency import *
from templating import *

serviceName = 'L3VNI'
serviceKey = 'PROD-SRV-APP'
service = Service.parse_file(f'services/serviceDefinitions/{serviceName}.json')
sTreeService = STreeService.parse_file(service.streeDefinition)

print(sTreeService)

rawCollectionConfigs, rawCollectionFootprints, footprintHashSet = consistency(service, 'RawConfigs/tmpTest', 'referenceValues.json')

""" for k, v in footprintHashSet.items():
    print(k)
    print(v.devices)
    print(json.dumps(v.config, sort_keys=True, indent=4)) """

varsFromSot = getVarsFromSoT('dataModel.json', '014', serviceName, serviceKey)
serviceType = varsFromSot['serviceType']['value']

if not varsFromSot:
    print("can't get SoT")
    exit()

complianceReport = ComplianceReport()

for device, footprint in rawCollectionFootprints.items():
    vars = processVariables(varsFromSot, footprint[serviceName])
    sTreeServiceProcessed = sTreeService.process(vars)
    rootNode = streeFromConfig(rawCollectionConfigs[device])
    result = []
    genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)

print('\n'.join(result))


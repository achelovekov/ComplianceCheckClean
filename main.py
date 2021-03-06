
from re import template
from ttpLib import TTPLib
from modeling import *
from definition import Service
from consistency import *
from templating import *

serviceName = 'L3VNI'
serviceKey = 'PROD-SRV-APP'
service = Service.parse_file(f'services/serviceDefinitions/{serviceName}.json')
sTreeService = STreeService.parse_file(service.streeDefinition)

rawCollectionConfigs, rawCollectionFootprints, footprintHashSet = consistency(service, 'RawConfigs/tmp', 'referenceValues.json')

for k, v in footprintHashSet.items():
    print(k)
    print(v.devices)
    print(json.dumps(v.config, sort_keys=True, indent=4))

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
    templated = TemplatedAuxilary.generateTemplated(vars, serviceName, serviceType)
    genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)
    original = '\n'.join(result)
    complianceReportItem = ComplianceReportItem(key=serviceKey, original=original, templated=templated, deviceName=device, footprint=json.dumps(rawCollectionFootprints[device][serviceName]))
    complianceReport.append(complianceReportItem)

print(complianceReport.json())
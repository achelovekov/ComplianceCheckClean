
from re import template
from ttpLib import TTPLib
from modeling import *
from definition import Service
from consistency import *
from templating import *

serviceName = 'L3VNI'
serviceKey = 'eAZ'
service = Service.parse_file(f'services/serviceDefinitions/{serviceName}.json')
sTreeService = STreeService.parse_file(service.streeDefinition)

rawCollectionConfigs, rawCollectionFootprints, footprintHashSet = consistency(service, 'RawConfigs/Site4')

data = getVarsFromSoT('dataModel.json', '014', serviceName, serviceKey)

if not data:
    print("can't get SoT")
    exit()

complianceReport = ComplianceReport()

for device, footprint in rawCollectionFootprints.items():
    vars = processVariables(data, footprint[serviceName])
    sTreeServiceProcessed = sTreeService.process(vars)
    original = genereteStreeOriginal(sTreeServiceProcessed, rawCollectionConfigs[device])
    templated = TemplatedAuxilary.generateTemplated(vars, serviceName)

    complianceReportItem = ComplianceReportItem(key=serviceKey, original=original, templated=templated, deviceName=device, footprint=json.dumps(rawCollectionFootprints[device][serviceName]))
    complianceReport.append(complianceReportItem)

print(complianceReport.json())
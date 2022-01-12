
from re import template
from ttpLib import TTPLib
from modeling import *
from definition import Service
from consistency import *
from templating import *

serviceName = 'L3VNI'
serviceKey = 'PROD-SRV-APP'
siteID = 'VTB'
configsFolder = 'RawConfigs/configTest'
service = Service.parse_file(f"services/serviceDefinitions/{serviceName}.json")
sTreeService = STreeService.parse_file(service.streeDefinition)
referenceValuesFilename = 'referenceValues.json'
with open(referenceValuesFilename, encoding = 'utf-8') as f:
    data = f.read()
    referenceValues = ReferenceValues.parse_raw(data) 

varsFromSot = getVarsFromSoT('dataModel.json', siteID, serviceName, serviceKey)
if not varsFromSot:
    print(f"can't get SoT values for {serviceName} {serviceKey} for folder {configsFolder}")
    exit()

print(json.dumps(varsFromSot, sort_keys=True, indent=4))
referenceValues.updateReferenceValues(getDirectVarsValues(varsFromSot))
print(referenceValues.json())

rawCollectionConfigs, rawCollectionFootprints, footprintHashSet = consistency(service, configsFolder, referenceValues)

""" for k, v in footprintHashSet.items():
    print(k)
    print(v.devices)
    print(json.dumps(v.config, sort_keys=True, indent=4)) """

for device, footprint in rawCollectionFootprints.items():
    print(device)
    print(json.dumps(footprint[serviceName], sort_keys=True, indent=4))


serviceType = varsFromSot['serviceType']['value']

complianceReport = ComplianceReport()


for device, footprint in rawCollectionFootprints.items():
    if footprint[serviceName]:
        vars = processVariables(varsFromSot, footprint[serviceName])
        sTreeServiceProcessed = sTreeService.process(vars)
        rootNode = streeFromConfig(rawCollectionConfigs[device])
        templated = TemplatedAuxilary.generateTemplated(vars, serviceName, serviceType)
        print(f"templated: {templated}")
        result = []
        genereteStreeOriginal(sTreeServiceProcessed, rootNode, result)
        original = '\n'.join(result)
        print(f"original: {original}")
        complianceReportItem = ComplianceReportItem(key=serviceKey, original=original, templated=templated, deviceName=device, footprint=json.dumps(rawCollectionFootprints[device][serviceName]))
        complianceReport.append(complianceReportItem)

print(complianceReport.json())  

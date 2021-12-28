

import definition 
import consistency
import templating

serviceName = 'L3VNI'
#serviceKey = 'eAZ'
service = definition.Service.parse_file(f'services/serviceDefinitions/{serviceName}.json')
sTreeService = templating.STreeService.parse_file(service.streeDefinition)
rawInventoryFolder = f'RawConfigs'
site = 'Site6'
device = 'SKO-DATA-AC-014-H31-01-EXT'
footprint = {}
referenceValues = f'referenceValues.json'

try:
    with open(f"{rawInventoryFolder}/{site}/{device}/{device}-running.txt", encoding = 'utf-8') as f:
        rawConfig = f.read()

except Exception as e:
    print(f"{e}")
    exit()

consistency.generateFootprint(service, footprint, rawConfig, referenceValues)
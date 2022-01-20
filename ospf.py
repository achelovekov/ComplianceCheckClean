import json
import compliance
import definition

serviceName = 'ospf'
keys = definition.KeysDefinition()
keys.append(definition.KeyDefinition(footprintKey='UNDERLAY', SoTKey='general'))

siteID = 'VTB'
configsFolder = 'RawConfigs/configTest'
SOTDB = 'dataModel.json' 


#compliance.TTPDB.generate(serviceName, configsFolder)

""" consistencyReport = compliance.ConsistencyReport.generate(serviceName, footprintKey, siteID, configsFolder, SOTDB)
for k, v in consistencyReport.items():
  print(k)
  print(v.devices)
  print(json.dumps(v.config, sort_keys=True, indent=4))    """


complianceReport = compliance.ComplianceReport()  

serviceDefinition = definition.ServiceDefinition.parse_file(f"services/serviceDefinitions/{serviceName}.json")

complianceReport.generate(serviceName, keys, siteID, configsFolder, SOTDB, serviceDefinition)

for item in complianceReport:
  item.footprint = json.dumps(item.footprint) 

print(complianceReport.json())


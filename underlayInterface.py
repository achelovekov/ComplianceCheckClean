import json
import compliance
import modeling
import definition

serviceName = 'UnderlayInterface'
footprintKeys = ['Ethernet1/51', 'Ethernet1/52']
serviceSotKey = 'general'
siteID = 'VTB'
configsFolder = 'RawConfigs/configTestNew'
SOTDB = 'dataModel.json' 


compliance.TTPDB.generate(serviceName, configsFolder)

""" consistencyReport = compliance.ConsistencyReport.generate(serviceName, footprintKey, siteID, configsFolder, SOTDB)
for k, v in consistencyReport.items():
  print(k)
  print(v.devices)
  print(json.dumps(v.config, sort_keys=True, indent=4))    """


complianceReport = compliance.ComplianceReport()  

serviceDefinition = definition.ServiceDefinition.parse_file(f"services/serviceDefinitions/{serviceName}.json")

complianceReport.generate(serviceName, footprintKeys, serviceSotKey, siteID, configsFolder, SOTDB, serviceDefinition)

for item in complianceReport:
  item.footprint = json.dumps(item.footprint) 

print(complianceReport.json())


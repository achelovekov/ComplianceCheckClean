import json
import compliance

serviceName = 'underlay'
serviceKey = 'Ethernet1/52'
siteID = 'VTB'
configsFolder = 'RawConfigs/configTestNew'
SOTDB = 'dataModel.json' 


compliance.TTPDB.generate(serviceName, configsFolder)

consistencyReport = compliance.ConsistencyReport.generate(serviceName, serviceKey, siteID, configsFolder, SOTDB)
for k, v in consistencyReport.items():
  print(k)
  print(v.devices)
  print(json.dumps(v.config, sort_keys=True, indent=4))   


""" complianceReport = compliance.ComplianceReport.generate(serviceName, serviceKey, siteID, configsFolder, SOTDB)
print(complianceReport.json())   """
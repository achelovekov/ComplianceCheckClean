import json
import compliance
import definition
import auxilary
import sot

configsFolder = "RawConfigs/configTest"
siteId = 'VTB'
SoTDBFile = 'SoTDB.json'
auxilaryDBFile = 'AuxilaryDB.json'

serviceItemsJSON = """
[
  {
    "serviceName": "loopbackInterface",
    "footprintKeysType": "static",
    "footprintKeys": [
      "loopback0"
    ],
    "SoTKeysType": "general"
  },
  {
    "serviceName": "bfd",
    "footprintKeysType": "none",
    "SoTKeysType": "general"
  },
  {
    "serviceName": "ospf",
    "footprintKeysType": "dynamic",
    "SoTKeysType": "general"
  },
  {
    "serviceName": "pim",
    "footprintKeysType": "none",
    "SoTKeysType": "general"
  },
  {
    "serviceName": "underlayInterface",
    "footprintKeysType": "dynamic",
    "SoTKeysType": "general"
  }
]
"""
serviceItems = definition.ServiceItems.parse_raw(serviceItemsJSON)
SoTDB = sot.SoTDB.parse_file(SoTDBFile)
auxilaryDB = auxilary.AuxilaryDB.parse_file(auxilaryDBFile)

complianceReport = compliance.combinedCompianceReport(configsFolder, serviceItems, auxilaryDB, siteId, SoTDB)

print(complianceReport.json())
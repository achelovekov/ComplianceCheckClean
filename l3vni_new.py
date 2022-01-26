import json
import compliance
import definition
import auxilary
import sot

configsFolder = "RawConfigs/configTest"
siteId = 'VTB'
SOTDBFile = 'dataModel.json'
auxilaryDBFile = 'AuxilaryDB.json'

serviceItemsJSON = """
[
        {
            "serviceName": "L3VNI",
            "footprintKeysType": "static",
            "footprintKeys": [
               "PROD-SRV-APP"],
            "SoTKeysType": "specific"
        }
    ]
"""
serviceItems = definition.ServiceItems.parse_raw(serviceItemsJSON)
SOTDB = sot.ServiceSoT.parse_file(SOTDBFile)
auxilaryDB = auxilary.AuxilaryDB.parse_file(auxilaryDBFile)

complianceReport = compliance.combinedCompianceReport(configsFolder, serviceItems, auxilaryDB, siteId, SOTDB)

print(complianceReport.json())
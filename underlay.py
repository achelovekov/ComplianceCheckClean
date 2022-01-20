import json
import compliance
import definition

serviceDescriptionJSON = """
{
    "siteID": "VTB",
    "configsFolder": "RawConfigs/configTest",
    "SOTDB": "dataModel.json",
    "serviceItems": [
        {
            "serviceName": "UnderlayInterface",
            "keys": [
                {
                    "footprintKey": "Ethernet1/51", 
                    "SoTKey": "general"
                },
                {
                    "footprintKey": "Ethernet1/52", 
                    "SoTKey": "general"
                }
            ]
        },
        {
            "serviceName": "ospf",
            "keys": [
                {
                    "footprintKey": "Underlay", 
                    "SoTKey": "general"
                }
            ]
        }
    ]
}
"""

print(compliance.combinedCompianceReport(serviceDescriptionJSON))


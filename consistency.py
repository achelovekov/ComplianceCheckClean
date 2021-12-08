from dict_hash import dict_hash, hashable, sha256
from typing import Any, Dict, List
from pydantic import BaseModel
import hashlib


class Item(BaseModel):
    configHash: str
    config: Dict
    devices: List[str]

def consistency(deviceConfigMap: Dict) -> Dict:
    hashSet = {}
    for device, config in deviceConfigMap.items():
        configHash = sha256(config)
        if configHash not in hashSet:
            hashSet[configHash] = Item(configHash=configHash, config=config, devices = [device])
        else:
            item = hashSet[configHash]
            item.devices.append(device)
    
    return hashSet

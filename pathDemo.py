import pathlib

path = pathlib.Path(__file__).parent.resolve()

filename = f"{path}/services/footprintDefinitions/L2VNI.json"

with open(filename, encoding = 'utf-8') as f:
    data = f.read()

print(data)
import json

config = {'default_frames': 120,
          'default_folder': "D:\\turntables"}

with open('config.json', 'w') as outfile:
    json.dumps(config)

with open('config.json', 'r') as jsonfile:
    data = json.load(jsonfile)

print(type(data))
print(data)
import easygui
import json

with open('config.json', 'r') as file:
    config_content = file.read()
    config = json.loads(config_content)

path = easygui.fileopenbox()

config['database-name'] = path

with open('config.json', 'w') as file:
    json.dump(config, file, indent=4)

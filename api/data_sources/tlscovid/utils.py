import json

CONFIG_PATH = 'config.json'

def load_json(file_path):
    with open(file_path, 'r') as fp:
        data = json.load(fp)

    return data

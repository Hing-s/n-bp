import json
from config import Config

with open('cfg/config') as f:
    config = Config(json.loads(f.read())['settings'])

cmds = {}

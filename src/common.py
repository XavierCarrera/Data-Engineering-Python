# We use the common.py file to open our yaml in reading mode.
# This way we have access to the url, as well as the links, titles and body structures

import yaml

__config = None

def config():

    global __config
    if not __config:
        with open('config.yaml', mode='r') as f:
            __config = yaml.safe_load(f)

    return __config
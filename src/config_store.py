import json

class ConfigStore:
    def __init__(self, config_fname):
        with open(config_fname) as f:
            self.dictionary = json.load(f)
    
    def __getattr__(self, name):
        return self.dictionary[name]

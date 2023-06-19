import sys
import json
from pathlib import Path

class AppConfig:
    def __init__(self, config_fname):
        config_path = Path(config_fname)
        assert config_path.exists(), f"does not exist: {config_path}"

        with open(config_path, 'r') as f:
            self.d = json.load(f)
        #

    def get(self, key):
        assert key in self.d.keys()
        return self.d[key]

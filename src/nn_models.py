
from pathlib import Path
from enum import Enum
import os

KNOB_SEGMENTER = "knobhead-r08.eim"
KNOB_CLASSIFIER = "itsagas-r01.eim"

def get_model_path(model_name, os_name=None):
    """
    return path to model filename (eim file)
    """
    if os_name is None:
        os_name = os.uname().sysname
    if os_name == 'Linux':
        model_path = Path('.') / 'modelfiles' / 'linux-x86-64' / str(model_name)
    elif os_name == 'Darwin':
        model_path = Path('.') / 'modelfiles' / 'macos' / str(model_name)
    else:
        assert False, f"unknown platform {os_name}"
    #

    model_path = model_path.resolve()
    assert model_path.exists(), f"model_path {model_path} does not exist"

    return model_path



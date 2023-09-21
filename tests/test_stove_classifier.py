# unit tests for  knob_locator.py in the same vein as test_knob_classify.py
import unittest
import numpy as np
from pathlib import Path
import os


import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import helplib 
import stove_classifier

class TestStoveClassifier(unittest.TestCase):
    knobs_path = Path('tests/in/out-renamed/general/general-0026.jpg')
    assert knobs_path.exists(), f"{knobs_path} does not exist"

    if os.uname().sysname == 'Linux':
        kl_model_path = Path('./modelfiles/linux-x86-64/knobhead-r08.eim')
        kc_model_path = Path('./modelfiles/linux-x86-64/itsagas-r01.eim')
    elif os.uname().sysname == 'Darwin':
        kl_model_path = Path('./modelfiles/macos/knobhead-r08.eim')  # knob locator
        kc_model_path = Path('./modelfiles/macos/itsagas-r01.eim') # knob classifier
    else:
        assert False, f"unknown platform {os.uname().sysname}"
    assert kl_model_path.exists(), f"model_path {kl_model_path} does not exist"
    assert kc_model_path.exists(), f"model_path {kc_model_path} does not exist"

    def setUp(self):
        print("setup")

    def tearDown(self):
        print("teardown")

    def test_stove_classifier(self):
        import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = Path('./tests/out/'))
        stove_is_on = sc.classify_image(self.knobs_path, write_img_flag=True)
        self.assertTrue(True)
        #

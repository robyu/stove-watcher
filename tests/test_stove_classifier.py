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
    STOVE_ON_IMG = Path('tests/in/out-renamed/general/general-0026.jpg').resolve()
    assert STOVE_ON_IMG.exists(), f"{STOVE_ON_IMG} does not exist"
    STOVE_OFF_IMG = Path('tests/in/out-renamed/general/general-0000.jpg').resolve()
    assert STOVE_OFF_IMG.exists(), f"{STOVE_OFF_IMG} does not exist"
    STOVE_DARK_IMG = Path('tests/in/out-renamed/general/general-0009.jpg').resolve()
    assert STOVE_DARK_IMG.exists(), f"{STOVE_DARK_IMG} does not exist"

    
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

    def Xtest_stove_is_on(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = Path('./tests/out/'))
        stove_is_on = sc.stove_is_on(self.STOVE_ON_IMG, write_img_flag=True)
        self.assertTrue(stove_is_on==True)
        #

    def Xtest_stove_is_off(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = Path('./tests/out/'))
        stove_is_on = sc.stove_is_on(self.STOVE_OFF_IMG, write_img_flag=True)
        self.assertTrue(stove_is_on==False)

    def test_stove_is_dark(self):
        import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = Path('./tests/out/'))
        stove_is_on = sc.stove_is_on(self.STOVE_DARK_IMG, write_img_flag=True)
        self.assertTrue(stove_is_on==False)

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

    TEST_OUT_DIR = Path('./tests/out/test_stove_classifier').resolve()
    @classmethod
    def setUpClass(cls):
        # execute function before test suite runs
        print("Setting up test suite...")
        if not TestStoveClassifier.TEST_OUT_DIR.exists():
            TestStoveClassifier.TEST_OUT_DIR.mkdir(parents=False, exist_ok=True)
        else:
            # remove all files in TEST_OUT_DIR
            print("remove existing output files")
            for f in os.listdir(TestStoveClassifier.TEST_OUT_DIR):
                os.remove(TestStoveClassifier.TEST_OUT_DIR / f)    


    def setUp(self):
        print("setup")

        # there's no reason to execute this code pre-test, so it it doesn't really belong here
        if os.uname().sysname == 'Linux':
            self.kl_model_path = Path('./modelfiles/linux-x86-64/knobhead-r08.eim')
            self.kc_model_path = Path('./modelfiles/linux-x86-64/itsagas-r01.eim')
        elif os.uname().sysname == 'Darwin':
            self.kl_model_path = Path('./modelfiles/macos/knobhead-r08.eim')  # knob locator
            self.kc_model_path = Path('./modelfiles/macos/itsagas-r01.eim') # knob classifier
        else:
            assert False, f"unknown platform {os.uname().sysname}"
        assert self.kl_model_path.exists(), f"model_path {self.kl_model_path} does not exist"
        assert self.kc_model_path.exists(), f"model_path {self.kc_model_path} does not exist"

        

    def tearDown(self):
        print("teardown")

    def test_smoke(self):
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        self.assertTrue(True)

    def test_stove_is_on(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_ON_IMG)
        self.assertTrue(len(knob_on_l)==7)
        self.assertTrue(min(knob_on_l) >= 0.90)


    def test_stove_is_off(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_OFF_IMG)
        self.assertTrue(len(knob_on_l)==7)
        self.assertTrue(min(knob_on_l) < 0.90)

    def test_stove_is_dark(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_DARK_IMG)
        self.assertTrue(len(knob_on_l)==0)   # no knobs found




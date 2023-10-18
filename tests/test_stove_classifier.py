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
import nn_models
import shutil
import stove_state

class TestStoveClassifier(unittest.TestCase):
    STOVE_ON_IMG = Path( "./tests/in/test_stove_classifier/borest1-0000.jpg").resolve()
    STOVE_OFF_IMG = Path("./tests/in/test_stove_classifier/borest1-0023.jpg").resolve()
    STOVE_DARK_IMG =      Path("./tests/in/test_stove_classifier/borest1-0044.jpg").resolve()


    REJECT_PATH = Path('./tests/out/test_knob_classifier/reject').resolve()
    TEST_OUT_DIR = Path('./tests/out/test_stove_classifier').resolve()

    #import pudb; pudb.set_trace()

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

        TestStoveClassifier.REJECT_PATH.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        print("setup")

        # there's no reason to execute this code pre-test, so it it doesn't really belong here
        self.kl_model_path = nn_models.get_model_path(nn_models.KNOB_SEGMENTER)
        self.kc_model_path = nn_models.get_model_path(nn_models.KNOB_CLASSIFIER)

    def tearDown(self):
        print("teardown")

    def test_smoke(self):
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        self.assertTrue(True)

    def test_stove_is_on(self):

        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_ON_IMG)
        # verify that knob_on_l is a numpy array
        self.assertTrue(isinstance(knob_on_l, np.ndarray))
        self.assertTrue(len(knob_on_l)== stove_state.StoveState.NUM_KNOBS)
        self.assertTrue(max(knob_on_l) >= 0.90)

    def test_stove_is_off(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_OFF_IMG)
        knob_off_l = 1.0 - np.array(knob_on_l)
        self.assertTrue(len(knob_on_l)==stove_state.StoveState.NUM_KNOBS)
        self.assertTrue(min(knob_off_l) > 0.90)

    def test_stove_is_dark(self):
        #import pudb; pudb.set_trace()
        sc = stove_classifier.StoveClassifier(self.kl_model_path, self.kc_model_path, debug_out_path = TestStoveClassifier.TEST_OUT_DIR)
        knob_on_l = sc.classify_image(self.STOVE_DARK_IMG)
        self.assertTrue(len(knob_on_l)==0)   # no knobs found

    def test_knob_reject_filter(self):
        # delete all files in REJECT_PATH
        for f in TestStoveClassifier.REJECT_PATH.iterdir():
            f.unlink()

        sc = stove_classifier.StoveClassifier(self.kl_model_path,
                                              self.kc_model_path,
                                              reject_out_path = TestStoveClassifier.REJECT_PATH,
                                            )
        knob_on_l = sc.classify_image(self.STOVE_ON_IMG,
                                      test_inject_conf = 0.5)

        # check that the reject filter wrote a file to REJECT_PATH
        reject_files_l = list(TestStoveClassifier.REJECT_PATH.iterdir())
        print(reject_files_l)
        self.assertTrue( len(reject_files_l) >= 1)


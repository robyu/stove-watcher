import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import cv2
from pathlib import Path
import unittest
import helplib
import os
import numpy as np
import helplib
from edge_impulse_linux.image import ImageImpulseRunner

from pathlib import Path
import knob_classifier

class TestKnobClassifier(unittest.TestCase):
    KNOB_OFF_IMG = Path('./tests/in/test_knob_classifier/bbt-general-0000-b00.png').resolve()
    KNOB_ON_IMG = Path('./tests/in/test_knob_classifier/bbt-general-0027-b00.png').resolve()

    # pick the correct model for your platform
    if os.uname().sysname == 'Linux':   
        model_path = Path('./modelfiles/linux-x86-64/itsagas-r01.eim').resolve()
    elif os.uname().sysname == 'Darwin':
        model_path = Path('./modelfiles/macos/itsagas-r01.eim').resolve()
    else:
        assert False, f"unknown platform {os.uname().sysname}"
    assert model_path.exists(), f"model_path {model_path} does not exist"

    def setUp(self):
        pass

    def tearDown(self):
        print('teardown')
        

    def test_knob_classify_off(self):
        print(f"model: {self.model_path}")
        print(f"image: {self.KNOB_OFF_IMG}")
        kc = knob_classifier.KnobClassifier(self.model_path)
        img_rgb = helplib.read_image_rgb(self.KNOB_OFF_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( (1.0 - conf_on) > 0.9)

    def test_knob_classify_on(self):
        print(f"model: {self.model_path}")
        print(f"image: {self.KNOB_ON_IMG}")
        kc = knob_classifier.KnobClassifier(self.model_path)
        img_rgb = helplib.read_image_rgb(self.KNOB_ON_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( conf_on > 0.9)
        


if __name__== "__main__":
    unittest.main()
    

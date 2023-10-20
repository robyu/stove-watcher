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
import nn_models


class TestKnobClassifier(unittest.TestCase):
    KNOB_OFF_IMG = Path('./tests/in/test_knob_classifier/bbt-general-0000-b00.png').resolve()
    KNOB_ON_IMG = Path('./tests/in/test_knob_classifier/bbt-general-0027-b00.png').resolve()
    KNOB_INDET_IMG = Path('./tests/in/test_knob_classifier/bbt-general-0015-b03.png').resolve()
    KNOB_BLANK_IMG = Path('./tests/in/test_knob_classifier/general-0040-knob-03-onconf-099.png').resolve()

    # pick the correct model for your platform
    MODEL_PATH = nn_models.get_model_path(nn_models.KNOB_CLASSIFIER)

    def setUp(self):
        pass

    def tearDown(self):
        print('teardown')
        

    def test_knob_classify_off(self):
        print(f"\nmodel: {self.MODEL_PATH}")
        print(f"image: {self.KNOB_OFF_IMG}")
        kc = knob_classifier.KnobClassifier(self.MODEL_PATH)
        img_rgb = helplib.read_image_rgb(self.KNOB_OFF_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( (1.0 - conf_on) > 0.9)

    def test_knob_classify_on(self):
        print(f"\nmodel: {self.MODEL_PATH}")
        print(f"image: {self.KNOB_ON_IMG}")
        kc = knob_classifier.KnobClassifier(self.MODEL_PATH)
        img_rgb = helplib.read_image_rgb(self.KNOB_ON_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( conf_on > 0.9)
        
    def test_knob_classify_indeterminate1(self):
        print(f"\nmodel: {self.MODEL_PATH}")
        print(f"image: {self.KNOB_INDET_IMG}")
        kc = knob_classifier.KnobClassifier(self.MODEL_PATH)
        img_rgb = helplib.read_image_rgb(self.KNOB_INDET_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( conf_on < 0.9)

    def test_knob_classify_indeterminate(self):
        """
        run an indeterminate knob image through the classifier  
        and make sure the confidence is low

        I found the image within EI studio / itsagas project by classifying all
        the test data and picking out the iamges w/ low confidence values
        """
        print(f"\nmodel: {self.MODEL_PATH}")
        print(f"image: {self.KNOB_INDET_IMG}")
        kc = knob_classifier.KnobClassifier(self.MODEL_PATH)
        img_rgb = helplib.read_image_rgb(self.KNOB_INDET_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( conf_on < 0.9)

    def test_blank_knob_is_off(self):
        print(f"\nmodel: {self.MODEL_PATH}")
        print(f"image: {self.KNOB_BLANK_IMG}")
        kc = knob_classifier.KnobClassifier(self.MODEL_PATH)
        img_rgb = helplib.read_image_rgb(self.KNOB_INDET_IMG)
        conf_on = kc.classify(img_rgb)
        self.assertTrue( (1.0 - conf_on) >= 0.9)


if __name__== "__main__":
    unittest.main()
    

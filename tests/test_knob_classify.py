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
    knob_off_path = Path('./data/out-knobtagger/bbtagger/general/off/bbt-general-0000-b00.png')
    model_path = Path('./modelfiles/macos/itsagas-r01.eim')
    

    def setUp(self):
        print('setup')


    def tearDown(self):
        print('teardown')
        

    @staticmethod
    def knob_is_on(res, thresh = 0.95):
        off_score = res['result']['classification']['off']
        on_score = res['result']['classification']['on']
        print(f"off_score: {off_score} | on_score: {on_score}")
        assert off_score + on_score > 0.99, f"off_score + on_score = {off_score + on_score} < 0.99"
        if on_score > thresh:
            return True
        else:
            return False
        #

    def test_knob_classification_standalone(self):
        print(f"model: {self.model_path}")
        print(f"image: {self.knob_off_path}")
        runner = ImageImpulseRunner(str(self.model_path))
        model_info = runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

        
        # get image
        img_rgb = helplib.read_image_rgb(self.knob_off_path)

        #
        features, img_out = runner.get_features_from_image(img_rgb)

        res = runner.classify(features)
        runner.stop() 
        is_on = self.knob_is_on(res)

        self.assertFalse(is_on)

    def test_knob_classification(self):
        print(f"model: {self.model_path}")
        print(f"image: {self.knob_off_path}")
        kc = knob_classifier.KnobClassifier(self.model_path)
        img_rgb = helplib.read_image_rgb(self.knob_off_path)
        is_on = kc.is_on(img_rgb)
        self.assertFalse(is_on)


        


if __name__== "__main__":
    unittest.main()
    

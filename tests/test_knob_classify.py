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

class TestKnobClassifier(unittest.TestCase):
    knob_off_path = Path('./data/out-knobtagger/bbtagger/general/off/bbt-general-0000-b00.png')
    model_path = Path('./modelfiles/itsagas-r01.eim')
    

    def setUp(self):
        print('setup')


    def tearDown(self):
        print('teardown')
        
    @staticmethod    
    def print_classification(labels, res, tag):
        if "classification" in res["result"].keys():
            print('%s: Result (%d ms.) ' % (tag, res['timing']['dsp'] + res['timing']['classification']), end='')
            for label in labels:
                score = res['result']['classification'][label]
                print('%s: %.2f\t' % (label, score), end='')
            print('', flush=True)
        elif "bounding_boxes" in res["result"].keys():
            print('%s: Found %d bounding boxes (%d ms.)' % (tag, len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
            for bb in res["result"]["bounding_boxes"]:
                print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                
    def test_knob_classification(self):
        print(f"model: {self.model_path}")
        print(f"image: {self.knob_off_path}")
        runner = ImageImpulseRunner(str(self.model_path))
        model_info = runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
        labels = model_info['model_parameters']['labels']
        print(labels)
        
        # get image
        img_rgb = helplib.read_image_rgb(self.knob_off_path)

        #
        features, img_out = runner.get_features_from_image(img_rgb)
        res = runner.classify(features)
        runner.stop()

        self.print_classification(labels, res, 'stove')
        self.assertTrue(True)
        

if __name__== "__main__":
    unittest.main()
    

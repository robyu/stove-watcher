import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import cv2
import knobid
from pathlib import Path
import unittest
import appconfig
import helplib

class TestNeuralNets(unittest.TestCase):
    knobs_5_twists_1 = Path('data/out-resized/logi-2023-06-06-16-19-4.jpg')
    
    def setUp(self):
        print('setup')
        self.config = appconfig.AppConfig("tests/testconfig.json")

    def tearDown(self):
        print('teardown')

        
    def test_knob_extractor(self):
        ke = knobid.KnobId(self.config.get("ke_model_fname"))
        imgrgb = helplib.read_image_rgb(self.knobs_5_twists_1)
        bb_l, img_out = ke.locate_knobs(imgrgb)
        for bb in bb_l:
            print(f"val: {bb['value']:5.3} x: {bb['x']} y:{bb['y']} w:{bb['width']} h:{bb['height']}")
        #
        self.assertTrue(len(bb_l)==5)

            
    #

if __name__== "__main__":
    unittest.main()
    

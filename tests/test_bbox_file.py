import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import os

from pathlib import Path
import unittest
import boundingboxfile


class TestBBoxFile(unittest.TestCase):
    def setUp(self):
        print('setup')

    def tearDown(self):
        print('teardown')
        
    def test_round_trip(self):
        #import pudb; pudb.set_trace()
        image_path = Path("tests/data/square.png")
        box0 = (0, 100, 50, 60)   # x, y, w, h
        box1 = (200, 200, 25, 30)

        try:
            os.remove("tests/data/rects.pickle")
        except:
            pass
        
        bbf = boundingboxfile.BBoxFile(image_path)


        img_bboxes = boundingboxfile.ImageBBoxes(image_path, 600, 600)
        img_bboxes.add_bbox(box0)
        img_bboxes.add_bbox(box1)
        bbf[str(image_path)] = img_bboxes
        bbf.save()

        del bbf
        bbf = boundingboxfile.BBoxFile(image_path)
        self.assertTrue(str(image_path) in bbf.images_d)
        self.assertTrue(bbf[str(image_path)].get_num_bboxes() == 2)
    #

if __name__== "__main__":
    unittest.main()
    

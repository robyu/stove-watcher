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
        
    # def test_round_trip(self):
    #     #import pudb; pudb.set_trace()
    #     image_path = Path("./data/square.png")
    #     box0 = (0, 100, 50, 60)   # x, y, w, h
    #     box1 = (200, 200, 25, 30)

    #     try:
    #         os.remove("tests/data/rects.pickle")
    #     except:
    #         pass
        
    #     bbf = boundingboxfile.BBoxFile(image_path)


    #     img_bboxes = boundingboxfile.ImageBBoxes(image_path, 600, 600)
    #     img_bboxes.add_bbox(box0)
    #     img_bboxes.add_bbox(box1)
    #     bbf[str(image_path)] = img_bboxes
    #     bbf.save()

    #     del bbf
    #     bbf = boundingboxfile.BBoxFile(image_path)
    #     self.assertTrue(str(image_path) in bbf.images_d)
    #     self.assertTrue(bbf[str(image_path)].get_num_bboxes() == 2)
    #

    def test_bbox_to_dict(self):
        bbox = boundingboxfile.BBox(0, 5, 10, 20, 0.5, 'knob')
        print(bbox)
        d = bbox.to_dict()
        self.assertTrue(d['x'] == 0)
        self.assertTrue(d['y'] == 5)
        
    def test_imagebboxes(self):
        image_path = Path("foo.png")   # doesn't need to exist
        img_bboxes = boundingboxfile.ImageBBoxes(image_path, 600, 600)
        self.assertTrue(img_bboxes.image_path == image_path)
        self.assertTrue(img_bboxes.image_width == 600)
        self.assertTrue(img_bboxes.image_height == 600)
        self.assertTrue(img_bboxes.get_num_bboxes() == 0)

    def test_imagebboxes_iter(self):
        # test iterating through bboxes
        image_path = Path("foo.png")   # doesn't need to exist
        img_bboxes = boundingboxfile.ImageBBoxes(image_path, 600, 600)
        bbox0 = boundingboxfile.BBox(0, 5, 10, 20, 0.5, 'knob')
        bbox1 = boundingboxfile.BBox(100, 105, 110, 120, 0.5, 'knob')

        img_bboxes.add_bbox(bbox0)
        img_bboxes.add_bbox(bbox1)

        # iterate through the bboxes
        num_bboxes = 0
        for bbox in img_bboxes:
            num_bboxes += 1
        self.assertTrue(num_bboxes == 2)


if __name__== "__main__":
    unittest.main()
    

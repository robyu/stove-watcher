# unit tests for  knob_locator.py in the same vein as test_knob_classify.py
import unittest
import numpy as np
from pathlib import Path
import os


import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import helplib 
import knob_locator 
import boundingboxfile

class TestKnobLocator(unittest.TestCase):
    knobs_resized_path = Path('tests/in/out-resized/general/general-0026.png')
    assert knobs_resized_path.exists(), f"{knobs_resized_path} does not exist"

    knobs_path = Path('tests/in/out-renamed/general/general-0026.jpg')
    assert knobs_path.exists(), f"{knobs_path} does not exist"

    if os.uname().sysname == 'Linux':
        model_path = Path('./modelfiles/linux-x86-64/knobhead-r08.eim')
    elif os.uname().sysname == 'Darwin':
        model_path = Path('./modelfiles/macos/knobhead-r08.eim')
    else:
        assert False, f"unknown platform {os.uname().sysname}"
    assert model_path.exists(), f"model_path {model_path} does not exist"

    def setUp(self):
        print("setup")

    def tearDown(self):
        print("teardown")

    def test_knob_locator(self):
        kl = knob_locator.KnobLocator(self.model_path)
        imgrgb = helplib.read_image_rgb(self.knobs_resized_path)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_path = Path('./tests/out/test_knob_locator.png')
        helplib.write_image(out_path, img_out)
        self.assertTrue(out_path.exists())

        print("found {len(bb_l)} knobs")
        for bb in bb_l:
            # print x, y, w, h in each BBox
            print(f"val: {bb.value:5.3f}, (x, y)=({bb.x}, {bb.y}), (w, h)=({bb.w}, {bb.h})")
        #
        self.assertTrue(len(bb_l)==7)

    def test_knob_locator_with_resize(self):
        kl = knob_locator.KnobLocator(self.model_path)
        imgrgb = helplib.read_image_rgb(self.knobs_resized_path)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_path = Path('./tests/out/test_knob_locator_with_resize.png')
        helplib.write_image(out_path, img_out)
        self.assertTrue(out_path.exists())

        print("found {len(bb_l)} knobs")
        for bb in bb_l:
            # print x, y, w, h in each BBox
            print(f"val: {bb.value:5.3f}, (x, y)=({bb.x}, {bb.y}), (w, h)=({bb.w}, {bb.h})")
        #
        self.assertTrue(len(bb_l)==7)

        out_path = Path('./tests/out/test_knob_locator_with_resize_marked.png')
        for bb in bb_l:
            boundingboxfile.mark_bb_on_img(img_out, bb)
        helplib.write_image(out_path, img_out)

    def test_write_marked_image(self):
        kl = knob_locator.KnobLocator(self.model_path)
        imgrgb = helplib.read_image_rgb(self.knobs_resized_path)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_path = Path('./tests/out/test_write_marked_image.png')
        for bb in bb_l:
            boundingboxfile.mark_bb_on_img(img_out, bb)
        helplib.write_image(out_path, img_out)
        self.assertTrue(out_path.exists())







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
import nn_models
import shutil

class TestKnobLocator(unittest.TestCase):

    # cropped & resized to square image
    KNOBS_RESIZED_PATH = Path('tests/in/test_knob_locator/general-0026.png')
    assert KNOBS_RESIZED_PATH.exists(), f"{KNOBS_RESIZED_PATH} does not exist"

    # raw image (not resized)
    KNOBS_PATH = Path('tests/in/test_knob_locator/general-0026.jpg')
    assert KNOBS_PATH.exists(), f"{KNOBS_RESIZED_PATH} does not exist"

    #KNOBS_PATH = Path('tests/in/out-renamed/general/general-0026.jpg')
    #assert KNOBS_PATH.exists(), f"{KNOBS_PATH} does not exist"

    MODEL_PATH = nn_models.get_model_path(nn_models.KNOB_SEGMENTER)

    OUT_PATH = Path('./tests/out/test_knob_locator').resolve()  
    if OUT_PATH.exists():
        shutil.rmtree(OUT_PATH)
    OUT_PATH.mkdir(parents=True)

    def setUp(self):
        print("setup")

    def tearDown(self):
        print("teardown")

    def test_locate_knobs_resized_img(self):
        kl = knob_locator.KnobLocator(self.MODEL_PATH)
        imgrgb = helplib.read_image_rgb(self.KNOBS_RESIZED_PATH)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_fname = self.OUT_PATH / "test_knob_locator.png"
        helplib.write_image(out_fname, img_out)
        self.assertTrue(out_fname.exists())

        print(f"found {len(bb_l)} knobs")
        for bb in bb_l:
            # print x, y, w, h in each BBox
            print(f"val: {bb.value:5.3f}, (x, y)=({bb.x}, {bb.y}), (w, h)=({bb.w}, {bb.h})")
        #
        self.assertTrue(len(bb_l)==7)

    def test_locate_knobs_full_sized_img(self):
        kl = knob_locator.KnobLocator(self.MODEL_PATH)
        imgrgb = helplib.read_image_rgb(self.KNOBS_PATH)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_fname = self.OUT_PATH / 'test_knob_locator_with_resize.png'
        helplib.write_image(out_fname, img_out)
        self.assertTrue(out_fname.exists())

        print(f"found {len(bb_l)} knobs")
        for bb in bb_l:
            # print x, y, w, h in each BBox
            print(f"val: {bb.value:5.3f}, (x, y)=({bb.x}, {bb.y}), (w, h)=({bb.w}, {bb.h})")
        #
        self.assertTrue(len(bb_l)==7)

        out_fname = self.OUT_PATH / 'test_knob_locator_with_resize_marked.png'
        for bb in bb_l:
            boundingboxfile.mark_bb_on_img(img_out, bb)
        helplib.write_image(out_fname, img_out)

    def test_write_marked_image(self):
        kl = knob_locator.KnobLocator(self.MODEL_PATH)
        imgrgb = helplib.read_image_rgb(self.KNOBS_PATH)
        bb_l, img_out = kl.locate_knobs(imgrgb)

        out_fname = self.OUT_PATH / 'test_write_marked_image.png'

        for bb in bb_l:
            boundingboxfile.mark_bb_on_img(img_out, bb)
        helplib.write_image(out_fname, img_out)
        self.assertTrue(out_fname.exists())

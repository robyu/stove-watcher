

import os
from pathlib import Path

# add ./src to path
import sys
sys.path.append('./src')
import knob_classifier
import knob_locator
import helplib

class StoveClassifier:
    """
    read an image, segment out knobs, classify each knob
    """
    MAX_NUM_KNOBS = 7
    KNOB_CLASSIFIER_THRESHOLD = 0.90
    
    def __init__(self, locater_model_path, 
                 classifier_model_path,
                   reject_path = Path('./rejects'),
                   debug_out_path = None):
        self.kl = knob_locator.KnobLocator(locater_model_path)
        self.kc = knob_classifier.KnobClassifier(classifier_model_path, thresh = StoveClassifier.KNOB_CLASSIFIER_THRESHOLD)
        self.reject_path = Path(reject_path)
        if reject_path.exists():
            assert reject_path.is_dir(), f"{reject_path} is not a directory"
        else:
            reject_path.mkdir(parents=True, exist_ok=True)
        #
        self.debug_out_path = debug_out_path
        if self.debug_out_path:
            assert self.debug_out_path.exists()
            assert self.debug_out_path.is_dir()
        #            
        self.extra_knob_width = 26
        self.extra_knob_height = 26
        self.bb_l = []  
        self.adjusted_box_coords_l = []

    def _write_knob_locator_out(self, img, bb_l, fname):
        img_copy = img.copy()
        for bb in bb_l:
            img_copy = helplib.draw_box(img_copy, bb.x0, bb.y0, bb.x1, bb.y1)
        #
        helplib.write_image(self.debug_out_path / fname, img_copy)

    def _write_orig_img_with_bboxes(self, img, box_coords_l, fname):
        img_copy = img.copy()
        for box_coords in box_coords_l:
            img_copy = helplib.draw_box(img_copy, box_coords[0], box_coords[1], box_coords[2], box_coords[3])
        #
        helplib.write_image(self.debug_out_path / fname, img_copy)

    def classify_image(self, img_path, write_img_flag=False):
        assert img_path.exists()
        img_orig = helplib.read_image_rgb(img_path)

        self.bb_l, img_kl = self.kl.locate_knobs(img_orig)
        kl_reject_flag = self._reject_stove_image(self.bb_l, img_orig, img_path)

        if write_img_flag:
            self._write_knob_locator_out(img_kl, self.bb_l, "knob-locator-out.png")

        if kl_reject_flag==False:
            # create list of bbox coords adjusted for the original image
            self.adjusted_box_coords_l = self._adjust_bbox_coords(self.bb_l, img_orig)
            if write_img_flag:
                self._write_orig_img_with_bboxes(img_orig, self.adjusted_box_coords_l, "orig-img-with-bboxes.png")               
            #
            stove_is_on = self._eval_knobs(self.adjusted_box_coords_l, img_orig, img_path, write_img_flag)
        else:
            stove_is_on = False
            self.adjusted_box_coords_l = []
        #
        print(f"stove {img_path}: stove_is_on = {stove_is_on}")
        return stove_is_on
    
    def _adjust_bbox_coords(self, bb_l, img):
        """
        IN
        bb_l: list of BBox objects
        img: original (uncropped) image array
        
        OUT
        bb_adj_l: list of BBox objects with adjusted coords
        """

        # compute crop params
        scalef, h_offset = helplib.compute_crop_params(img.shape[1], img.shape[0], self.kl.MAX_ROWS_COLS, self.kl.MAX_ROWS_COLS)

        adjusted_box_coords_l = []
        for bb in bb_l:
            adj_bbox_coords = helplib.adjust_bbox_coords(bb,
                                                 scalef,
                                                 h_offset,
                                                 self.extra_knob_width,
                                                 self.extra_knob_height,
                                                 img.shape[1], # orig width
                                                 img.shape[0])
            adjusted_box_coords_l.append(adj_bbox_coords)
        #
        return adjusted_box_coords_l

    def _reject_stove_image(self, bb_l, img, img_path):
        reject_flag = False
        if len(bb_l) > StoveClassifier.MAX_NUM_KNOBS:
            # filename is reject_path + img_path stem + "too-many-knobs" + png
            reject_fname = self.reject_path / f"{img_path.stem}-too-many-knobs.png"
            helplib.write_image(reject_fname, img)
            print(f"rejecting {img_path} because it has {len(bb_l)} knobs")
            print(f"wrote to {reject_fname}")
            reject_flag = True
        #
        return reject_flag

    def _eval_knobs(self, adjusted_box_coords_l, img, img_path, write_img_flag=False):
        """
        IN
        bb_l: list of BBox objects
        img: image (numpy array)
        img_path: path to image
        write_img_flag:  if True, write image to debug_out_path
        
        OUT
        stove_is_on: boolean
        """
        stove_is_on = False
        for n, coord in enumerate(adjusted_box_coords_l):
            knob_img = helplib.extract_knob_image(img, *coord)  # *coord is unpacking the tuple
            knob_is_on = self.kc.is_on(knob_img)
            print(f"knob {n} is {knob_is_on}")
            if knob_is_on:
                stove_is_on = stove_is_on or True
            #
            if write_img_flag:
                fname = self.debug_out_path / f"{img_path.stem}-knob-{n:02d}-{str(knob_is_on)}.png"
                helplib.write_image(fname, knob_img)
                print(f"wrote {fname}")
            #

        return stove_is_on



    



import os
from pathlib import Path
import argparse
import nn_models


# add ./src to path
import sys
sys.path.append('./src')
import knob_classifier
import knob_locator
import helplib
import enum
import datetime
import numpy as np

class StoveClassifier:
    """
    read an image, segment out knobs, classify each knob
    """
    # MAX_NUM_KNOBS = 7
    KNOB_ON_THRESH = 0.90
    KNOB_OFF_THRESH = 0.90
    
    def __init__(self, 
                 locater_model_path, 
                 classifier_model_path,
                 debug_out_path = None,  # functions as both an output path and enable flag,
                 reject_out_path = None, # functions as both an output path and enable flag
                 reject_conf_on_thresh = 0.9,
                 reject_conf_off_thresh = 0.9,
                 ):
        self.kl = knob_locator.KnobLocator(locater_model_path)
        self.kc = knob_classifier.KnobClassifier(classifier_model_path)

        self.debug_out_path = None
        if debug_out_path != None:
            self.debug_out_path = Path(debug_out_path).resolve()
            assert self.debug_out_path.exists()
            assert self.debug_out_path.is_dir()
        #            

        self.extra_knob_width = 26
        self.extra_knob_height = 26
        self.bb_l = []  
        self.adjusted_box_coords_l = []

        self.reject_out_path = None
        if reject_out_path != None:
            self.reject_out_path = Path(reject_out_path).resolve()
            assert self.reject_out_path.exists()
            assert self.reject_out_path.is_dir()
        #
        self.reject_conf_on_thresh = reject_conf_on_thresh
        self.reject_conf_off_thresh = reject_conf_off_thresh

    def _write_img_with_bboxes(self, img, bb_l, fname):
        """
        for debug: mark a copy of img with all bounding boxes, then
        write to the debug_out_path
        """
        img_copy = img.copy()
        for bb in bb_l:
            img_copy = helplib.draw_box(img_copy, bb.x0, bb.y0, bb.x1, bb.y1)
        #
        helplib.write_image(fname, img_copy)
        print(f"wrote image with knobs to {fname}")

    def _write_img_with_bbox_coords(self, img, box_coords_l, fname):
        """
        like _write_img_with_bboxes, except bbox_coords are adjusted coordinates
        """
        img_copy = img.copy()
        for box_coords in box_coords_l:
            img_copy = helplib.draw_box(img_copy, box_coords[0], box_coords[1], box_coords[2], box_coords[3])
        #
        helplib.write_image(fname, img_copy)


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

    def _debug_write_knob_image(self, out_path, knob_img, knob_index, img_path, knob_on_conf):
        """
        write individual knob image with a nice filename
        """
        assert out_path.exists(), f"output path {out_path} does not exist"

        conf_int = int(knob_on_conf * 100)
        fname = out_path / f"{img_path.stem}-knob-{knob_index:02d}-onconf-{conf_int:03d}.png"
        print(f"writing knob image to {fname}")
        helplib.write_image(fname, knob_img)



    def _eval_knobs(self, adjusted_box_coords_l, img, img_path, test_inject_conf = -1.0):
        """
        IN
        bb_l: list of BBox objects
        img: image (numpy array)
        img_path: path to image
        write_img_flag:  if True, write image to debug_out_path
        
        OUT
        stove_class
        """
        knob_on_conf_l = []  # list of knob==on confidences
        for n, coord in enumerate(adjusted_box_coords_l):
            knob_img= helplib.extract_knob_image(img, *coord)  # *coord is unpacking the tuple
            conf_on = self.kc.classify(knob_img)

            if n==0 and test_inject_conf >= 0.0:
                conf_on = test_inject_conf
            #

            knob_on_conf_l.append(conf_on)
            #
            if self.debug_out_path != None:
                self._debug_write_knob_image(self.debug_out_path, knob_img, n, img_path, conf_on)
            # 

            if self.reject_out_path != None and conf_on < self.reject_conf_on_thresh and (1.0-conf_on) < self.reject_conf_off_thresh:
                self._debug_write_knob_image(self.reject_out_path, knob_img, n, img_path, conf_on)
            #
        #
        # write the stove image w/ bboxes
        if self.debug_out_path != None:
            fname = self.debug_out_path / f"{img_path.stem}-knob-locator-out.png"
            print(f"writing image with knobs to {fname}")
            self._write_img_with_bbox_coords(img, adjusted_box_coords_l, fname)

        return np.array(knob_on_conf_l)

    def classify_image(self, img_path, test_inject_conf = -1.0):
        """
        IN
        img: image (numpy array)
        write_img_flag:  if True, write image to debug_out_path

        OUT
        knob_on_conf_l: list of P(knob=on) for each knob
        """
        assert img_path.exists(), f"image path {img_path} does not exist"
        print(f"classifying image {img_path}")
        
        img_orig = helplib.read_image_rgb(img_path)

        self.bb_l = []
        self.adjusted_box_coords_l = []


        self.bb_l, img_kl = self.kl.locate_knobs(img_orig)
        self.adjusted_box_coords_l = self._adjust_bbox_coords(self.bb_l, img_orig)
        knob_on_conf_l = self._eval_knobs(self.adjusted_box_coords_l, img_orig, img_path, test_inject_conf)

        return knob_on_conf_l


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("image_path", type=Path, help="path to stove image or image dir")
    parser.add_argument("-o", "--out_path", type=str, required=True, help="output path")
    parser.add_argument("-x", "--extra_width", type=int, default=26, help="extra width, in pixels, default=26")
    return parser.parse_args()

"""
process stove image, wrote marked stove image (with bounding boxes) 
and knob images 
"""
if __name__=="__main__":
    args  = parse_args()
    assert args.image_path.exists(), f"{args.image_path} does not exist"

    assert args.out_path != None, f"must specify output path"
    out_path = Path(args.out_path).resolve()

    # if image_path is a directory, then create a list of all *.png files in that directory
    # otherwise it's a single file
    if args.image_path.is_dir():
        image_ext = ('.png', '.jpg', '.jpeg')
        image_files_l = [f for f in args.image_path.resolve().iterdir() if f.suffix.lower() in image_ext]
    else:
        image_files_l = [args.image_path]

    if len(image_files_l) == 0:
        print(f"no image files found in {args.image_path}")
        exit(0)

    # make out_path
    if not out_path.exists():
        os.makedirs(out_path, exist_ok=True)

    # load the model
    sc = StoveClassifier(nn_models.get_model_path(nn_models.KNOB_SEGMENTER),
                         nn_models.get_model_path(nn_models.KNOB_CLASSIFIER),
                         out_path)
    sc.extra_knob_width = args.extra_width
    sc.extra_knob_height = args.extra_width

    # extract knob images from each stove image
    for img_path in image_files_l:
        sc.classify_image(img_path)
    #


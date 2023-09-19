

import os
import pathlib as Path

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
    KNOB_CLASSIFIER_THRESHOLD = 0.95
    
    def __init__(self, locater_model_path, classifier_model_path, reject_dir = './rejects'):
        self.kl = knob_locator.KnobLocator(locater_model_path)
        self.kc = knob_classifier.KnobClassifier(classifier_model_path)
        self.reject_path = Path(reject_dir)
        if reject_path.exists():
            assert reject_path.is_dir(), f"{reject_path} is not a directory"
        else:
            reject_path.mkdir(parents=True, exist_ok=True)
        #
        self.extra_knob_width = 26
        self.extra_knob_height = 26
        selfis.bb_l = []  
        self.bb_adj_l = []

    def classify_image(self, img_path):
        assert img_path.exists()
        img_orig = helplib.read_image_rgb(img_path)

        self.bb_l, img_kl = self.kl.locate_knobs(img_orig)
        kl_reject_flag = self._reject_stove_image(self.bb_l, img_orig, img_path)

        if kl_reject_flag==False:
            # create list of bboxes w/ coords adjusted for the original image
            this.bb_adj_l = self._adjust_bbox_coords(self.bb_l, img_orig)
            stove_is_on = self.eval_knobs(self.bb_adj_l, img_orig, img_path)
        else:
            self.bb_adj_l = []
            stove_is_on = False
        #
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


        bb_adj_l = []
        for bb in bb_l:
            bb_adj = helplib.adjust_bbox_coords(bb,
                                                 scalef,
                                                 h_offset,
                                                 self.extra_knob_width,
                                                 self.extra_knob_height,
                                                 img.shape[1], # orig width
                                                 img.shape[0])
            bb_adj_l.append(bb_adj)
        #
        return bb_adj_l

    def _reject_stove_image(self, bb_l, img, img_path):
        reject_flag = False
        if len(bb_l) > StoveClassifier.MAX_NUM_KNOBS:
            # filename is reject_path + img_path stem + "too-many-knobs" + png
            reject_fname = self.reject_path / f"{img_path.stem}-too-many-knobs.png"
            helplib.write_image(reject_fname, img)
            print(f"rejecting {img_path} because it has {len(bb_l)} knobs")
            reject_flag = True
        #
        return reject_flag

    def _eval_knobs(bb_l, img, img_path):
        """
        IN
        bb_l: list of BBox objects
        img: image (numpy array)
        img_path: path to image
        
        OUT
        stove_is_on: boolean
        """
        for n, bb in enumerate(bb_l):
            knob_img = helplib.extract_bbox(img, bb)
            knob_is_on = self.kc.is_on(knob_img)
            if knob_is_on:
                print(f"knob {n} is on")
                return True
            #


    

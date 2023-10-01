

import os
from pathlib import Path

# add ./src to path
import sys
sys.path.append('./src')
import knob_classifier
import knob_locator
import helplib
import enum

class StoveClasses(enum.Enum):
    ON = enum.auto()
    OFF = enum.auto()
    INDETERMINATE = enum.auto()

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
        self.reject_path = Path(reject_path).resolve()
        if reject_path.exists():
            assert reject_path.is_dir(), f"{reject_path} is not a directory"
        else:
            reject_path.mkdir(parents=True, exist_ok=True)
        #
        self.debug_out_path = Path(debug_out_path).resolve()
        if self.debug_out_path:
            assert self.debug_out_path.exists()
            assert self.debug_out_path.is_dir()
        #            
        self.extra_knob_width = 26
        self.extra_knob_height = 26
        self.bb_l = []  
        self.adjusted_box_coords_l = []

    def _write_img_with_bboxes(self, img, bb_l, fname):
        """
        for debug: mark a copy of img with all bounding boxes, then
        write to the debug_out_path
        """
        img_copy = img.copy()
        for bb in bb_l:
            img_copy = helplib.draw_box(img_copy, bb.x0, bb.y0, bb.x1, bb.y1)
        #
        img_fname = self.debug_out_path / fname
        helplib.write_image(self.debug_out_path / fname, img_copy)
        print(f"wrote image with knobs to {img_fname}")

    def _write_img_with_bbox_coords(self, img, box_coords_l, fname):
        img_copy = img.copy()
        for box_coords in box_coords_l:
            img_copy = helplib.draw_box(img_copy, box_coords[0], box_coords[1], box_coords[2], box_coords[3])
        #
        helplib.write_image(self.debug_out_path / fname, img_copy)

    def OLDstove_is_on(self, img_path, write_img_flag=False):
        assert img_path.exists()
        img_orig = helplib.read_image_rgb(img_path)

        self.bb_l, img_kl = self.kl.locate_knobs(img_orig)
        kl_reject_flag = self._reject_stove_image(self.bb_l, img_orig, img_path)

        if write_img_flag:
            self._write_img_with_bboxes(img_kl, self.bb_l, "knob-locator-out.png")

        if kl_reject_flag==False:
            # create list of bbox coords adjusted for the original image
            self.adjusted_box_coords_l = self._adjust_bbox_coords(self.bb_l, img_orig)
            if write_img_flag:
                self._write_img_with_bbox_coords(img_orig, self.adjusted_box_coords_l, "orig-img-with-bboxes.png")               
            #
            stove_is_on = self._eval_knobs(self.adjusted_box_coords_l, img_orig, img_path, write_img_flag)
        else:
            stove_is_on = False
            self.adjusted_box_coords_l = []
        #
        print(f"stove {img_path}: stove_is_on = {stove_is_on}")
        return stove_is_on
    
    def classify(self, img_path, write_img_flag=False):
        assert img_path.exists()
        img_orig = helplib.read_image_rgb(img_path)

        self.bb_l = []
        self.adjusted_box_coords_l = []
        stove_class = None

        self.bb_l, img_kl = self.kl.locate_knobs(img_orig)
        kl_reject_flag = self._reject_stove_image(self.bb_l, img_orig, img_path)

        if write_img_flag:
            self._write_img_with_bboxes(img_kl, self.bb_l, "knob-locator-out.png")

        if kl_reject_flag==True:
            stove_class = StoveClasses.INDETERMINATE
        else:
            # create list of bbox coords adjusted for the original image
            self.adjusted_box_coords_l = self._adjust_bbox_coords(self.bb_l, img_orig)
            if write_img_flag:
                self._write_img_with_bbox_coords(img_orig, self.adjusted_box_coords_l, "orig-img-with-bboxes.png")               
            #
            stove_class = self._eval_knobs(self.adjusted_box_coords_l, img_orig, img_path, write_img_flag)
        #
        print(f"stove {img_path}: stove_class = {stove_class}")

        assert stove_class != None
        return stove_class
    
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
        if len(bb_l) <= 0:
            reject_fname = self.reject_path / f"{img_path.stem}-no-knobs.png"
            helplib.write_image(reject_fname, img)
            print(f"rejecting {img_path} because it has {len(bb_l)} knobs")
            print(f"wrote to {reject_fname}")
            reject_flag = True
        elif len(bb_l) > StoveClassifier.MAX_NUM_KNOBS:
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
        stove_class
        """
        stove_class = None
        for n, coord in enumerate(adjusted_box_coords_l):
            knob_img= helplib.extract_knob_image(img, *coord)  # *coord is unpacking the tuple
            knob_result = self.kc.classify(knob_img)
            print(f"knob {n} coords: {coord}")
            if knob_result.knobclass == knob_classifier.KnobClass.ON:
                print(f"knob {n} is ON (value = {knob_result.on_score}")
                stove_is_on = stove_is_on or True
            elif knob_result.knobclass == knob_classifier.KnobClass.OFF:
                print(f"knob {n} is OFF (value = {knob_result.off_score}")
            else:
                print(f"knob {n} is INDETERMINATE (on_score = {knob_result.on_score}, off_score = {knob_result.off_score})")

                # if indeterminate, then write the WHOLE STOVE'S image to rejects
                # write an unmarked image so that it's easier to process
                reject_fname = self.reject_path / f"{img_path.stem}-indeterminate.png"
                helplib.write_image(reject_fname, img)

                # also write the knob image to rejects
                reject_fname = self.reject_path / f"{img_path.stem}-knob-{n:02d}-indeterminate.png"
                helplib.write_image(reject_fname, knob_img)
            #
                
            if write_img_flag:
                fname = self.debug_out_path / f"{img_path.stem}-knob-{n:02d}"
                if knob_result.knobclass == knob_classifier.KnobClass.ON:
                    fname = str(fname) + "-on.png"
                elif knob_result.knobclass == knob_classifier.KnobClass.OFF:
                    fname = str(fname) + "-off.png"
                else:
                    fname = str(fname) + "-indeterminate.png"

                helplib.write_image(fname, knob_img)
                print(f"wrote {fname}")
            #

        return stove_class



    

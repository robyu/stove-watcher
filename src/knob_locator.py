
import cv2
import os
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
from pathlib import Path
import boundingboxfile
import helplib

class KnobLocator:
    MAX_ROWS_COLS = 640  # max rows and cols of input image
    def __init__(self, eim_fname):
        self.eim_path = Path(eim_fname)
        assert self.eim_path.exists()
        self.runner = ImageImpulseRunner(str(self.eim_path.resolve()))
        self.model_info = self.runner.init()

    def locate_knobs(self, img_rgb):
        """
        resize image to MAX_ROWS_COLS x MAX_ROWS_COLS
        use EI runner to locate knobs
        extract list of bounding boxes from EI runner output
        return list of bounding boxes and EI processed image
        """
        assert img_rgb.shape[0] >= KnobLocator.MAX_ROWS_COLS
        assert img_rgb.shape[1] >= KnobLocator.MAX_ROWS_COLS

        # 
        if img_rgb.shape[0] != KnobLocator.MAX_ROWS_COLS or img_rgb.shape[1] != KnobLocator.MAX_ROWS_COLS:
            img_sqr = self._reshape_to_square(img_rgb)
        else:
            img_sqr = np.copy(img_rgb)
        #
        features, img_out = self.runner.get_features_from_image(img_sqr)
        res = self.runner.classify(features)
        #
        # convert EI runner output into bbox objects
        assert "bounding_boxes" in res["result"].keys() 
        bb_l = [boundingboxfile.BBox(d['x'], d['y'],
                                     d['width'], d['height'],
                                     value=d['value'],
                                     label=d['label']) for d in res['result']['bounding_boxes']]

        assert len(bb_l)==len(res['result']['bounding_boxes'])
        return bb_l, img_out

    def _reshape_to_square(self, img):
        """
        resize image to MAX_ROWS_COLS x MAX_ROWS_COLS
        
        use helplib.compute_crop_params to compute scalef and h_offset
        use cv2.resize to resize image
        return resized image
        """
        scalef, h_offset = helplib.compute_crop_params(img.shape[1], img.shape[0], KnobLocator.MAX_ROWS_COLS, KnobLocator.MAX_ROWS_COLS)
        img_crop = img[:, h_offset:h_offset+img.shape[0], :]
        img_sqr = cv2.resize(img_crop, (KnobLocator.MAX_ROWS_COLS, KnobLocator.MAX_ROWS_COLS))
        return img_sqr


    def __del__(self):
        self.runner.stop()


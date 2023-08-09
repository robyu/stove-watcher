
import cv2
import os
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
from pathlib import Path
import boundingboxfile

class KnobId:
    def __init__(self, eim_fname):
        self.eim_path = Path(eim_fname)
        assert self.eim_path.exists()
        self.runner = ImageImpulseRunner(str(self.eim_path.resolve()))
        self.model_info = self.runner.init()

    def locate_knobs(self, img_rgb):
        """
        returns
        bb_l: list of boundingboxfile.BBox objects
        img_out: EI-processed image output
        """
        features, img_out = self.runner.get_features_from_image(img_rgb)
        res = self.runner.classify(features)
        assert "bounding_boxes" in res["result"].keys()

        #
        # convert EI runner output into bbox objects
        bb_l = [boundingboxfile.BBox(d['x'], d['y'],
                                     d['width'], d['height'],
                                     value=d['value'],
                                     label=d['label']) for d in res['result']['bounding_boxes']]
        assert len(bb_l)==len(res['result']['bounding_boxes'])
        return bb_l, img_out

    def __del__(self):
        self.runner.stop()


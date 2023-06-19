
import cv2
import os
import sys, getopt
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
import json
import argparse
from pathlib import Path

class KnobExtractor:
    def __init__(self, eim_fname):
        import pudb;pudb.set_trace()
        self.eim_path = Path(eim_fname)
        assert self.eim_path.exists()
        self.runner = ImageImpulseRunner(str(self.eim_path.resolve()))
        self.model_info = self.runner.init()

    def locate_knobs(self, img_rgb):
        features, img_out = self.runner.get_features_from_image(img_rgb)
        res = self.runner.classify(features)
        assert "bounding_boxes" in res["result"].keys()
        return res["result"]["bounding_boxes"], img_out

    def __del__(self):
        self.runner.stop()


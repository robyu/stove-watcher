#!/usr/bin/env python

import cv2
import os
import sys
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
import knobid
import json
import argparse
import helplib
from pathlib import Path
import re

"""
standalone interface to knobid.py
process image files to locate knobs
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser')

    parser.add_argument('-m', '--modelfile', type=str, default='../modelfile.eim', help='Model filename')
    parser.add_argument('input_jpg', type=str, help='Input JPEG filename or input directory')
    parser.add_argument('boxes_dir', type=str, help='Output Bounding Box directory')

    args = parser.parse_args()

    # Check if mandatory arguments are provided
    if not args.input_jpg or not args.modelfile:
        parser.error('input_jpg and modelfile are mandatory arguments')

    return args

def make_box_json_fname(boxes_path, input_jpg):
    out_fname = boxes_path / Path(input_jpg.stem).with_suffix(".json")
    return out_fname

def classify_image(input_jpg, boxes_json, modelfile):
    assert input_jpg.exists()
    
    kid = knobid.KnobId(modelfile)
    img_rgb = helplib.read_image_rgb(input_jpg)
    bb_l, img_out = kid.locate_knobs(img_rgb)  # bb_l = list of bounding boxes
    
    # for bb in bb_l:
    #     print(f"val: {bb['value']:5.3} x: {bb['x']} y:{bb['y']} w:{bb['width']} h:{bb['height']}")
    #
    with open(boxes_json, "w") as f:
        json.dump(bb_l, f)
    #
    print(f"{input_jpg} -> {len(bb_l)} ->  {boxes_json}")

def classify_dir_images(input_path, boxes_path, modelfile):
    assert input_path.is_dir() 
    assert boxes_path.is_dir() 
    pat = r"(?:jpg|JPG|jpeg|JPEG)$"   # ? = non capturing group
    for fname in input_path.glob("*"):
        if re.search(pat, str(fname)):
            box_fname =make_box_json_fname(boxes_path, fname)
            classify_image(fname, box_fname, modelfile)
        #
    #


if __name__ == "__main__":
    args = parse_arguments()
    assert Path(args.modelfile).exists, f"could not locate model file {args.modelfile}"
    input_path = Path(args.input_jpg)
    boxes_path = Path(args.boxes_dir)

    if boxes_path.is_dir()==False:
        boxes_path.mkdir()
    #
    if input_path.is_dir():
        classify_dir_images(input_path,
                            boxes_path,
                            args.modelfile)
    elif input_path.is_file():
        classify_image(input_path,
                       boxes_path,
                       args.modelfile)
    else:
        assert False, "bad combination of input directories and paths"
    #

    
    
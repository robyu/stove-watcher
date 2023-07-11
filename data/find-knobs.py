#!/usr/bin/env python

import sys
sys.path.append("../src")

import cv2
import os
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
import knobid
import json
import argparse
import helplib

"""
standalone interface to knobid.py
process image files to locate knobs
"""

def parse_arguments():
    parser = argparse.ArgumentParser(description='Find Knobs')

    parser.add_argument('-m', '--modelfile', type=str, default='../modelfile.eim', help='Model filename')
    parser.add_argument('input_jpg', type=str, help='Input JPEG filename')
    parser.add_argument('boxes_json', type=str, help='Output Bounding Box JSON filename')

    args = parser.parse_args()

    # Check if mandatory arguments are provided
    if not args.input_jpg or not args.modelfile:
        parser.error('input_jpg and modelfile are mandatory arguments')

    return args

def classify(input_jpg, modelfile):
    kid = knobid.KnobId(modelfile)
    img_rgb = helplib.read_image_rgb(input_jpg)
    bb_l, img_out = kid.locate_knobs(img_rgb)  # bb_l = list of bounding boxes
    img_width = img_out.shape[0]
    img_height = img_out.shape[1]
    for bb in bb_l:
        print(f"val: {bb['value']:5.3} x: {bb['x']} y:{bb['y']} w:{bb['width']} h:{bb['height']}")
    return bb_l, img_width, img_height

if __name__ == "__main__":
    args = parse_arguments()
    bb_l, img_width, img_height = classify(args.input_jpg,
                                           args.modelfile)
    out_d = {"img_fname": args.input_jpg,
             "img_width": img_width,
             "img_height": img_height}
    out_d['bb'] = bb_l
    with open(args.boxes_json, "w") as f:
        json.dump(out_d, f)
        print(f"wrote bounding boxes to {args.boxes_json}")
    

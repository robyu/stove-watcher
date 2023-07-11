#!/bin/env python


import cv2
#import os
#import numpy as np
import json
import argparse
from pathlib import Path

import sys
sys.path.append("../src")
import helplib

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract Knobs')

    parser.add_argument('bb_json', type=str, help='JSON file with bounding boxes (output of find-knobs.py)')
    parser.add_argument('out_dir', type=str, help='Output directory')
    parser.add_argument('-t', '--value_thresh', type=float, default=0.95, help='bounding box minimum value')

    args = parser.parse_args()

    return args

def read_bb_json(bb_json_path):
    with open(bb_json_path, "r") as f:
        d = json.load(f)
    #
    print(f"input image: {d['img_fname']}")
    print(f"contains {len(d['bb'])} bounding boxes")

    return d

def read_orig_image(cropped_img_fname, orig_dir):
    orig_img_path = Path("out-renamed") / Path(cropped_img_fname).name
    assert orig_img_path.exists(), f"does not exist: {orig_img_path}"
    img_rgb = helplib.read_image_rgb(orig_img_path)
    return img_rgb
    
def compute_crop_params(orig_width, orig_height, cropped_width, cropped_height):
    assert cropped_width==cropped_height

    # resize.py resized orig image to height=640, width maintains ratio
    scalef = float(orig_height)/cropped_height
    assert scalef > 1.0

    # assume that we cropped the equal-sized "wings" of the resized image in
    # order to make a square image
    # the size of a wing is the horiz offset
    h_offset = int((orig_width - scalef * cropped_width)/2.0)
    return scalef, h_offset

def mark_boxes(img, bb_l, value_thresh):
    for n, box in enumerate(bb_l):
        if box['value'] < value_thresh:
            continue
        else:
            x = box['x']
            y = box['y']
            w = box['width']
            h = box['height']
            cv2.rectangle(img, (x, y), (x+w, y+h), (0, 255, 0), 2)
        #
    #
    #cv2.rectangle(img, (500, 500), (700, 700), (0, 255, 0), 10)
    return img

def adjust_bounding_boxes(bb_l, scalef, h_offset):
    adj_bb_l = [{'x': int(scalef * bb['x'] + h_offset),
                 'y': int(scalef * bb['y']),
                 'width': int(scalef * bb['width']),
                 'height': int(scalef * bb['height']),
                 'value': bb['value']} for bb in bb_l]
    return adj_bb_l
        
    

if __name__ == "__main__":
    args = parse_arguments()

    out_path = Path(args.out_dir)
    out_path.mkdir(exist_ok=True)

    bb_json_path = Path(args.bb_json)
    assert bb_json_path.exists(), f"file does not exist: {bb_json_path}"

    # keys: img_fname, img_width, img_height, bb (a list)
    bb_d = read_bb_json(bb_json_path)

    orig_img_rgb = read_orig_image(bb_d['img_fname'], orig_dir="out-renamed/")

    scalef, h_offset = compute_crop_params(orig_img_rgb.shape[1],
                                           orig_img_rgb.shape[0],
                                           bb_d['img_width'],
                                           bb_d['img_height'])

    adjusted_bb_l = adjust_bounding_boxes(bb_d['bb'], scalef, h_offset)

    marked_img = mark_boxes(orig_img_rgb, adjusted_bb_l, args.value_thresh)
    marked_fname = out_path / Path(bb_d['img_fname']).name
    print(f"marked image: {marked_fname}")
    cv2.imwrite(str(marked_fname), marked_img)
    


    

    

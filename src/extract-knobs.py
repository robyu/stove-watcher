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
import boundingboxfile

def parse_arguments():
    parser = argparse.ArgumentParser(description='Extract Knobs')

    default_thresh = 0.95
    
    parser.add_argument('-b', '--bbjson', type=Path, default=None, help='JSON file with bounding boxes (output of find-knobs.py)')
    parser.add_argument('-p', '--bbpickle', type=Path, default=None, help='pickle file with bounding boxes (output of bbtagger.py)')
    parser.add_argument('out_dir', type=Path, help='Output directory')
    parser.add_argument('orig_dir', type=Path, help='directory containing original image')
    parser.add_argument('-t', '--value_thresh', type=float, default=default_thresh, help=f'bounding box minimum value (default {default_thresh})')
    parser.add_argument('-x', '--extrawidth', type=int, default=30, help='extra bounding box width, in pixels')
    parser.add_argument('-y', '--extraheight', type=int, default=30, help='extra bounding box height, in pixels')

    args = parser.parse_args()

    return args

def read_bb_json(bb_json_path):
    print(f"reading bboxes from {bb_json_path}")
    with open(bb_json_path, "r") as f:
        d = json.load(f)

    #
    print(f"input image: {d['image_fname']}")
    print(f"contains {len(d['bounding_boxes'])} bounding boxes")

    return d

# def read_orig_image(cropped_img_fname, orig_dir):
#     orig_img_path = Path("out-renamed") / Path(cropped_img_fname).name
#     assert orig_img_path.exists(), f"does not exist: {orig_img_path}"
#     img_rgb = helplib.read_image_rgb(orig_img_path)
#     return img_rgb
    
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

def extract_boxes(img, bb_l, value_thresh, out_img_stem):
    for n, box in enumerate(bb_l):
        if box['value'] < value_thresh:
            continue
        else:
            x = box['x']
            y = box['y']
            w = box['width']
            h = box['height']
            knob = img[y:y+h, x:x+w]
            assert n < 100
            out_fname = out_img_stem.parent / f"{out_img_stem.name}-b{n:02d}.png"
            helplib.write_image(out_fname, knob)
        #
    #

def adjust_bounding_boxes(bb_l, scalef, h_offset, extra_width, extra_height):
    adj_bb_l = []
    for bb in bb_l:
        x0 = int(scalef * bb['x'] + h_offset - extra_width/2.0)
        if x0 <= 0:
            x0 = 0

        y0 = int(scalef * bb['y'] - extra_height/2.0)
        if y0 <= 0:
            y0 = 0

        adj_bb_l.append({'x': x0,
                         'y': y0,
                         'width': int(scalef * bb['width'] + extra_width),
                         'height': int(scalef * bb['height'] + extra_height),
                         'value': bb['value']})
    #
    return adj_bb_l
        

def extract_from_single_image(bb_d, # bbox dict
                              orig_path,
                              out_path,
                              value_thresh,
                              extra_width=0,
                              extra_height=0
                              ):

    # compose filenames of input image and output images
    orig_img_path = orig_path / Path(bb_d['image_fname']).name  # path of original (uncropped, un-resized) image
    assert orig_img_path.exists()
    out_img_path_stem = out_path / Path(bb_d['image_fname']).stem

    # load original image
    orig_img_rgb = helplib.read_image_rgb(orig_img_path)

    # recompute crop parameters to fit orig image
    scalef, h_offset = compute_crop_params(orig_img_rgb.shape[1],
                                           orig_img_rgb.shape[0],
                                           bb_d['image_width'],
                                           bb_d['image_height'])

    # derive new bounding box coords
    adjusted_bb_l = adjust_bounding_boxes(bb_d['bounding_boxes'], # list of bounding boxes
                                          scalef,
                                          h_offset,
                                          extra_width,
                                          extra_height)

    # extract each knob to a separate image file
    extract_boxes(orig_img_rgb, adjusted_bb_l, value_thresh, out_img_path_stem)

    # mark the knobs on the original image
    marked_img = mark_boxes(orig_img_rgb, adjusted_bb_l, value_thresh)
    marked_img_path = out_img_path_stem.with_suffix(".png")
    helplib.write_image(marked_img_path, marked_img)
    print(f"wrote marked image: {marked_img_path}")

def extract_from_all_images_json(bb_json_path,
                            orig_path,
                            out_path,
                            value_thresh,
                            extra_width=0,
                            extra_height=0):
    assert bb_json_path.is_dir()
    for bb_fname in bb_json_path.glob("*.json"):
        try:
            # keys: img_fname, img_width, img_height, bb (a list)
            bb_d = read_bb_json(bb_fname)
            
            extract_from_single_image(bb_d,
                                      orig_path,
                                      out_path,
                                      value_thresh,
                                      extra_width=extra_width,
                                      extra_height=extra_height)
        except FileNotFoundError:
            print(f"error while reading {bb_fname}. Skipping...")
        #
            
    #

def extract_from_all_images_pickle(bb_pickle_path,
                                   orig_path,
                                   out_path,
                                   value_thresh,
                                   extra_width=0,
                                   extra_height=0):
    assert bb_pickle_path.is_file()
    bbox_file = boundingboxfile.BBoxFile(bb_pickle_path)

    #for bb_fname in bb_json_path.glob("*.json"):
    for bb_fname in bbox_file.d.keys():
        try:
            bb_d = bbox_file.d[bb_fname]
            extract_from_single_image(bb_d,
                                      orig_path,
                                      out_path,
                                      value_thresh,
                                      extra_width=extra_width,
                                      extra_height=extra_height)
        except FileNotFoundError:
            print(f"error while reading {bb_fname}. Skipping...")
        #
            
    #
    
    
if __name__ == "__main__":
    args = parse_arguments()
    args.out_dir.mkdir(exist_ok=True)

    if args.bbjson:
        if args.bbjson.is_file():
            # keys: img_fname, img_width, img_height, bb (a list)
            bb_d = read_bb_json(args.bbjson)

            extract_from_single_image(bb_d,
                                      args.orig_dir,
                                      args.out_dir,
                                      args.value_thresh,
                                      extra_width=args.extrawidth,
                                      extra_height=args.extraheight)
        elif args.bbjson.is_dir():
            extract_from_all_images_json(args.bbjson,
                                    args.orig_dir,
                                    args.out_dir,
                                    args.value_thresh,
                                    extra_width=args.extrawidth,
                                    extra_height=args.extraheight)
        else:
            print(f"{args.bbjson} is neither a file nor a directory")
            sys.exit(1)
        #
    elif args.bbpickle and args.bbpickle.is_file():
            extract_from_all_images_pickle(args.bbpickle,
                                           args.orig_dir,
                                           args.out_dir,
                                           args.value_thresh,
                                           extra_width=args.extrawidth,
                                           extra_height=args.extraheight)
    else:
        print("invalid args")
        sys.exit(1)
    #
    


    

    

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
import boundingboxfile

"""
standalone interface to knobid.py
process image files to locate knobs

read pickle.rect file (or create a new one)
add bboxes to each image
write pickle.rect file

"""

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser')

    parser.add_argument('-m', '--modelfile', type=Path, default=Path('../modelfile.eim'), help='Model filename')
    parser.add_argument('input_path', type=Path, help='Input image filename or input directory')
    parser.add_argument('-o', '--out_path', type=Path,
                        default=Path('../data/out-find-knobs/'), help='directory for image/bounding box pickle file')
    parser.add_argument('-d', '--delete', action='store_true', default=False, help='delete existing rect.pickle')

    args = parser.parse_args()

    return args

def make_box_json_fname(out_path, image_path):
    out_fname = out_path / Path(image_path.stem).with_suffix(".json")
    return out_fname

def classify_image(image_path, modelfile, bbox_file):
    assert image_path.exists()
    
    kid = knobid.KnobId(modelfile)
    img_rgb = helplib.read_image_rgb(image_path)
    bb_l, img_out = kid.locate_knobs(img_rgb)  # bb_l = list of bounding boxes
    ibb = boundingboxfile.ImageBBoxes(image_path,
                                      img_rgb.shape[1], # width = cols
                                      img_rgb.shape[0] # height = rows
                                      )
    for bb in bb_l:
        ibb.add_bbox(boundingboxfile.BBox(bb['x'],
                                          bb['y'],
                                          bb['width'],
                                          bb['height'],
                                          value=bb['value']))
    #

    bbox_file[image_path] = ibb
    print(f"{image_path} has {len(bb_l)} knobs")

    return bbox_file

def classify_dir_images(input_path, modelfile, bbox_file):
    assert input_path.is_dir() 
    pat = r"(?:jpg|JPG|jpeg|JPEG|png)$"   # ? = non capturing group
    for fname in input_path.glob("*"):
        if re.search(pat, str(fname)):
            bbox_file = classify_image(fname, modelfile, bbox_file)
        #
    #
    return bbox_file

def init_bbox_file(out_path,
                   delete_flag):
    if delete_flag:
        pickle_path = boundingboxfile.make_pickle_path(out_path)
        if pickle_path.is_file():
            os.remove(pickle_path)
        #
    #
    bbox_file = boundingboxfile.BBoxFile(out_path)
    return bbox_file

if __name__ == "__main__":
    args = parse_arguments()
    assert args.modelfile.exists(), f"could not locate model file {args.modelfile}"

    if args.out_path.is_dir()==False:
        args.out_path.mkdir()
    #
    
    bbox_file = init_bbox_file(args.out_path,
                               args.delete)
    print(bbox_file)
    if args.input_path.is_dir():
        bbox_file = classify_dir_images(args.input_path,
                                        args.modelfile,
                                        bbox_file)
    else:
        assert args.input_path.is_file()
        bbox_file = classify_image(args.input_path,
                                   args.modelfile,
                                   bbox_file)
    
    #
    bbox_file.save()
    
    

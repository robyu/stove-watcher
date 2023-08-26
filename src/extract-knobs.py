#!/bin/env python


import cv2
#import os
import numpy as np
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
    default_extra_width = 10
    default_extra_height = 10
    
    parser.add_argument('-p', '--picklepath', type=Path, default=None, help='pickle file with bounding boxes (output of bbtagger.py)')
    parser.add_argument('-o','--out_dir', type=Path, default=Path('../data/out-extractedknobs'), help='Output directory for extracted knob images')
    parser.add_argument('-i', '--image_dir', type=Path, help='directory containing original (un-resized, ./out-renamed) image')
    parser.add_argument('-t', '--value_thresh', type=float, default=default_thresh, help=f'bounding box minimum value (default {default_thresh})')
    parser.add_argument('-x', '--extrawidth', type=int, default=default_extra_width, help=f'extra bounding box width, in pixels, default={default_extra_width}')
    parser.add_argument('-y', '--extraheight', type=int, default=default_extra_height, help=f'extra bounding box height, in pixels, default={default_extra_height}')

    args = parser.parse_args()

    return args

def draw_box(img, x0, y0, x1, y1):
    cv2.rectangle(img,
                  (x0, y0),
                  (x1, y1),
                  (0, 255, 0), 2)

    #cv2.rectangle(img, (500, 500), (700, 700), (0, 255, 0), 10)
    return img

def adjust_bounding_box(bb,
                        scalef,
                        h_offset,
                        extra_width,
                        extra_height,
                        orig_width,
                        orig_height,
                        ):
    x0 = int(scalef * bb.x + h_offset - extra_width/2.0)
    x0 = max(0, x0)

    y0 = int(scalef * bb.y - extra_height/2.0)
    y0 = max(0, y0)

    x1 = x0 + int(scalef * bb.w) + extra_width
    x1 = min(x1, orig_width)
    
    y1 = y0 + int(scalef * bb.h) + extra_height
    y1 = min(y1, orig_height)
    return x0, y0, x1, y1
        
# def make_knob_fname(out_dir, orig_img_fname, n):
#     out_fname = out_dir / f"{orig_img_fname.stem}-b{n:02d}.png"
#     return out_fname

def extract_knobs_single_image(ibb, # imageBBox object
                               orig_img_fname,
                               out_dir,
                               value_thresh,
                               extra_width=0,
                               extra_height=0,
                               ):

    # compose filenames of input image and output images
    assert orig_img_fname.exists()
    out_img_path_stem = out_dir / ibb.image_path.stem

    # load original image
    orig_img_rgb = helplib.read_image_rgb(orig_img_fname)

    # recompute crop parameters to fit orig image
    scalef, h_offset = helplib.compute_crop_params(orig_img_rgb.shape[1],
                                                   orig_img_rgb.shape[0],
                                                   ibb.image_width,
                                                   ibb.image_height)
    marked_img = np.copy(orig_img_rgb)
    n = 0
    for bb in ibb:
        if bb.value < value_thresh:
            continue
        #
        
        x0, y0, x1, y1 = adjust_bounding_box(bb,
                                             scalef,
                                             h_offset,
                                             extra_width,
                                             extra_height,
                                             orig_img_rgb.shape[1], # orig width
                                             orig_img_rgb.shape[0]) # orig height
        #
        # extract knob image
        knob_img = orig_img_rgb[y0:y1, x0:x1]
        # knob_fname = make_knob_fname(out_dir,
        #                              orig_img_fname,
        #                              n)
        knob_fname = out_img_path_stem.parent / f"{out_img_path_stem.name}-b{n:02d}.png"
        helplib.write_image(knob_fname, knob_img)

        #
        # mark up image
        marked_img = draw_box(marked_img,
                                   x0, y0, x1, y1)
        # increment only if valid threshold
        n += 1
    #

    marked_img_path = out_img_path_stem.with_suffix(".png")
    helplib.write_image(marked_img_path, marked_img)
    print(f"wrote marked image: {marked_img_path}")


def find_orig_img_fname(resized_fname,
                    orig_dir):
    orig_fname = orig_dir / resized_fname.name

    suffix_l = ['.png', '.jpg']

    # try suffixes until we find a valid filename
    found_img = False
    for s in suffix_l:
        probe_fname = orig_fname.with_suffix(s)
        if probe_fname.exists():
            found_img=True
            break
        #
    #
    assert found_img, f"original image not found corresponding to  {resized_fname}"
    return probe_fname

def extract_knobs_all_images(bb_file,
                             orig_dir,
                             out_dir,
                             value_thresh = .90,
                             extra_width=0,
                             extra_height=0,
                             ):
    assert isinstance(bb_file, boundingboxfile.BBoxFile)
    assert orig_dir.is_dir()
    out_dir.mkdir(exist_ok=True, parents=True)

    for bb_fname, ibb in bbox_file.images_d.items():
        print(f"resized image: {bb_fname}")
        try:
            orig_img_fname = find_orig_img_fname(Path(bb_fname),
                                                 orig_dir)
        except:
            print(f"could not original image {orig_img_fname}")
            continue
        extract_knobs_single_image(ibb,
                                   orig_img_fname,
                                   out_dir,
                                   value_thresh,
                                   extra_width,
                                   extra_height)

                
    #
    
    
if __name__ == "__main__":
    args = parse_arguments()

    bbox_file = boundingboxfile.BBoxFile(args.picklepath)

    extract_knobs_all_images(bbox_file,
                             args.image_dir,
                             args.out_dir,
                             value_thresh=args.value_thresh,
                             extra_width=args.extrawidth,
                             extra_height=args.extraheight)

    


    

    

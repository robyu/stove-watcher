#!/bin/env python
import cv2
import sys
import json
import subprocess
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser')

    parser.add_argument('-i', '--in_image_fname', type=str, default='output.jpg', help='Input JPEG filename')
    parser.add_argument('-b', '--box_fname', type=str, default='output.json', help='JSON file with box coords')
    parser.add_argument('-o', '--out_image_fname', type=str, default='output-marked.jpg', help='Output JPEG filename')
    parser.add_argument('-d', '--display_image_flag', action='store_true', default=False, help='display image with feh app')
    parser.add_argument('-t', '--threshold', type=float, default=0.0, help='value threshold (default 0.0)')

    args = parser.parse_args()

    return args


def mark_boxes(in_image_fname,
               box_fname,
               out_image_fname,
               display_image_flag=False,
               value_thresh = 0.0):
    # Read the image
    image = cv2.imread(in_image_fname)

    # read the box coordinates
    with open(box_fname, "r") as f:
        boxes_l = json.load(f)
        
    scalex = 1.0
    scaley = 1.0
    xoffset=0
    yoffset=0
    for n, box in enumerate(boxes_l):
        if box['value'] < value_thresh:
            continue
        else:
            x =int(scalex * box['x']) + xoffset
            y = int(scaley * box['y']) + yoffset
            width = int(scalex * box['width'])
            #width = int(660/120.0)
            height = int(scaley * box['height'])
            #height = int(660/120.0)
            print(f"[{n}] x={x} y={y} width={width} height={height} value={box['value']:3.4f}")
            # Draw the rectangle on the image
            cv2.rectangle(image, (x, y), (x+width, y+height), (0, 255, 0), 2)

    cv2.imwrite(out_image_fname, image)
    #

    if display_image_flag:
        cmd_l = ['feh', f"{out_image_fname}"]
        subprocess.run(cmd_l)
        
        
if __name__=="__main__":
    args = parse_arguments()
    mark_boxes(args.in_image_fname,
               args.box_fname,
               args.out_image_fname,
               display_image_flag = args.display_image_flag,
               value_thresh = args.threshold)
    

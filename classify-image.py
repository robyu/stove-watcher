#!/usr/bin/env python

#import device_patches       # Device specific patches for Jetson Nano (needs to be before importing cv2)

import cv2
import os
import sys, getopt
import numpy as np
from edge_impulse_linux.image import ImageImpulseRunner
import json
import argparse

def parse_arguments():
    parser = argparse.ArgumentParser(description='Argument Parser')

    parser.add_argument('modelfile', type=str, help='Model filename')
    parser.add_argument('input_jpg', type=str, help='Input JPEG filename')
    parser.add_argument('-o', '--output_jpg', type=str, default='output.jpg', help='Output JPEG filename')
    parser.add_argument('-b', '--boxes_json', type=str, default='output.json', help='Boxes JSON filename')

    args = parser.parse_args()

    # Check if mandatory arguments are provided
    if not args.input_jpg or not args.modelfile:
        parser.error('input_jpg and modelfile are mandatory arguments')

    return args

def classify(input_jpg, modelfile, output_jpg, boxes_json):

    dir_path = os.path.dirname(os.path.realpath(__file__))
    modelfile = os.path.join(dir_path, modelfile)

    print('MODEL: ' + modelfile)

    with ImageImpulseRunner(modelfile) as runner:
        try:
            model_info = runner.init()
            print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')
            labels = model_info['model_parameters']['labels']

            img = cv2.imread(input_jpg)
            if img is None:
                print(f"Failed to load image {input_jpg}")
                exit(1)

            # imread returns images in BGR format, so we need to convert to RGB
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            features, cropped = runner.get_features_from_image(img)

            res = runner.classify(features)

            if "classification" in res["result"].keys():
                print('Result (%d ms.) ' % (res['timing']['dsp'] + res['timing']['classification']), end='')
                for label in labels:
                    score = res['result']['classification'][label]
                    print('%s: %.2f\t' % (label, score), end='')
                print('', flush=True)

            elif "bounding_boxes" in res["result"].keys():
                print('Found %d bounding boxes (%d ms.)' % (len(res["result"]["bounding_boxes"]), res['timing']['dsp'] + res['timing']['classification']))
                for bb in res["result"]["bounding_boxes"]:
                    print('\t%s (%.2f): x=%d y=%d w=%d h=%d' % (bb['label'], bb['value'], bb['x'], bb['y'], bb['width'], bb['height']))
                with open(boxes_json, "w") as f:
                    json.dump(res["result"]["bounding_boxes"], f)
                    print(f"wrote bounding boxes to {boxes_json}")
                #
            # the image will be resized and cropped, save a copy of the picture here
            # so you can see what's being passed into the classifier
            cv2.imwrite(output_jpg, cv2.cvtColor(cropped, cv2.COLOR_RGB2BGR))
            print(f"wrote classifier input image to {output_jpg}")

        finally:
            if (runner):
                runner.stop()

if __name__ == "__main__":
    args = parse_arguments()
    classify(args.input_jpg,
             args.modelfile,
             args.output_jpg,
             args.boxes_json)
    
    

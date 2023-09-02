#!/bin/bash

# (stovewatcher) ryu@debian11:src$ python   knobtagger.py --help
# usage: knobtagger.py [-h] [-d] [-q PEAK_DELTA_THRESH] [-r PMETRIC_THRESH] [-s SKEW_THRESH] image_path
# positional arguments:
#   image_path            path to image
# options:
#   -h, --help            show this help message and exit
#   -d, --disp            display/plot stuff
#   -q PEAK_DELTA_THRESH, --peak_delta_thresh PEAK_DELTA_THRESH
#                         peak delta threshold; default 50
#   -r PMETRIC_THRESH, --pmetric_thresh PMETRIC_THRESH
#                         peakiness metric threshold; default 50.0
#   -s SKEW_THRESH, --skew_thresh SKEW_THRESH

# python   knobtagger.py -r 30  ../data/out-extract-knobs/bbtagger/general
# python   knobtagger.py -r 30  ../data/out-extract-knobs/bbtagger/robert-twist
# python   knobtagger.py -r 30  ../data/out-extract-knobs/bbtagger/single-twist
python   knobtagger.py -q 110 -r 30  ../data/out-extract-knobs/bbtagger/synth-twist
#python   knobtagger.py -r 27  ../data/out-extract-knobs/bbtagger/towel-twist

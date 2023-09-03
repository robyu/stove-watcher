#!/bin/bash

#
# skip the automatic tagging--it doesn't really work
# just copy all images into the "off" directories and sort them by hand
SRCDIR=../data/out-extract-knobs/ei
DESTDIR=../data/out-knobtagger/ei
#python   knobtagger.py --all_off  ../data/out-extract-knobs/ei/general
python   knobtagger.py --all_off  ../data/out-extract-knobs/ei/robert-twist
python   knobtagger.py --all_off  ../data/out-extract-knobs/ei/single-twist
python   knobtagger.py --all_off  ../data/out-extract-knobs/ei/synth-twist
python   knobtagger.py --all_off  ../data/out-extract-knobs/ei/towel-twist



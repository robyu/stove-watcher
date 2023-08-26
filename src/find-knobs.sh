#!/bin/bash

#
# run NN model to find knobs
python find-knobs.py -m ../modelfile_r7.eim  -o ../data/out-find-knobs/general      ../data/out-resized/general
python find-knobs.py -m ../modelfile_r7.eim  -o ../data/out-find-knobs/robert-twist ../data/out-resized/robert-twist
python find-knobs.py -m ../modelfile_r7.eim  -o ../data/out-find-knobs/single-twist ../data/out-resized/single-twist
python find-knobs.py -m ../modelfile_r7.eim  -o ../data/out-find-knobs/synth-twist  ../data/out-resized/synth-twist 
python find-knobs.py -m ../modelfile_r7.eim  -o ../data/out-find-knobs/towel-twist  ../data/out-resized/towel-twist 



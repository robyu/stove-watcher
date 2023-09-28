#!/bin/bash

os=$(uname -s)

if [ "$os" == "Linux" ]; then
  echo "Linux"
  MODELFILE=../modelfiles/linux-x86-64/knobhead-r08.eim
elif [ "$os" == "Darwin" ]; then
  echo "macOS"
  MODELFILE=../modelfiles/macos/knobhead-r08.eim
else
    echo "Unknown"
    exit 1
fi

#
# run NN model to find knobs
python find-knobs.py -m "$MODELFILE"  -o ../data/out-find-knobs/general      ../data/out-resized/general
python find-knobs.py -m "$MODELFILE"  -o ../data/out-find-knobs/robert-twist ../data/out-resized/robert-twist
python find-knobs.py -m "$MODELFILE"  -o ../data/out-find-knobs/single-twist ../data/out-resized/single-twist
python find-knobs.py -m "$MODELFILE"  -o ../data/out-find-knobs/synth-twist  ../data/out-resized/synth-twist 
python find-knobs.py -m "$MODELFILE"  -o ../data/out-find-knobs/towel-twist  ../data/out-resized/towel-twist 



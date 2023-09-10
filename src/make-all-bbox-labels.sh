#!/bin/bash
#
# use bbtagger to convert all bbox pickle files into EI-compatible JSON files
#
python bbtagger.py writejson -p ../data/out-bbtagger/general/ ../data/out-resized/general/
python bbtagger.py writejson -p ../data/out-bbtagger/robert-twist ../data/out-resized/robert-twist/
python bbtagger.py writejson -p ../data/out-bbtagger/single-twist/ ../data/out-resized/single-twist/
python bbtagger.py writejson -p ../data/out-bbtagger/synth-twist/ ../data/out-resized/synth-twist/
python bbtagger.py writejson -p ../data/out-bbtagger/towel-twist/ ../data/out-resized/towel-twist/

find ../data -name *.labels -print

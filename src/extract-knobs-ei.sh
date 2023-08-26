#!/bin/bash
OUTDIR=../data/out-extract-knobs/ei
PICKLEDIR=../data/out-find-knobs
SRCDIR=../data/out-renamed

#
# extract knob images from hand-tagged images
python extract-knobs.py -x 26 -y 26 -o "$OUTDIR/general"      -p "$PICKLEDIR/general"      -i "$SRCDIR/general"
python extract-knobs.py -x 26 -y 26 -o "$OUTDIR/robert-twist" -p "$PICKLEDIR/robert-twist" -i "$SRCDIR/robert-twist"
python extract-knobs.py -x 26 -y 26 -o "$OUTDIR/single-twist" -p "$PICKLEDIR/single-twist" -i "$SRCDIR/single-twist"
python extract-knobs.py -x 26 -y 26 -o "$OUTDIR/synth-twist"  -p "$PICKLEDIR/synth-twist"  -i "$SRCDIR/synth-twist"
python extract-knobs.py -x 26 -y 26 -o "$OUTDIR/towel-twist"  -p "$PICKLEDIR/towel-twist"  -i "$SRCDIR/towel-twist"




# python extract-knobs.py   -o ../data/out-extract-knobs/ei -p ../data/out-bbtagger/robert-twist -i ../data/out-renamed/robert-twist
# python extract-knobs.py   -o ../data/out-extract-knobs/ei -p ../data/out-bbtagger/single-twist -i ../data/out-renamed/single-twist
# python extract-knobs.py   -o ../data/out-extract-knobs/ei -p ../data/out-bbtagger/synth-twist  -i ../data/out-renamed/synth-twist
# python extract-knobs.py   -o ../data/out-extract-knobs/ei -p ../data/out-bbtagger/towel-twist  -i ../data/out-renamed/towel-twist


#!/bin/bash
OUTDIR=../data/out-extract-knobs/bbtagger
PICKLEDIR=../data/out-bbtagger
SRCDIR=../data/out-renamed
#
# extract knob images from hand-tagged images
python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/boresight1"  -p "$PICKLEDIR/boresight1"  -i "$SRCDIR//boresight1"
# python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/general"      -p "$PICKLEDIR/general"      -i "$SRCDIR/general"
# python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/robert-twist" -p "$PICKLEDIR/robert-twist" -i "$SRCDIR//robert-twist"
# python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/single-twist" -p "$PICKLEDIR/single-twist" -i "$SRCDIR//single-twist"
# python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/synth-twist"  -p "$PICKLEDIR/synth-twist"  -i "$SRCDIR//synth-twist"
# python extract-knobs.py  -x 0 -y 0  -o "$OUTDIR/towel-twist"  -p "$PICKLEDIR/towel-twist"  -i "$SRCDIR//towel-twist"


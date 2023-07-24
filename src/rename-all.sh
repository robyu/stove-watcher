#!/bin/bash
SRC="../data/stove-orig"
DEST="../data/out-renamed"
python rename.py general      "$SRC"/general      "$DEST"/general
python rename.py robert-twist "$SRC"/robert-twist "$DEST"/robert-twist
python rename.py single-twist "$SRC"/single-twist "$DEST"/single-twist
python rename.py synth-twist  "$SRC"/synth-twist  "$DEST"/synth-twist
python rename.py towel-twist  "$SRC"/towel-twist  "$DEST"/towel-twist


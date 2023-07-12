#!/bin/bash
OUT_DIR="./out-boxes"

mkdir -p "$OUT_DIR"

for file in "out-resized"/*.jpg; do   # note placement of end quote wrt wildcard! glob shit
    #echo $file
    #echo "|"
    OUT_JSON="$OUT_DIR"/$(basename "$file")
    OUT_JSON="${OUT_JSON%.jpg}.json"
    #echo "processing $OUT_JSON"
    #echo './find-knobs.py -m ../modelfile_r6.eim file "$OUT_JSON"'
    ./find-knobs.py  -m ../modelfile_r6.eim $file "$OUT_JSON"
done

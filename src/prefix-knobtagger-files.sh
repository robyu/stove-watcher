#!/bin/bash

#
# rename *.png files to add prefix to hand-tagged knob images

rename_files() {
    local directory="$1"
    local prefix="$2"
    shopt -s nullglob   # if glob returns no files, then return empty string

    for file in "$directory"/*.png; do
        local new_name="${file%/*}/${prefix}-${file##*/}"
        mv "$file" "$new_name"
	echo "${file}" - "${new_name}"
    done
}

#
# knob images extracted from hand-boxed images
BASEDIR=../data/out-knobtagger/bbtagger
dirs=("$BASEDIR/general/on"
      "$BASEDIR/general/off"
      "$BASEDIR/robert-twist/on"
      "$BASEDIR/robert-twist/off"
      "$BASEDIR/single-twist/on"
      "$BASEDIR/single-twist/off"
      "$BASEDIR/synth-twist/on"
      "$BASEDIR/synth-twist/off"
      "$BASEDIR/towel-twist/on"
      "$BASEDIR/towel-twist/off")

prefix="bbt"
for dir in "${dirs[@]}"; do
    echo "$dir";
    #ls -l "$dir";
    rename_files "$dir" "$prefix";
done      

#
# knob-images extracted by Edge Impulse-processed images
BASEDIR=../data/out-knobtagger/ei
dirs=("$BASEDIR/general/on"
      "$BASEDIR/general/off"
      "$BASEDIR/robert-twist/on"
      "$BASEDIR/robert-twist/off"
      "$BASEDIR/single-twist/on"
      "$BASEDIR/single-twist/off"
      "$BASEDIR/synth-twist/on"
      "$BASEDIR/synth-twist/off"
      "$BASEDIR/towel-twist/on"
      "$BASEDIR/towel-twist/off")
prefix="ei"
for dir in "${dirs[@]}"; do
    echo "$dir";
    #ls -l "$dir";
    rename_files "$dir" "$prefix";
done      

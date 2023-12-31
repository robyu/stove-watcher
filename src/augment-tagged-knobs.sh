#!/bin/bash

#
# convert off knob images into on images by rotating them

SRC="../data/tagged-knobs/ei/general"

INPUT_DIR="$SRC/on"
DEST="$SRC/augmented_off"

# Delete rotated directory if it exists
if [ -d "$DEST" ]; then
    rm -rf "$DEST"
fi

echo input dir = "$INPUT_DIR"

# Create the rotated directory if it doesn't exist
mkdir -p "$DEST"

# Loop through all PNG files in the src directory
for file in "$INPUT_DIR"/*.png; do
    # Get the filename without the directory path
    filename=$(basename "$file")
    echo "$INPUT_DIR/$filename" 
    
    # Rotate 90 degrees
    convert "$file" -rotate 90 "$DEST/${filename%.*}_90.png"
    
    # Rotate 180 degrees
    convert "$file" -rotate 180 "$DEST/${filename%.*}_180.png"

    # flip LR
    convert "$file" -flop "$DEST/${filename%.*}_flip.png"
done
echo dest dir = "$DEST"


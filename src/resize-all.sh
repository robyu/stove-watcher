#!/bin/bash
SRCDIR="../data/out-renamed"
DESTDIR="../data/out-resized"
rm -rf "$DESTDIR"
for subdir in "$SRCDIR"/*; do
    if [ -d "$subdir" ]; then
	python resize.py  "$subdir" "$DESTDIR"/$(basename "$subdir")
    fi
done

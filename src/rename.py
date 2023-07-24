#!/bin/env python

import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import argparse
import fnmatch
import os

def parse_args():
    parser = argparse.ArgumentParser(description="Rename image files")
    parser.add_argument("prefix", help="file prefix")
    parser.add_argument("in_dir", help="Input directory")
    parser.add_argument("out_dir", help="Output directory")
    return parser.parse_args()

def rename_files(prefix, in_dir, out_dir):
    in_path = Path(in_dir)
    out_path = Path(out_dir)

    if out_path.is_dir()==False:
        os.makedirs(out_path)  # makedirs: make intermed directories

    n = 0
    for file_path in in_path.glob("*"):
        if fnmatch.fnmatch(file_path, "*.jpg"):
            new_fname = f"{prefix}-{n:04d}.jpg"
            
            # Copy the file to the output directory with the new filename
            new_file_path = out_path / new_fname
            print(f"{file_path} -> {new_file_path}")
            shutil.copy2(file_path, new_file_path)

            n += 1

if __name__ == "__main__":
    args = parse_args()
    rename_files(args.prefix, args.in_dir, args.out_dir)

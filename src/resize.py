#!/usr/bin/env python
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import subprocess
import argparse
import os

def parse_args():
    help_text = '''
    Image Resize Tool
    =======================
    This script resizes image files using the ImageMagick convert command.

    Usage example:
    python script.py input_dir output_dir
    '''

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=help_text)
    parser.add_argument('in_dir', type=Path, help='Input directory containing image files')
    parser.add_argument('out_dir', type=Path, help='Output directory for resized image files')

    args = parser.parse_args()

    # Check if both arguments are provided
    assert args.in_dir, 'Input directory is missing'
    assert args.out_dir, 'Output directory is missing'

    return args


def resize_files(in_path, out_path):
    assert in_path.is_dir()

    if out_path.is_dir()==False:
        os.makedirs(out_path)

    for file_path in in_path.glob("*.jpg"):
        out_fname = out_path / Path(file_path.name).with_suffix('.png')
        cmd_list = ['convert', file_path,
                    '-resize', 'x640>',   # "x": compute width automatically, "660>" = max height 660
                    "-crop", "640x640+170+0", # crop to 660x660, offset is (170, 0)
                    out_fname]
        print(f"resize {file_path} -> {out_fname}")
        subprocess.run(cmd_list)

if __name__ == '__main__':
    args = parse_args()

    resize_files(args.in_dir, args.out_dir)


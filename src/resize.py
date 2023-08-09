#!/usr/bin/env python
import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import subprocess
import argparse
import os
import helplib

MAX_ROWS_COLS=640

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

    for img_path in in_path.glob("*.jpg"):
        assert img_path.exists()
        img = helplib.read_image_rgb(img_path)
        orig_rows = img.shape[0]
        orig_cols = img.shape[1]
        assert orig_rows < orig_cols

        scalef, h_offset = helplib.compute_crop_params(orig_cols,
                                                       orig_rows,
                                                       MAX_ROWS_COLS,
                                                       MAX_ROWS_COLS)
        
        out_fname = out_path / Path(img_path.name).with_suffix('.png')
        cmd_list = ['convert', img_path,
                    '-crop', f'{orig_rows}x{orig_rows}+{h_offset}+{0}',
                    '-resize', f'{MAX_ROWS_COLS}x{MAX_ROWS_COLS}',
                    out_fname]
        print(f"resize {img_path} -> {out_fname}")
        subprocess.run(cmd_list)

if __name__ == '__main__':
    args = parse_args()

    resize_files(args.in_dir, args.out_dir)


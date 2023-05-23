import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import subprocess
import argparse

def parse_args():
    help_text = '''
    Image Resize Tool
    =======================
    This script resizes image files using the ImageMagick convert command.

    Usage example:
    python script.py input_dir output_dir
    '''

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, epilog=help_text)
    parser.add_argument('in_dir', help='Input directory containing image files')
    parser.add_argument('out_dir', help='Output directory for resized image files')

    args = parser.parse_args()

    # Check if both arguments are provided
    assert args.in_dir, 'Input directory is missing'
    assert args.out_dir, 'Output directory is missing'

    return args


def resize_files(in_dir, out_dir):
    in_path = Path(in_dir)
    out_path = Path(out_dir)

    for file_path in in_path.glob("*.jpg"):
        out_fname = out_path / file_path.name
        cmd_list = ['convert', file_path, '-resize', '1000x>', out_fname]
        print(f"resize {file_path} -> {out_fname}")
        subprocess.run(cmd_list)




if __name__ == '__main__':
    args = parse_args()
    in_dir = args.in_dir
    out_dir = args.out_dir

    resize_files(in_dir, out_dir)


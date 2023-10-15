#!/usr/bin/env python

from pathlib import Path
import shutil
import sys
sys.path.append('./src')
import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("dir", type=Path, help="directory to process")
    parser.add_argument("-p", "--prefix", type=str, help="prefix to add to all files in dir")
    parser.add_argument("-f", "--filter-pat", type=str, help="filter pattern for files to process")
    parser.add_argument('-d', '--dry-run', action='store_true', default=False, help='dry run')

    return parser.parse_args()


if __name__=="__main__":
    args = parse_args()
    assert args.dir.exists(), f"directory {args.dir} does not exist"
    assert args.prefix is not None, f"prefix must be specified"

    # get list of files to process
    # include only *.png and *.jpg files
    image_ext = ('.png', '.jpg', '.jpeg')
    # find only files which end in image_ext
    files_l = [Path(f.name) for f in args.dir.iterdir() if f.suffix.lower() in image_ext]

    # if filter pattern is specified, then filter the list of files
    # assume that the filter pattern is a substring of the filename
    if args.filter_pat is not None:
        files_l = [f for f in files_l if args.filter_pat in f.name]

    # rename all files in files_l by adding prefix to filename
    for f in files_l:
        # if args.filter_pat, then replace "filter_pat" with "prefix"
        if args.filter_pat is not None:
            new_name = f.name.replace(args.filter_pat, args.prefix)
        else:
            new_name = args.prefix + f.name
        
        new_f = args.dir / new_name
        print(f"renaming {f} to {new_name}")
        old_f = args.dir / f
        if not args.dry_run:

            shutil.move(old_f, new_f)
        #
    
    

    


    
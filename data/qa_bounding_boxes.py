import json
from pathlib import Path
import sys
import argparse
import fnmatch

def parse_arguments():
    parser = argparse.ArgumentParser(description='perform QA on bounding box JSON files')

    parser.add_argument('json_dir', type=str, help='directory with bounding box json files')
    args = parser.parse_args()

    return args

def get_num_bb(d):
    try:
        num_bb = len(d['bb'])  # 'bb' should be an array of bounding boxes
    except:
        num_bb = 0
    #
    return num_bb

def validate_files(dir_path):
    retval = False
    fname_pat = "[a-zA-Z]*.json"
    for fname in dir_path.glob("*.json"):
        if fnmatch.fnmatch(fname.name, fname_pat):
            with open(fname, "r") as f:
                d = json.load(f)
                num_bb = get_num_bb(d)
                if (num_bb <= 0) or (num_bb > 7) :
                    retval = retval or True
                    print(f"{fname} contains {num_bb} boxes")
                #
            #
        #
    #
    return retval

if __name__ == "__main__":
    args = parse_arguments()

    json_dir_path = Path(args.json_dir)
    assert json_dir_path.is_dir(), f"{d} is not a directory"
    retval = validate_files(json_dir_path)
    if retval:
        sys.exit(1)
    else:
        sys.exit(0)
    


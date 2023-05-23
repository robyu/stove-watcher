import shutil
from pathlib import Path
from datetime import datetime
from PIL import Image
import argparse

def parse_args():
    parser = argparse.ArgumentParser(description="Rename image files based on their properties.")
    parser.add_argument("in_dir", help="Input directory")
    parser.add_argument("out_dir", help="Output directory")
    return parser.parse_args()

def rename_files(in_dir, out_dir):
    in_path = Path(in_dir)
    out_path = Path(out_dir)

    for file_path in in_path.glob("*.jpg"):
        if file_path.is_file():
            # Extract date and time information from the filename
            try:
                parts = file_path.stem.split(" on ")[1].split(" at ")
                date_str, time_str = parts[0], parts[1]
            except IndexError:
                print(f"could not parse {file_path}")
                continue   

            # time_str = "8.02 PM #2"
            #     or   = "8.02 PM"
            time_str_l = time_str.split(" #")
            
            # Parse the date and time strings
            date = datetime.strptime(date_str, "%m-%d-%y")
            time = datetime.strptime(time_str_l[0], "%I.%M %p")

            try:
                ext = f"{time_str_l[1]}"
            except IndexError:
                ext = "0"
            #

            # Format the date and time as desired
            formatted_date = date.strftime("%Y-%m-%d")
            formatted_time = time.strftime("%H-%M")


            image = Image.open(file_path)
            width = image.width

            if width==1080:
                prefix="apple"
            elif width==1616:
                prefix="logi"
            else:
                assert False, f"unrecognized camera image width={width}"
            
            # Construct the new filename
            new_filename = f"{prefix}-{formatted_date}-{formatted_time}-{ext}.jpg"
            
            # Copy the file to the output directory with the new filename
            new_file_path = out_path / new_filename
            print(f"{file_path} -> {new_file_path}")
            shutil.copy2(file_path, new_file_path)

if __name__ == "__main__":
    args = parse_args()
    rename_files(args.in_dir, args.out_dir)

from PIL import Image, ImageTk
from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle
import argparse
import boundingboxfile

def parse_args():
    parser = argparse.ArgumentParser()

    valid_cmds = ['tag','tagall','tagnext','convert','audit','writejson']
    parser.add_argument("cmd", choices=valid_cmds, help=f'one of {valid_cmds}')
    parser.add_argument("image_path", default='', type=Path)
    return parser.parse_args()

class Tagger:
    def __init__(self, image_fname):
        self.image_path = Path(image_fname)
        self.root = Tk()
        self.root.title(f"{self.image_path.stem}")

        # Open the image using Pillow
        image = Image.open(str(self.image_path))

        # Create a canvas to display the image
        self.canvas = Canvas(self.root, width=image.width, height=image.height)
        self.canvas.pack()

        # Convert the image to PhotoImage format
        self.image_tk = ImageTk.PhotoImage(image)

        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.curr_rect = None
        self.retval = 0

        #
        # load rects pickle file and extract or initialize
        # the list of rectangles for this file
        self.bbox_file = boundingboxfile.BBoxFile(self.image_path)
    
    def display(self):
        # Display the image
        self.canvas.create_image(0, 0, image=self.image_tk, anchor="nw")

        #
        # gotta add the rects to the canvas after it's been displayed
        # otherwise they don't show up
        #self.rect_l = self.all_files_dict_to_rects(self.all_files_d, self.image_path.name)
        self.rect_l = self.bbox_file.to_rects(self.canvas, self.image_path.name)

        
        callback = partial(self.handle_keypress, self)
        self.root.bind("<KeyPress>", self.handle_keypress)  # amazingly, "self" is correctly passed to the callback
        self.root.bind("<ButtonPress-1>", self.handle_mousepress)
        self.root.bind("<B1-Motion>", self.handle_mousedrag)
        self.root.bind("<ButtonRelease-1>", self.handle_mouseup)
        self.root.mainloop()

    def handle_keypress(self, event):
        print(f"got keypress {event.char.lower()}")
        if event.char.lower() == 'q':
            #
            # copy canvas rect list back into all_files_d
            self.bbox_file.update_bboxes(self.image_path.name, self.canvas, self.rect_l)
            #self.all_files_d[self.image_path.name] = self.convert_rects_to_bboxes(self.rect_l)

            self.bbox_file.save()
            # with open(self.pickle_path, "wb") as f:
            #     pickle.dump(self.all_files_d, f)
            #
            
            #
            # write bounding box JSON and quit

            # self.write_bb_json()
            #sys.exit(0)
            if event.char=='q':
                self.retval = 0 # normal exit
            else:
                self.retval = 1  # exit loop
            #
            self.root.destroy() # destroy tk window and stop main loop
            
        elif event.char.lower() == 'd':
            # delete most recent rect
            self.delete_last_rect()
        #

    def delete_last_rect(self):
        try:
            rect = self.rect_l.pop()
            self.canvas.delete(rect)
            
        except IndexError:
            print("no bounding boxes in list")
        #
        

    def handle_mousepress(self, event):
        self.start_x, self.start_y = event.x, event.y
        print(f"mousepress @ {self.start_x}, {self.start_y}")
        

    def handle_mousedrag(self, event):
        self.end_x, self.end_y = event.x, event.y

        # draw the rect
        if self.curr_rect:
            self.canvas.delete(self.curr_rect)
        #
        self.curr_rect = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                      self.end_x, self.end_y,
                                                      outline='green')  

        print(f"mousedrag {self.end_x}, {self.end_y}")

    def handle_mouseup(self, event):
        self.rect_l.append(self.curr_rect)
        self.curr_rect = None

    #
    # def destroy(self):
    #     self.canvas.delete(self.image_tk)
        

    # def __del__(self):
    #     self.destroy()

def find_jpg_files(image_dir):
    assert image_dir.is_dir()
    jpg_files = list(image_dir.glob('**/*.jpg'))
    return jpg_files

    
def tag_one_image(image_fname):
    assert image_fname.exists()
    tagger = Tagger(image_fname)
    tagger.display()
    print(tagger.retval)
    return tagger.retval
    

def tag_all_images(image_dir):
    assert image_dir.is_dir()
    #
    # load each image in the directory
    
    files_l = find_jpg_files(image_dir.parent)
    for p in files_l:
        retval = tag_one_image(p)
        if retval:
            break  # user indicated to exit the entire loop
    #
    

def tag_next_untagged(image_dir):
    assert image_dir.is_dir()
    bboxfile = boundingboxfile.BBoxFile(image_dir)
    files_l = find_jpg_files(image_dir.parent)

    for file_path in files_l:
        fname = file_path.name
        if fname in bboxfile.images_d and len(bboxfile.images_d[fname].bb_l) <= 0:
            print(fname)
            break
        #
    #
    target_path = image_dir / fname
    print(target_path)
    assert target_path.exists()
    tag_one_image(target_path)
    

def audit_tags(image_dir):
    assert image_dir.is_dir()
    bboxfile = boundingboxfile.BBoxFile(image_dir)
    files_l = find_jpg_files(image_dir)

    for n, file_path in enumerate(files_l):
        fname = file_path.name
        num_bboxes = 0
        is_tagged = False
        if fname in bboxfile.images_d:
            num_bboxes = len(bboxfile.images_d[fname].bb_l)
            is_tagged = True
        #
        print(f"""\
|{n:3}| {fname:30s} | {str(is_tagged):5s} | {num_bboxes:2d} |""")
    #
    
def bbox_file_to_json(image_dir):
    assert image_dir.is_dir()
    bboxfile = boundingboxfile.BBoxFile(image_dir)
    bboxfile.write_json()

if __name__=="__main__":
    args = parse_args()
    assert isinstance(args.image_path, Path)
    #
    if args.cmd=="tag":
        #
        # tag a single image
        if Path(args.image_path).exists()==False:
            args.image_path = Path('out-resized/apple-2023-05-14-19-18-2.jpg')
        #
        tag_one_image(args.image_path)
    elif args.cmd=="tagall":
        #
        # iterate through all images in a path
        tag_all_images(args.image_path)
    elif args.cmd=="tagnext":
        #
        # tag next untagged image
        tag_next_untagged(args.image_path)
    elif args.cmd=="audit":
        audit_tags(args.image_path)
    elif args.cmd=="writejson":
        bbox_file_to_json(args.image_path)
    else:
        print(f"Unrecognized command: {args.cmd}")
        sys.exit(0)
    #
    
    
    

from PIL import Image, ImageTk
from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle
import argparse
import boundingboxfile
import os

def parse_args():
    parser = argparse.ArgumentParser()

    valid_cmds = ['tag','tagall','tagnext','audit','writejson']
    parser.add_argument("cmd", choices=valid_cmds, help=f'one of {valid_cmds}')
    parser.add_argument("image_path", type=Path, help="path to (resized, square) image or image dir")
    parser.add_argument("-p", "--pickle_path", type=Path,
                        help=f"destination path for output rect.pickle (OR for audit: pickle input path)")
    parser.add_argument("-d", "--delete", action="store_true", default=False, help="delete existing rect.pickle")
    parser.add_argument("--fix_value_field", action="store_true", default=False, help="for all bbox entries, set value field to 1.0 and then rewrite rects.pickle")
    parser.add_argument("--boresight_bboxes", action="store_true", default=False, help="initialize image with boresight bounding boxes")
    return parser.parse_args()

class Tagger:
    MIN_RECT_WIDTH = 24
    MIN_RECT_HEIGHT = 24
    def __init__(self, image_path, out_path, init_bbox_l = None):
        assert isinstance(image_path, Path)
        self.image_path = image_path
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
        assert isinstance(out_path, Path)
        self.bbox_file = boundingboxfile.BBoxFile(out_path)

        if self.image_path in self.bbox_file:
            self.img_bboxes = self.bbox_file[self.image_path]
        else:
            # create new img_bbox obj and add to the collection
            self.img_bboxes = boundingboxfile.ImageBBoxes(self.image_path,
                                                          image.width, # cols : width
                                                          image.height  # rows : height
                                                          )
            self.bbox_file[self.image_path] = self.img_bboxes
        #

        # if an init_bbox_l was provided, then overwrite self.img_bboxes.bbox_l
        if init_bbox_l:
            print("using initial bbox list:")
            for n, bbox in enumerate(init_bbox_l):
                print(f"{n}: {bbox}")
            self.img_bboxes.bbox_l = init_bbox_l.copy()


        #
        # bounding boxes are mirrored in canvas_rect_l (a list of rect objects on the canvas)
        # and bbox_l, a list of bounding boxes
        self.canvas_rect_l = []   # a list of canvas rects; this is necessary for bookkeeping when deleting bbox
        self.bbox_l = self.img_bboxes.bbox_l # a more convenient way of accessing self.img_bboxes.bbox_l
    
    def display(self):
        # Display the image
        self.canvas.create_image(0, 0, image=self.image_tk, anchor="nw")

        #
        # gotta add the rects to the canvas after it's been displayed
        # otherwise they don't show up
        #self.canvas_rect_l = self.all_files_dict_to_rects(self.all_files_d, self.image_path.name)
        self.canvas_rect_l = self.img_bboxes.bboxes_to_canvas_rects(self.canvas)
        
        callback = partial(self.handle_keypress, self)
        self.root.bind("<KeyPress>", self.handle_keypress)  # amazingly, "self" is correctly passed to the callback
        self.root.bind("<ButtonPress-1>", self.handle_mousepress)
        self.root.bind("<B1-Motion>", self.handle_mousedrag)
        self.root.bind("<ButtonRelease-1>", self.handle_mouseup)
        self.root.mainloop()

        return self.bbox_l

    def handle_keypress(self, event):
        #print(f"got keypress {event.char.lower()}")
        if event.char.lower() == 'q':
            #
            # copy canvas rect list back into all_files_d
            #self.img_bboxes.canvas_rects_to_bboxes(self.canvas, self.canvas_rect_l)
            assert len(self.bbox_l) == len(self.canvas_rect_l)
            print("-----------------------------")
            print(f"Writing bounding {len(self.bbox_l)} boxes")
            print(self.img_bboxes)
            self.bbox_file[self.image_path] = self.img_bboxes
            #self.all_files_d[self.image_path.name] = self.convert_rects_to_bboxes(self.rect_l)

            self.bbox_file.save()
            # with open(self.pickle_path, "wb") as f:
            #     pickle.dump(self.all_files_d, f)
            #
            
            #
            # write bounding box JSON and quit

            # self.write_bb_json()
            #sys.exit(0)
            if event.char=='q':    # lower case: continue to next image
                self.retval = 0 # normal exit
            else:
                assert event.char=='Q'
                self.retval = 1  # exit loop
            #
            self.root.destroy() # destroy tk window and stop main loop
            
        elif event.char.lower() == 'd':
            # delete most recent rect
            self.delete_last_rect()
        #

    def delete_last_rect(self):
        try:
            rect = self.canvas_rect_l.pop()
            self.canvas.delete(rect)

            # also delete from bbox list
            self.bbox_l.pop()

            
        except IndexError:
            print("no bounding boxes in list")
        #'q'
        

    def handle_mousepress(self, event):
        self.start_x, self.start_y = event.x, event.y
        print(f"mousepress @ {self.start_x}, {self.start_y}")
        

    def handle_mousedrag(self, event):
        self.end_x, self.end_y = event.x, event.y

        #
        # limit min size of rect
        if self.end_x - self.start_x < Tagger.MIN_RECT_WIDTH:
            self.end_x = self.start_x + Tagger.MIN_RECT_WIDTH
        if self.end_y - self.start_y < Tagger.MIN_RECT_HEIGHT:
            self.end_y = self.start_y + Tagger.MIN_RECT_HEIGHT
        #
        
        # draw the rect
        if self.curr_rect:
            self.canvas.delete(self.curr_rect)
        #
        self.curr_rect = self.canvas.create_rectangle(self.start_x, self.start_y,
                                                      self.end_x, self.end_y,
                                                      outline='green', width=3)  

        #print(f"mousedrag w={self.end_x-self.start_x}, h={self.end_y-self.start_y}")

    def handle_mouseup(self, event):
        rect_coords = self.canvas.bbox(self.curr_rect) # get coords from canvas
        if len(self.canvas_rect_l) < 7 and rect_coords[0] >= 0 and rect_coords[1] >= 0:
            #
            # add new rect to list of canvas rects
            self.canvas_rect_l.append(self.curr_rect)

            # add new rect to bbox list

            bbox = boundingboxfile.canvas_rect_to_bbox(rect_coords)
            self.img_bboxes.add_bbox(bbox)
        else:
            print("too many bounding boxes or bad coords")    
            self.canvas.delete(self.curr_rect)
        #
        self.curr_rect = None


BORESIGHT_BBOX_L = [boundingboxfile.BBox(243, 301, 28, 28),
                    boundingboxfile.BBox(273, 302, 28, 28),
                    boundingboxfile.BBox(384, 301, 28, 28),
                    boundingboxfile.BBox(414, 302, 28, 28),
                    boundingboxfile.BBox(434, 296, 28, 28),
                    boundingboxfile.BBox(455, 304, 28, 28),
                    boundingboxfile.BBox(483, 301, 28, 28)]

def find_img_files(image_dir):
    assert image_dir.is_dir()
    jpg_files = list(image_dir.glob('*.jpg'))
    png_files = list(image_dir.glob('*.png'))
    img_files = sorted(jpg_files + png_files)
    return img_files

    
def tag_one_image(image_path, pickle_path, init_bbox_l = None):
    assert image_path.exists()
    print(f"tagging {image_path}")
    pickle_path.mkdir(exist_ok=True, parents=True)
    tagger = Tagger(image_path, pickle_path, init_bbox_l = init_bbox_l)
    tagger.display()
    print(tagger.retval)
    return tagger.retval
    

def tag_all_images(image_dir, pickle_path, init_bbox_l = None):
    assert image_dir.is_dir()
    #
    # load each image in the directory
    
    files_l = find_img_files(image_dir)
    for p in files_l:
        retval = tag_one_image(p, pickle_path, init_bbox_l = init_bbox_l)
        if retval:
            break  # user indicated to exit the entire loop
    #
    

def tag_next_untagged(image_dir, pickle_path, init_bbox_l = None):
    assert image_dir.is_dir()
    bboxfile = boundingboxfile.BBoxFile(pickle_path)
    files_l = find_img_files(image_dir)
    assert len(files_l) > 0

    for file_path in files_l:
        fname = file_path.name
        if fname in bboxfile.images_d and len(bboxfile.images_d[fname].bb_l) <= 0:
            print(f"{fname} is tagged")
            break
        #
    #
    target_path = image_dir / fname
    print(target_path)
    assert target_path.exists()
    tag_one_image(target_path, pickle_path, init_bbox_l)
    

def audit_tags(image_dir, pickle_path, fix_value_field):
    assert image_dir.is_dir(), f"{image_dir} is not a directory"
    assert pickle_path.is_dir(), f"{pickle_path} is not a directory"
    bboxfile = boundingboxfile.BBoxFile(pickle_path)
    files_l = find_img_files(image_dir)

    print(f"""\
|{"#":3s}| {"file path":30s} | {"tagged?":8s} | {"# boxes":10s} |""")
    for n, file_path in enumerate(files_l):
        num_bboxes = 0
        is_tagged = False
        if file_path in bboxfile:
            num_bboxes = (bboxfile[file_path]).get_num_bboxes()
            is_tagged = True
        #
        print(f"""\
|{n:3}| {(str(file_path))[-30:]:30s} | {str(is_tagged):8s} | {num_bboxes:10d} |""")
    #

    if fix_value_field:
        print("setting value field in all bounding boxes")
        for image_fname, bbi in bboxfile.images_d.items():
            for bb in bbi:
                bb.value = 1.0
            #
        #
        bboxfile.save()
    #
    
def bbox_file_to_json(pickle_path, out_path):
    assert pickle_path.is_dir()
    assert out_path.is_dir()
    bboxfile = boundingboxfile.BBoxFile(pickle_path)
    bboxfile.write_ei_json(out_path)

if __name__=="__main__":
    args = parse_args()
    assert isinstance(args.image_path, Path)

    if args.delete==True:
        assert args.cmd != "audit"
        assert args.cmd != "writejson"
        pickle_path = boundingboxfile.BBoxFile.make_pickle_path(args.pickle_path)
        if pickle_path.is_file():
            os.remove(pickle_path)
    #
    init_bbox_l = None
    if args.boresight_bboxes:
        # make a copy of the list object so that the original isn't modified
        init_bbox_l = BORESIGHT_BBOX_L.copy()

    if args.cmd=="tag":
        #
        # tag a single image
        if Path(args.image_path).exists()==False:
            # for testing
            args.image_path = Path('../data/out-resized/general/general-0000.png')
        #
        tag_one_image(args.image_path,
                      args.pickle_path,
                      init_bbox_l = init_bbox_l)
    elif args.cmd=="tagall":

        #
        # iterate through all images in a path
        tag_all_images(args.image_path,
                       args.pickle_path,
                       init_bbox_l = init_bbox_l)
    elif args.cmd=="tagnext":
        #
        # tag next untagged image
        tag_next_untagged(args.image_path,
                          args.pickle_path,
                          init_bbox_l = init_bbox_l)
    elif args.cmd=="audit":
        audit_tags(args.image_path,
                   args.pickle_path,
                   args.fix_value_field)
            
    elif args.cmd=="writejson":
        bbox_file_to_json(args.pickle_path,
                          args.image_path)
    else:
        print(f"Unrecognized command: {args.cmd}")
        sys.exit(0)
    #
    
    
    

from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle

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

        #
        # load rects pickle file and extract or initialize
        # the list of rectangles for this file
        self.pickle_path = self.image_path.parent / "rects.pickle"
        self.all_files_d = self.load_bbox_pickle()

    def load_bbox_pickle(self):
        try:
            with open(self.pickle_path, "rb") as f:
                d = pickle.load(f)
        except FileNotFoundError:
            print(f"could not load {self.pickle_path}")
            d = {}
        #

        return d

    def all_files_dict_to_rects(self, all_files_d, image_name):
        """
        the pickle contains a dictionary of the form:
        {
            "file_a.jpg" : [{
                "x0" : x0,
                "y0" : y0,
                "x1" : x1,
                "y1" : y1},
                ... (more rects)
                ],
           "file_b.jpg": [
                {rect},
                {rect}, ...
                ]
        }

        look up "file.jpg" in the pickle dict and convert to rect list
        """
        if image_name in all_files_d:
            #
            # copy pickle entry to a list
            bbox_l = all_files_d[image_name]
        else:
            print(f"{self.pickle_path} does not contain a preexisting entry for {image_name}")
            bbox_l = []
        #
        rect_l = self.convert_bboxes_to_rects(self.canvas, bbox_l)
        return rect_l

    def convert_bboxes_to_rects(self, canvas, bbox_l):
        rect_l = []
        for bbox in bbox_l:
            rect = canvas.create_rectangle(bbox[0],
                                           bbox[1],
                                           bbox[0] + bbox[2],
                                           bbox[1] + bbox[3],
                                           outline='green')
            rect_l.append(rect)
        #
        return rect_l
    

    def convert_rects_to_bboxes(self, rect_l):
        #
        # convert list of canvas rects to list of bounding box tuples
        bbox_l = []
        for rect in rect_l:
            bbox_l.append(self.convert_rect_to_bbox(rect))
        #
        return bbox_l
            
    
    def display(self):
        # Display the image
        self.canvas.create_image(0, 0, image=self.image_tk, anchor="nw")

        #
        # gotta add the rects to the canvas after it's been displayed
        # otherwise they don't show up
        self.rect_l = self.all_files_dict_to_rects(self.all_files_d, self.image_path.name)

        
        callback = partial(self.handle_keypress, self)
        self.root.bind("<KeyPress>", self.handle_keypress)  # amazingly, "self" is correctly passed to the callback
        self.root.bind("<ButtonPress-1>", self.handle_mousepress)
        self.root.bind("<B1-Motion>", self.handle_mousedrag)
        self.root.bind("<ButtonRelease-1>", self.handle_mouseup)
        self.root.mainloop()

    def make_out_fname(self):
        assert isinstance(self.image_path, Path)
        out_fname = self.image_path.parent / Path(self.image_path.stem).with_extension('.json')
        return out_fname

    def convert_rect_to_bbox(self, rect):
        """
        convert a convas rect to a bounding box tuple
        """
        bbox = self.canvas.bbox(rect)  # get tuple coord
        x = bbox[0]
        y = bbox[1]
        w = bbox[2] - x
        assert w > 0
        h = bbox[3] - y
        assert h > 0
        print(f"{bbox}")

        bbox = [x, y, w, h]
        return bbox

        
    def write_bbox_json(self):
        out_fname = self.make_out_fname()
        d = self.convert_rects_to_dict(self)
        with open(out_fname, "w") as f:
            json.dump(d, f)
        #
        
    def handle_keypress(self, event):
        print(f"got keypress {event.char.lower()}")
        if event.char.lower() == 'q':
            #
            # copy canvas rect list back into all_files_d
            self.all_files_d[self.image_path.name] = self.convert_rects_to_bboxes(self.rect_l)

            with open(self.pickle_path, "wb") as f:
                pickle.dump(self.all_files_d, f)
            #
            
            #
            # write bounding box JSON and quit

            # self.write_bb_json()
            sys.exit(0)
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
        
        
if __name__=="__main__":
    tagger = Tagger('out-resized/apple-2023-05-14-19-18-2.jpg')
    tagger.display()
    
    
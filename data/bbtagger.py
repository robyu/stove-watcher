from PIL import Image, ImageDraw, ImageTk
from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json

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

        self.rect_l = []
        self.start_x = 0
        self.start_y = 0
        self.end_x = 0
        self.end_y = 0
        self.curr_rect = None

    def display(self):
        # Display the image
        self.canvas.create_image(0, 0, image=self.image_tk, anchor="nw")
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

    def convert_rect_to_bb(self, rect):
        bbox = self.canvas.bbox(rect)  # get tuple coord
        x = bbox[0]
        y = bbox[1]
        w = bbox[2] - x
        assert w > 0
        h = bbox[3] - y
        assert h > 0
        print(f"{bbox}")

        # the JSON format for a bounding box is specified in
        # https://docs.edgeimpulse.com/docs/edge-impulse-cli/cli-uploader#bounding-boxes
        bb_d = {'label':'knob',
                'x': x,
                'y': y,
                'width': w,
                'height': h]
        return bb_d
                    

    def convert_rects_to_dict(self):
        bb_l = []
        for rect in self.rect_l:
            bb_d = self.convert_rect_to_bb(rect)
            bb_l.append(bb_d)
        #

        # JSON should look like:
        # {
        #     "mypicture.jpg": [{
        #         "label": ...
        #     },
        #     {  .. another box
        #     }]
        # }
        d[self.image_path.name] = bb_l
        return d
        
    def write_bb_json(self):
        out_fname = self.make_out_fname()
        d = self.convert_rects_to_dict(self)
        with open(out_fname, "w") as f:
            json.dump(d, f)
        #
        
    def handle_keypress(self, event):
        print(f"got keypress {event.char.lower()}")
        if event.char.lower() == 'q':
            #
            # write bounding box JSON and quit
QUIT HERE
            self.write_bb_json()
            sys.exit(0)
        elif event.char.lower() == 'd':
            # delete most recent bounding box
            self.delete_last_bb()
        #

    def delete_last_bb(self):
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
    
    

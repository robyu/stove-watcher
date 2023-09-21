from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle
import cv2

class BBox:
    def __init__(self, x, y, w, h, value=1.0, label='knob'):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.value = value
        self.label = label

    def to_dict(self):
        return self.__dict__

    def __str__(self):
        s = f"x:{self.x} y:{self.y} w:{self.w} h:{self.h} value={self.value} label={self.label}"
        return s
            
    # allow me to access self.x1 and have the object automatically calculate self.x + self.w
    @property
    def x0(self):
        return self.x

    @property
    def x1(self):
        return self.x + self.w
    
    @property
    def y0(self):
        return self.y
    
    @property
    def y1(self):
        return self.y + self.h
    

class ImageBBoxes:
    """
    an object representing an image path and its corresponding bounding boxes
    """
    def __init__(self, image_path, width, height):
        assert isinstance(image_path, Path)
        self.image_path = image_path
        self.image_width = width
        self.image_height = height
        self.bbox_l = []   # list of BBoxes

    def __str__(self):
        #import pudb; pudb.set_trace()
        s = f"image_path={str(self.image_path)}, width={self.image_width}, height={self.image_height})"
        for bbox in self.bbox_l:
            s += f"\n{str(bbox)}"
        #
        return s

    def add_bbox(self, bbox):
        assert bbox.x >= 0
        assert bbox.y >= 0
        assert bbox.x + bbox.w  < self.image_width
        assert bbox.y + bbox.h  < self.image_height
        self.bbox_l.append(bbox)

    def get_num_bboxes(self):
        return len(self.bbox_l)

    def __iter__(self):
        """
        this will let me use ImageBBoxes as an iterator
        to iterate through bboxes, e.g.

        for bbox in image_bboxes:
            print(bbox)
        """
        return iter(self.bbox_l)


    def bboxes_to_canvas_rects(self, canvas):
        """
        given an IBB and a canvas,
        add all bounding boxes to canvas rects
        and return a list of the rect object IDs
        """
        rect_l = []
        for n, bbox in enumerate(self.bbox_l):
            print(f"box {n}: {bbox}")
            rect = canvas.create_rectangle(bbox.x,
                                           bbox.y,
                                           bbox.x + bbox.w,
                                           bbox.y + bbox.h,
                                           outline='green', width=3)
            rect_l.append(rect)
        #
        return rect_l
        
    def _canvas_rect_to_bbox(self, rect_coords):
        """
        convert a canvas rect to a bounding box tuple
        """
        x = rect_coords[0]
        y = rect_coords[1]
        w = rect_coords[2] - x
        assert w > 0
        h = rect_coords[3] - y
        assert h > 0
        print(f"{rect_coords}")

        bbox = BBox(x, y, w, h)
        return bbox

    def canvas_rects_to_bboxes(self, canvas, rect_l):
        # clear the ibb list of bboxes and re-add each rect
        self.bbox_l = []
        for rect in rect_l:
            rect_coords = canvas.bbox(rect)  # get tuple coord
            assert len(rect_coords)==4
            bbox_coords = self._canvas_rect_to_bbox(rect_coords)
            self.bbox_l.append(bbox_coords)
        #


        
# def make_id_dict(image_path,
#                  image_width,
#                  image_height,
#                  bb_l # list of bounding boxes
#                  ):
#     assert image_width >= image_height
#     d = {'image_path': str(image_path),
#          'image_width': image_width,
#          'image_height': image_height,
#          'bounding_boxes': bb_l}
#     return d
        
# def id_dict_to_bboxes(d):
#     assert "image_path" in d
#     assert "image_width" in d
#     assert "image_height" in d
#     assert "bounding_boxes" in d

#     ibb = ImageBBoxes(d['image_path'],
#                       d['image_width'],
#                       d['image_height'])
    
#     for bbox in d['bounding_boxes']:
#         ibb.append(bbox)
#     #
#     return ibb


        


# TODO: move to helplib
def mark_bb_on_img(img, bb):
    cv2.rectangle(img,
                  (bb.x, bb.y),
                  (bb.x + bb.w,
                   bb.y  + bb.h),
                  (0, 255, 0), 3)
    
    
class BBoxFile:  
    """
    a collection of Images and their associated bounding boxes, 
    stored as a pickle file
    """
    def __init__(self, pickle_dir):
        self.pickle_path = make_pickle_path(pickle_dir)
        print(f"pickle path is {self.pickle_path}...", end='')

        # images_d is associative array: {image filename: image stats & list of bounding boxes}
        self.images_d = {}

        try:
            with open(self.pickle_path, "rb") as f:
                self.images_d = pickle.load(f)
        except FileNotFoundError:
            print(f"NOT FOUND")
        else:
            print("loaded")
        #

    @staticmethod
    def make_pickle_path(file_path):
        if file_path.is_dir():
            bb_path = image_path
        else:
            bb_path = image_path.parent
        #
        assert bb_path.is_dir()

        pickle_path = bb_path / "rects.pickle"
        return pickle_path

    def __str__(self):
        s = f"pickle path: {self.pickle_path}\n"
        for k, v in self.images_d.items():
            s +=  f"{str(k):30s}: {v.get_num_bboxes()} boxes\n"
        #
        return s
        

    def __getitem__(self, key):
        """
        implements bbox_file[fname] = bbox_file.images_d[fname]
        """
        if isinstance(key, str)==False:
            key = str(key)
        return self.images_d[key]

    def __setitem__(self, key, value):
        """
        implements bbox_file[fname] = ImageBBoxes
        equiv to bbox_file.images_d[fname] = ImageBBoxes
        """
        if isinstance(key, str)==False:
            key = str(key)
        assert isinstance(value, ImageBBoxes)
        self.images_d[key] = value

    def __contains__(self, key):
        """
        implements "fname in bbox_file"
        equiv to "fname in bbox_file.images_d"
        """
        if isinstance(key, str)==False:
            key = str(key)
        return key in self.images_d

    
    def save(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.images_d, f)

        print(f"wrote {self.pickle_path}")


        

    def _make_json_fname(self, out_path):
        out_fname = out_path / "bounding_boxes.labels"
        return out_fname
        
    def write_ei_json(self, out_path):
        assert out_path.is_dir()
        json_d = {"version": 1,
                  "type": "bounding-box-labels"}
        bbox_per_file_d = {}
        for image_fname in self.images_d.keys():
            imagebbox = self.images_d[image_fname]
            if len(imagebbox.bbox_l) <= 0:
                # no bounding boxes for this file, so skip to next
                continue
            else:
                # json_bbox_l = [{"label":"knob",
                #                "x": bbox[0],
                #                "y": bbox[1],
                #                "width": bbox[2],
                #                "height": bbox[3]} for bbox in imagebbox.bbox_l] 
                json_bbox_l = [{"label":"knob",
                                "value": 1.0, # confidence for manually tagged bboxes is 100%
                               "x": bbox.x,
                                "y": bbox.y,
                                "width": bbox.w,
                                "height": bbox.h} for bbox in imagebbox]

                # each dictionary entry key is *just* the name,
                # not the path
                bbox_per_file_d[Path(image_fname).name] = json_bbox_l
            #
        #
        json_d['boundingBoxes'] = bbox_per_file_d
        out_fname = self._make_json_fname(out_path)
        with open(out_fname, "w") as f:
            json.dump(json_d, f)
        #
        print(f"wrote EI JSON to {out_fname}")
        

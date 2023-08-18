from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle
import cv2

class BBox:
    def __init__(self, x, y, w, h, value=0.0, label='knob'):
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
            

class ImageBBoxes:
    def __init__(self, image_path, width, height):
        assert isinstance(image_path, Path)
        self.image_path = image_path
        self.image_width = width
        self.image_height = height
        self.bbox_l = []   # list of BBoxes

    def __str__(self):
        import pudb; pudb.set_trace()
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
        to iterate through bboxes
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
                                           outline='green')
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


        

def make_pickle_path(image_path):
    if image_path.is_dir():
        bb_path = image_path
    else:
        bb_path = image_path.parent
    #
    assert bb_path.is_dir()

    pickle_path = bb_path / "rects.pickle"
    return pickle_path

def mark_bb_on_img(img, bb):
    cv2.rectangle(img,
                  (bb.x, bb.y),
                  (bb.x + bb.w,
                   bb.y  + bb.h),
                  (0, 255, 0), 2)
    
    
class BBoxFile:  # a collection of ImageBBoxes
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


        

    def _make_json_fname(self):
        out_fname = self.pickle_path.parent / "bounding_boxes.labels"
        return out_fname
        
    def write_ei_json(self):
        json_d = {"version": 1,
                  "type": "bounding-box-labels"}
        bbox_per_file_l = []
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
                               "x": bbox.x,
                                "y": bbox.y,
                                "width": bbox.w,
                                "height": bbox.h} for bbox in imagebbox] 
                file_bbox_d = {f"{image_fname}": json_bbox_l}
                bbox_per_file_l.append(file_bbox_d)
            #
        #
        json_d['boundingBoxes'] = bbox_per_file_l
        out_fname = self._make_json_fname()
        with open(out_fname, "w") as f:
            json.dump(json_d, f)
        #
        print(f"wrote EI JSON to {out_fname}")
        

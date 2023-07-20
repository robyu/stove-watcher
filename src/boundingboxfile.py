from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle

class ImageBBoxes:
    def __init__(self, image_path, width, height):
        assert isinstance(image_path, Path)
        self.image_path = image_path
        self.image_width = width
        self.image_height = height
        self.bbox_l = []   # tuple (x0, y0, x1, y1)

    def add_bbox(self, bbox):
        assert len(bbox)==4
        assert bbox[0] >= 0
        assert bbox[1] >= 0
        assert bbox[0] + bbox[2] < self.image_width
        assert bbox[1] + bbox[3] < self.image_height
        self.bbox_l.append(bbox)

    def get_num_bboxes(self):
        return len(self.bbox_l)

    def __iter__(self):
        """
        this will let me use ImageBBoxes as an iterator
        to iterate through bboxes
        """
        return iter(self.bbox_l)

def bboxes_to_canvas_rects(ibb, canvas):
    """
    given an IBB and a canvas,
    add all bounding boxes to canvas rects
    """
    for bbox in ibb.bbox_l:
        rect = canvas.create_rectangle(bbox[0],
                                       bbox[1],
                                       bbox[0] + bbox[2],
                                       bbox[1] + bbox[3],
                                       outline='green')
        rect_l.append(rect)
    #
    return rect_l

def canvas_rects_to_bboxes(canvas, ibb):
    rect_l = canvas.find_withtag("rectangle")
    for rect in rect_l:
        rect_coords = canvas.bbox(rect)  # get tuple coord
        assert len(rect_coords)==4
        box_coords = self._rect_to_bbox(rect_coords)
        ibb.append(box_coords)
    #

class BBoxFile:  # a collection of ImageBBoxes
    def __init__(self, image_path):
        if image_path.is_dir():
            bb_path = image_path
        else:
            bb_path = image_path.parent
        #
        assert bb_path.is_dir()

        self.pickle_path = bb_path / "rects.pickle"
        print(f"pickle path is {self.pickle_path}")

        # images_d is associative array: {image filename: image stats & list of bounding boxes}
        self.images_d = {}

        try:
            with open(self.pickle_path, "rb") as f:
                self.images_d = pickle.load(f)
        except FileNotFoundError:
            print(f"could not load {self.pickle_path}")
        #

    def __getitem__(self, key):
        return self.images_d[key]

    def __setitem__(self, key, value):
        self.images_d[key] = value


    # def to_rects(self, canvas, image_name):
    #     """
    #     given Tk canvas & image_name, convert 
    #     the image's bounding boxes to rects and add to the canvas
    #     """
    #     if image_name in self.images_d.keys():
    #         #
    #         # copy pickle entry to a list
    #         bbox_l = self.images_d[image_name].bbox_l
    #     else:
    #         print(f"{self.pickle_path} does not contain a preexisting entry for {image_name}")
    #         bbox_l = []
    #     #
    #     rect_l = self._bboxes_to_rects(canvas, bbox_l)
    #     return rect_l

    def _rect_to_bbox(self, rect_coords):
        """
        convert a convas rect to a bounding box tuple
        """
        x = rect_coords[0]
        y = rect_coords[1]
        w = rect_coords[2] - x
        assert w > 0
        h = rect_coords[3] - y
        assert h > 0
        print(f"{rect_coords}")

        bbox = (x, y, w, h)
        return bbox

    # def update_bboxes(self, image_fname, canvas, rect_l):
    #     """
    #     given the image_fname and a list of Tk rects,
    #     convert each rect to a bbox and update the dictionary's
    #     image entry
    #     """
    #     #
    #     # convert list of canvas rects to list of bounding box tuples
    #     bbox_l = []
    #     for rect in rect_l:
    #         rect_coords = canvas.bbox(rect)  # get tuple coord
    #         assert len(rect_coords)==4
    #         box_coords = self._rect_to_bbox(rect_coords)
    #         bbox_l.append(box_coords)
    #     #
    #     self.images_d[image_fname] = bbox_l
    #     return bbox_l

    def save(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.images_d, f)
        

    def _make_json_fname(self):
        out_fname = self.pickle_path.parent / "bounding_boxes.labels"
        return out_fname
        
    def write_ei_json(self):
        json_d = {"version": 1,
                  "type": "bounding-box-labels"}
        bbox_per_file_l = []
        for image_fname in self.image_d.keys():
            imagebbox = self.image_d[image_fname]
            if len(imagebbox.bb_l) <= 0:
                # no bounding boxes for this file, so skip to next
                continue
            else:
                json_bbox_l = [{"label":"knob",
                               "x": bbox[0],
                               "y": bbox[1],
                               "width": bbox[2],
                               "height": bbox[3]} for bbox in imagebbox.bb_l]
                file_bbox_d = {f"{image_fname}": json_bbox_l}
                bbox_per_file_l.append(file_bbox_d)
            #
        #
        json_d['boundingBoxes'] = bbox_per_file_l
        out_fname = self._make_json_fname()
        with open(out_fname, "w") as f:
            json.dump(json_d, f)
        #

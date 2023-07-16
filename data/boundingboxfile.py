from tkinter import Tk, Canvas
import sys
from pathlib import Path
from functools import partial
import json
import pickle



class BBoxFile:
    def __init__(self, image_path):
        assert isinstance(image_path, Path)
        bb_path = image_path.parent
        assert bb_path.is_dir()

        self.pickle_path = bb_path / "rects.pickle"

        #     the pickle contains a dictionary of the form:
        #     {
        #         "file_a.jpg" : [{
        #             "x0" : x0,
        #             "y0" : y0,
        #             "x1" : x1,
        #             "y1" : y1},
        #             ... (more rects)
        #             ],
        #        "file_b.jpg": [
        #             {rect},
        #             {rect}, ...
        #             ]
        #     }
        self.d = {}

        try:
            with open(self.pickle_path, "rb") as f:
                self.d = pickle.load(f)
        except FileNotFoundError:
            print(f"could not load {self.pickle_path}")
        #


    def _bboxes_to_rects(self, canvas, bbox_l):
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

    def to_rects(self, canvas, image_name):
        """
        given Tk canvas & image_name, convert 
        the image's bounding boxes to rects and add to the canvas
        """
        if image_name in self.d:
            #
            # copy pickle entry to a list
            bbox_l = self.d[image_name]
        else:
            print(f"{self.pickle_path} does not contain a preexisting entry for {image_name}")
            bbox_l = []
        #
        rect_l = self._bboxes_to_rects(canvas, bbox_l)
        return rect_l

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

    def update_bboxes(self, image_fname, canvas, rect_l):
        """
        given the image_fname and a list of Tk rects,
        convert each rect to a bbox and update the dictionary's
        image entry
        """
        #
        # convert list of canvas rects to list of bounding box tuples
        bbox_l = []
        for rect in rect_l:
            rect_coords = canvas.bbox(rect)  # get tuple coord
            assert len(rect_coords)==4
            box_coords = self._rect_to_bbox(rect_coords)
            bbox_l.append(box_coords)
        #
        self.d[image_fname] = bbox_l
        return bbox_l

    def save(self):
        with open(self.pickle_path, "wb") as f:
            pickle.dump(self.d, f)
        

    def write_json(self):
        out_fname = self.make_out_fname()
        d = self.convert_rects_to_dict(self)
        with open(out_fname, "w") as f:
            json.dump(d, f)
        #

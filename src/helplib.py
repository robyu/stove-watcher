import cv2


def read_image_rgb(img_fname):
    """
    given image filename, returns
    image sample array (numpy?) in RGB order
    """
    img = cv2.imread(str(img_fname))
    assert img is not None, f"failed to read ({img_fname})"
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    return img_rgb

def write_image(img_fname, img_rgb):
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    cv2.imwrite(str(img_fname), img_bgr)

def compute_crop_params(orig_width, orig_height, cropped_width, cropped_height):
    """
    Given
    OrigImg -> horiz crop -> (square img) -> scale -> CroppedImg

    returns:
    scalef: INVERSE scalefactor applied from OrigImg to CroppedImg
    h_offset: columns to skip in OrigImg to achieve square image
    """
    
    assert cropped_width==cropped_height
    assert orig_width >= orig_height

    # resize.py resized orig image to height=640, width maintains ratio
    scalef = float(orig_height)/cropped_height
    assert scalef > 1.0

    # assume that we cropped the equal-sized "wings" of the resized image in
    # order to make a square image
    # the size of a wing is the horiz offset
    h_offset = int((orig_width - orig_height)/2.0)
    return scalef, h_offset


def adjust_bbox_coords(bb,
                        scalef,
                        h_offset,
                        extra_width,
                        extra_height,
                        orig_width,
                        orig_height,
                        ):
    """
    IN
    bb - bounding box object
    scalef - image scalefactor, see compute_crop_params
    h_offset - horiz offset, see compute_crop_params
    extra_width - extra width to add to bounding box
    extra_height - extra height to add to bounding box
    orig_width - original image width
    orig_height - original image height

    OUT
    x0, y0, x1, y1 - new bounding box coordinates for orig image dimensions

    Note:
    the bounding box will be square, with the side length equal to the
    maximum of the original bounding box width and height
    """
    MARGIN = 5  # margin allows for wiggle room during side-length equalization below
    max_side = max(bb.w, bb. h)
    

    x0 = int(scalef * bb.x + h_offset - extra_width/2.0)
    x0 = max(MARGIN, x0)
    x1 = x0 + int(scalef * max_side) + extra_width
    x1 = min(x1, orig_width-MARGIN)

    y0 = int(scalef * bb.y - extra_height/2.0)
    y0 = max(MARGIN, y0)
    y1 = y0 + int(scalef * max_side) + extra_height
    y1 = min(y1, orig_height-MARGIN)

    #
    # weirdness: iterate until the sides have the same length
    delta_x = x1 - x0
    delta_y = y1 - y0
    while delta_x != delta_y:
        if delta_x > delta_y:
            # increase delta_y
            diff = delta_x - delta_y
            y0 -= int(diff/2.0)
            y1 += diff - int(diff/2.0)
        else:
            # increase delta_x
            diff = delta_y - delta_x
            x0 -= int(diff/2.0)
            x1 += diff - int(diff/2.0)
        #
        delta_x = x1 - x0
        delta_y = y1 - y0
    #
    return x0, y0, x1, y1    
    

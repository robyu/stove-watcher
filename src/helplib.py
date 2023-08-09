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



    

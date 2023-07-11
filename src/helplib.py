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

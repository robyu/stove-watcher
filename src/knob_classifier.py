from edge_impulse_linux.image import ImageImpulseRunner
import argparse
from pathlib import Path
import helplib
import nn_models


class KnobClassifier:
    def __init__(self, model_path):
        self.runner = ImageImpulseRunner(str(model_path))
        model_info = self.runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

    def __del__(self):
        self.runner.stop()

    def _eval_knob_results(self, res):
        conf_off = res['result']['classification']['off']
        conf_on = res['result']['classification']['on']
        #print(f"conf_off: {conf_off:5.3f} | conf_on: {conf_on:5.3f}")

        return conf_on
        
    def classify(self, img_rgb):
        assert img_rgb.shape[0] == img_rgb.shape[1], f"image is not square: {img_rgb.shape}"
        features, img_out = self.runner.get_features_from_image(img_rgb)

        res = self.runner.classify(features)
        conf_on = self._eval_knob_results(res)
        return conf_on
    
    def __del__(self):
        self.runner.stop()

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("image_path", type=Path, help="path to (resized, square) image or image dir")
    parser.add_argument("-m", "--model_path", type=str, default=None, help="path to eim model; default: use nn_models.py to specify model")
    return parser.parse_args()

"""
process squarified knob images and print knob confidence
"""
if __name__=="__main__":
    args  = parse_args()
    assert args.image_path.exists(), f"{args.image_path} does not exist"

    if args.model_path is None:
        model_path = nn_models.get_model_path(nn_models.KNOB_CLASSIFIER)
    else:
        model_path = Path(args.model_path)
    #
    assert model_path.exists(), f"{model_path} does not exist"

    # if image_path is a directory, then create a list of all *.png files in that directory
    # otherwise it's a single file
    if args.image_path.is_dir():
        image_ext = ('.png', '.jpg', '.jpeg')
        image_files_l = [f for f in args.image_path.resolve().iterdir() if f.suffix.lower() in image_ext]
    else:
        image_files_l = [args.image_path]

    if len(image_files_l) == 0:
        print(f"no image files found in {args.image_path}")
        exit(0)


    # load the model
    kc = KnobClassifier(model_path)

    # classify each image
    print(f"{'image name':30s}: {'conf_on':5s}")
    for img_path in image_files_l:
        img_rgb = helplib.read_image_rgb(img_path)
        conf_on = kc.classify(img_rgb)
        print(f"{img_path.name:30s}: {conf_on:5.2f}")
    #



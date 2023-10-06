from edge_impulse_linux.image import ImageImpulseRunner


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
        print(f"conf_off: {conf_off:5.3f} | conf_on: {conf_on:5.3f}")

        return conf_on
        
    def classify(self, img_rgb):
        assert img_rgb.shape[0] == img_rgb.shape[1], f"image is not square: {img_rgb.shape}"
        features, img_out = self.runner.get_features_from_image(img_rgb)

        res = self.runner.classify(features)
        conf_on = self._eval_knob_results(res)
        return conf_on
    
    def __del__(self):
        self.runner.stop()
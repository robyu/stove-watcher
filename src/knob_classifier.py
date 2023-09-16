from edge_impulse_linux.image import ImageImpulseRunner


class KnobClassifier:
    def __init__(self, model_path):
        self.runner = ImageImpulseRunner(str(model_path))
        model_info = self.runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

    def __del__(self):
        self.runner.stop()

    def knob_is_on(self, res, thresh = 0.95):
        off_score = res['result']['classification']['off']
        on_score = res['result']['classification']['on']
        print(f"off_score: {off_score} | on_score: {on_score}")
        assert off_score + on_score > 0.99, f"off_score + on_score = {off_score + on_score} < 0.99"
        if on_score > thresh:
            return True
        else:
            return False

    def is_on(self, img_rgb):
        features, img_out = self.runner.get_features_from_image(img_rgb)
        res = self.runner.classify(features)
        return self.knob_is_on(res)
    
    def __del__(self):
        self.runner.stop()
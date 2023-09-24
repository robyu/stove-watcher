from edge_impulse_linux.image import ImageImpulseRunner
import enum

class KnobClass(enum.Enum):
    ON = enum.auto()
    OFF = enum.auto()
    INDETERMINATE = enum.auto()

class KnobResult:
    def __init__(self, thresh, on_score, off_score):
        self.on_score = on_score
        self.off_score = off_score
        if self.on_score > thresh:
            self.knobclass = KnobClass.ON
        elif self.off_score > thresh:
            self.knobclass = KnobClass.OFF
        else:
            assert self.on_score < thresh and self.off_score < thresh, f"on_score: {self.on_score} | off_score: {self.off_score}"
            self.knobclass = KnobClass.INDETERMINATE
        #
    
class KnobClassifier:
    def __init__(self, model_path, thresh = 0.9):
        self.runner = ImageImpulseRunner(str(model_path))
        model_info = self.runner.init()
        print('Loaded runner for "' + model_info['project']['owner'] + ' / ' + model_info['project']['name'] + '"')

        self.thresh = thresh

    def __del__(self):
        self.runner.stop()

    # def _OLDknob_is_on(self, res):
    #     off_score = res['result']['classification']['off']
    #     on_score = res['result']['classification']['on']
    #     print(f"off_score: {off_score:5.3f} | on_score: {on_score:5.3f}")
    #     assert off_score + on_score > 0.99, f"off_score + on_score = {off_score + on_score} < 0.99"
    #     if on_score > self.thresh:
    #         return True
    #     else:
    #         return False

    def _eval_knob_results(self, res):
        off_score = res['result']['classification']['off']
        on_score = res['result']['classification']['on']
        print(f"off_score: {off_score:5.3f} | on_score: {on_score:5.3f}")

        ret = KnobResult(self.thresh, on_score, off_score)
        return ret
        
    def classify(self, img_rgb):
        assert img_rgb.shape[0] == img_rgb.shape[1], f"image is not square: {img_rgb.shape}"
        features, img_out = self.runner.get_features_from_image(img_rgb)

        res = self.runner.classify(features)
        res_d = self._eval_knob_results(res)
        return res_d
    
    def __del__(self):
        self.runner.stop()
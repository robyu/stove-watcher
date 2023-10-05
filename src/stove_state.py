import sys
sys.path.append('./src')
import datetime as dt
import enum
from mqtt_topics import MqttTopics  
import mqtt_publisher
import numpy as np

class StoveStates(enum.Enum):
     INIT = enum.auto()
     OFF = enum.auto()
     ON = enum.auto()


class StoveState:
    NUM_KNOBS = 7

    def __init__(self, 
                 knob_on_thresh = 0.90,
                 knob_off_thresh = 0.90,
                 now_dt = None
                  ):
        self.curr_state = StoveStates.OFF   # state AFTER the update()
        self.prev_state = StoveStates.INIT # state BEFORE the update()
        self.on_duration_sec = 0    # duration spent in on state
        self.off_duration_sec = 0    # duration spent in off state
        self.knob_on_thresh = knob_on_thresh
        self.knob_off_thresh = knob_off_thresh

        if now_dt==None:
            self.prev_update_dt = dt.datetime.now()
        else:
            self.prev_update_dt = now_dt

    def _eval_inputs(self, knob_on_conf_l):
        # if we haven't located and classified all knobs, then skip this update
        skip_update = None
        if len(knob_on_conf_l) != StoveState.NUM_KNOBS:
            skip_update = True
        else:
            skip_update = False
        assert skip_update != None
        return skip_update


    def update(self, knob_on_conf_l, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        

        #
        # state actions
        self.prev_state = self.curr_state 
        delta_sec = (now_dt - self.prev_update_dt).seconds
        if self.curr_state == StoveStates.OFF:
            self.off_duration_sec += delta_sec
        else:
            assert self.curr_state == StoveStates.ON
            self.on_duration_sec += delta_sec
        #
        self.prev_update_dt = now_dt

        bad_inputs = self._eval_inputs(knob_on_conf_l)
        if bad_inputs:
            #
            # not a valid update, so don't bother evaluating transitions
            return
        
        # use the maximum confidence value 
        # reasoning: if a single knob is on with conf = 1, then the stove is on
        max_on_conf = np.max(knob_on_conf_l)
        assert max_on_conf >= 0.0 and max_on_conf <= 1.0

        # transitions
        next_state = self.curr_state

        #
        if self.curr_state == StoveStates.OFF:
            if max_on_conf >= self.knob_on_thresh:
                self.on_duration_sec = 0
                next_state = StoveStates.ON
            else:
                pass
            #
        else:
            assert self.curr_state == StoveStates.ON
            if (1.0 - max_on_conf) >= self.knob_off_thresh:
                self.off_duration_sec = 0
                next_state = StoveStates.OFF
            else:
                pass
            #
        #


        self.curr_state = next_state


    def get_state(self, now_dt=None):
        """
        return any state information we need for alerts
        """
        d = {'curr_state': self.curr_state,
             'prev_state': self.prev_state,
            'on_duration_sec': self.on_duration_sec,
            'off_duration_sec': self.off_duration_sec,
            }
        return d
    
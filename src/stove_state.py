import sys
sys.path.append('./src')
import datetime as dt
import enum
from mqtt_topics import MqttTopics  
import mqtt_publisher

class StoveStates(enum.Enum):
    OFF = enum.auto()
    ON1 = enum.auto()   # stove just turned out
    ON2 = enum.auto()   # stove has been on for a while



class StoveState:
    DEFAULT_PUBLISH_INTERVAL_SEC = 300
    def __init__(self, 
                 mqtt_pub,
                 publish_interval_sec=DEFAULT_PUBLISH_INTERVAL_SEC  # set default value here
                  ):
        # keep track of whether stove is on or off
        # if on, track for how long
        self.input_flag = False
        self.state = StoveStates.OFF
        self.countdown_sec = 0
        self.publish_interval_sec = publish_interval_sec
        self.last_update_dt = None

        assert type(mqtt_pub) == mqtt_publisher.MqttPublisher
        self.mqtt_pub = mqtt_pub

    def set_state(self, stove_is_on):
        """
        set_state() is a separate function from update() because
        in the main loop, set_state() is only called when the stove's state appears to change,
        whereas update() is called every loop iteration
        """
        self.input_flag = stove_is_on        

    def _do_state_actions(self, now_dt):
        if self.state==StoveStates.OFF:
            pass
        else:
            assert self.state==StoveStates.ON1 or self.state==StoveStates.ON2
            self.countdown_sec -= (now_dt - self.last_update_dt).total_seconds()
        #
        self.last_update_dt = now_dt

    def _do_transitions(self, input_flag):
        next_state = None
        if self.state==StoveStates.OFF:
            if input_flag:
                next_state = StoveStates.ON1
                self.countdown_sec = self.publish_interval_sec
            else:
                next_state = StoveStates.OFF
            #
        elif self.state==StoveStates.ON1:
            if input_flag==False:
                next_state = StoveStates.OFF
            else:
                if self.countdown_sec <= 0:
                    next_state = StoveStates.ON2
                    self.countdown_sec = self.publish_interval_sec
                    self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, 
                                          int(self.publish_interval_sec/60.0))
                else:
                    # no nothing
                    next_state = StoveStates.ON1
                #
            #
        else: # self.state==StoveStates.ON2:
            if input_flag==False:
                next_state = StoveStates.OFF
                self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_OFF, None)
            else:
                if self.countdown_sec <= 0:
                    next_state = StoveStates.ON2
                    self.countdown_sec = self.publish_interval_sec
                    self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, 
                                          int(self.publish_interval_sec/60.0))
                else:
                    # no nothing
                    next_state = StoveStates.ON2
                #
            #
        assert next_state != None
        return next_state
    
    def update(self, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #
        self._do_state_actions(now_dt)

        self.state = self._do_transitions(self.input_flag)

    def get_state(self, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #
        d = {}
        d['is_on'] = self.state==StoveStates.ON1 or self.state==StoveStates.ON2
        if self.state==StoveStates.OFF:
            d['on_countdown_sec'] = 0

        else:
            d['on_countdown_sec'] = self.countdown_sec

        return d
    
    





    

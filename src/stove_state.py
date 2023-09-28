import sys
sys.path.append('./src')
import datetime as dt
import enum
from mqtt_topics import MqttTopics  
import mqtt_publisher

class StoveStates(enum.Enum):
    OFF = enum.auto()
    ON = enum.auto()
    TURNING_OFF = enum.auto()


class StoveState:
    DEFAULT_PUBLISH_INTERVAL_SEC = 300
    def __init__(self, 
                 mqtt_pub,
                 publish_interval_sec=DEFAULT_PUBLISH_INTERVAL_SEC  # set default value here
                  ):
        # keep track of whether stove is on or off
        # if on, track for how long
        self.state = StoveStates.OFF
        self.countdown_sec = 0
        self.publish_interval_sec = publish_interval_sec
        self.next_state = None
        self.last_update_dt = None

        assert type(mqtt_pub) == mqtt_publisher.MqttPublisher
        self.mqtt_pub = mqtt_pub

    def set_state(self, stove_is_on):
        self.next_state = self.state
        if self.state == StoveStates.ON:
            if stove_is_on==False:
                self.next_state = StoveStates.OFF
            else:
                assert stove_is_on==True
                pass
            #
        elif self.state == StoveStates.OFF:
            if stove_is_on == True:
                self.next_state = StoveStates.ON
            else:
                assert stove_is_on==False
                pass
            #
        #       

    def update(self, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #

        if self.next_state != self.state:
            if self.state == StoveStates.OFF:
                if self.next_state == StoveStates.OFF:
                    # it's already off
                    pass
                else:
                    # off -> on
                    assert self.next_state == StoveStates.ON
                    self.countdown_sec = self.publish_interval_sec
                #
            else:
                assert self.state == StoveStates.ON
                if self.next_state == StoveStates.OFF:
                    self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_OFF, None)
                else:
                    assert self.next_state == StoveStates.ON
                    delta_sec = (now_dt - self.last_update_dt).total_seconds()
                    self.countdown_sec -= delta_sec
                    if self.countdown_sec <= 0:
                        #
                        # send notification and reset countdown
                        self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, 
                                             int(self.publish_interval_sec/60.0))
                        self.countdown_sec = StoveState.publish_interval_sec
                    #
                #
            #
            self.state = self.next_state
        else: # next_state == state
            if self.state == StoveStates.OFF:
                pass
            else:
                assert self.state == StoveStates.ON
                delta_sec = (now_dt - self.last_update_dt).total_seconds()
                self.countdown_sec -= delta_sec
                if self.countdown_sec <= 0:
                    #
                    # send notification and reset countdown
                    self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, 
                                            int(self.publish_interval_sec/60.0))
                    self.countdown_sec = self.publish_interval_sec
                #
            #
        #
                
        #
        self.last_update_dt = now_dt


    def get_state(self, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #
        d = {}
        d['is_on'] = self.state==StoveStates.ON
        if self.state==StoveStates.ON:
            d['on_countdown_sec'] = self.countdown_sec
        else:
            d['on_countdown_sec'] = 0

        return d
    
    





    

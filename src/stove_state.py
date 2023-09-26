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
    def __init__(self, mqtt_pub, update_interval_sec):
        # keep track of whether stove is on or off
        # if on, track for how long
        self.state = StoveStates.OFF
        self.state_start_dt = None
        self.update_interval_sec = update_interval_sec

        assert type(mqtt_pub) == mqtt_publisher.MqttPublisher
        self.mqtt_pub = mqtt_pub


    def update(self, stove_is_on, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #

        #
        # state activity
        # if stove is on and duration since self.state_start_dt is a mulitple of 5 minutes, then do_something
        next_state = self.state
        if self.state == StoveStates.ON:
            if stove_is_on==False:
                next_state = StoveStates.OFF
                self.state_start_dt = now_dt
            else:
                assert stove_is_on==True
                pass
            #
        elif self.state == StoveStates.OFF:
            if stove_is_on == True:
                next_state = StoveStates.ON
                self.state_start_dt = now_dt
            else:
                assert stove_is_on==False
                pass
            #
        #
        if next_state != self.state:
            if next_state==StoveStates.OFF:
                self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_OFF, None)
            else:
                assert next_state==StoveStates.ON
                pass
            #
            self.state = next_state
        #

        if self.state==StoveStates.ON:
            on_duration = now_dt - self.state_start_dt
            if abs(on_duration.total_seconds() % 300) <= self.update_interval_sec:
                # publish STOVE_IS_ON with duration in minutes
                self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, 
                                        int(on_duration.total_seconds()/60.0))
            #
        #

    def get_state(self, now_dt=None):
        if now_dt==None:
            now_dt = dt.datetime.now()
        #
        d = {}
        d['is_on'] = self.state==StoveStates.ON
        if self.state==StoveStates.ON:
            d['on_duration'] = now_dt - self.state_start_dt
        else:
            d['on_duration'] = dt.timedelta(0)

        return d
    
    






    # def turn_on(self, now_dt = None):
    #     if self.state ==False:
    #         if now_dt==None:
    #             now_dt = dt.datetime.now()
    #         else:   
    #             assert type(now_dt) == dt.datetime
    #         #
    #         # off -> on
    #         self.is_on = True
    #         self.start_dt = now_dt
    #     else:
    #         # it's already on
    #         pass
    #     #

    # def turn_off(self):
    #     if self.is_on==True:
    #         self.is_on = False
    #         self.start_dt = None
    #     else:
    #         # it's already off
    #         pass
    #     #


    # def get_state(self, now_dt=None):
    #     d = {}
    #     d['is_on'] = self.is_on
    #     if self.is_on:
    #         if now_dt==None:
    #             now_dt = dt.datetime.now()
    #         else:   
    #             assert type(now_dt) == dt.datetime
    #         #
    #         d['on_duration'] = now_dt - self.start_dt
    #     else:
    #         d['on_duration'] = dt.timedelta(0)

    #     return d
    

    





    

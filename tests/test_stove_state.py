import unittest
import datetime as dt
import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import stove_state
from unittest.mock import MagicMock
import mqtt_publisher

class test_stove_state(unittest.TestCase):
    #import pudb; pudb.set_trace()

    def setUp(self):
        mock_client = MagicMock()
        self.mqtt_pub = mqtt_publisher.MqttPublisher('localhost', 1883, test_client=mock_client)        

    def tearDown(self):
        pass

    def test_initial_state(self):
        s = stove_state.StoveState(self.mqtt_pub, 1)
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_duration'] == dt.timedelta(0))


    def test_turn_on(self):
        s = stove_state.StoveState(self.mqtt_pub, 1)
        s.update(True)
        d = s.get_state()
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_duration'] > dt.timedelta(0))

    def test_on_duration(self):
        s = stove_state.StoveState(self.mqtt_pub, 1)
        current_dt = dt.datetime.now()
        s.update(True, current_dt)
        
        new_dt = current_dt + dt.timedelta(minutes=5)
        s.update(True, new_dt)
        d = s.get_state(new_dt)
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_duration'] == dt.timedelta(minutes=5))
        print(d)

    def test_on_off(self):
        # turn it on, turn it off, check the state
        s = stove_state.StoveState(self.mqtt_pub, 1)
        current_dt = dt.datetime.now()
        s.update(True, current_dt)
        s.update(False)
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_duration'] == dt.timedelta(minutes=0))




import unittest
import datetime as dt
import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
from stove_state import StoveState
from unittest.mock import MagicMock
import mqtt_publisher
import mqtt_topics

class test_stove_state(unittest.TestCase):
    import pudb; pudb.set_trace()

    def setUp(self):
        self.mock_client = MagicMock()
        self.mqtt_pub = mqtt_publisher.MqttPublisher('localhost', 1883, test_client=self.mock_client)        

    def tearDown(self):
        pass

    def test_initial_state(self):
        s = StoveState(self.mqtt_pub)
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_countdown_sec'] == 0)


    def test_turn_on(self):
        s = StoveState(self.mqtt_pub)
        s.set_state(True)
        s.update()
        d = s.get_state()
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_countdown_sec'] >= 0)

    def test_on_duration(self):
        import pudb; pudb.set_trace()
        s = StoveState(self.mqtt_pub)
        current_dt = dt.datetime.now()
        s.set_state(True)
        s.update(current_dt)
        
        new_dt = current_dt + dt.timedelta(seconds=StoveState.DEFAULT_PUBLISH_INTERVAL_SEC)
        s.update(new_dt)
        d = s.get_state(new_dt)
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_countdown_sec'] == StoveState.DEFAULT_PUBLISH_INTERVAL_SEC)

        # did anything get published?
        # retrieve mock_client publish arguments
        self.mock_client.publish.assert_called_once()
        # retrieve mock_client publish arguments
        args, kwargs = self.mock_client.publish.call_args
        topic = args[0]
        message = args[1]
        self.assertTrue(topic == mqtt_topics.MqttTopics.STOVE_STATUS_ON_DURATION_MIN)
        self.assertTrue(message == StoveState.DEFAULT_PUBLISH_INTERVAL_SEC/60)
        print(message)


    def test_turn_on_off(self):
        s = StoveState(self.mqtt_pub)

        # turn on
        s.set_state(True)
        s.update()
        d = s.get_state()
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_countdown_sec'] >= 0)

        # turn off
        s.set_state(False)
        s.update()
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_countdown_sec'] == 0)

        # check mqtt messages: there should be NO messages
        self.mock_client.publish.assert_not_called()


    def test_turn_on_for_interval(self):
        s = StoveState(self.mqtt_pub)

        # turn on
        s.set_state(True)
        current_dt = dt.datetime.now()  
        s.update(current_dt)
        d = s.get_state()
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_countdown_sec'] >= 0)

        # update after a half interval
        # this update should NOT generate a message
        new_dt = current_dt + dt.timedelta(seconds=StoveState.DEFAULT_PUBLISH_INTERVAL_SEC/2)
        s.update(new_dt)

        # check for no message
        self.mock_client.publish.assert_not_called()

        # update after a full interval
        # this update *should* generate a message
        new_dt += dt.timedelta(seconds=StoveState.DEFAULT_PUBLISH_INTERVAL_SEC)
        s.update(new_dt)
        self.mock_client.publish.assert_called_once()
        args, kwargs = self.mock_client.publish.call_args
        topic = args[0]
        message = args[1]
        self.assertTrue(topic == mqtt_topics.MqttTopics.STOVE_STATUS_ON_DURATION_MIN)
        self.assertTrue(message == StoveState.DEFAULT_PUBLISH_INTERVAL_SEC/60)

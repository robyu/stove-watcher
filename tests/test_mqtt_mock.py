import unittest
from unittest.mock import MagicMock
import sys
sys.path.insert(0, './src')
import mqtt_publisher


class TestMqttPublisher(unittest.TestCase):
    def setUp(self):
        # Set up any necessary objects or configurations
        pass

    def tearDown(self):
        # Clean up after each test case
        pass

    def test_send_message(self):


        # Use the mock library to patch the MQTT client
        with MagicMock() as mock_client:
            # Create an instance of MQTTModule
            publisher = mqtt_publisher.MqttPublisher('localhost', 1883, test_client=mock_client)

            # Specify the expected topic and message
            expected_topic = 'topic'
            expected_message = 'Hello, MQTT!'

            # Call the method that sends the MQTT message
            publisher.publish_message(expected_topic, expected_message)

            # Assert that the MQTT client's publish() method was called with the expected arguments
            mock_client.publish.assert_called_once_with(expected_topic, expected_message)

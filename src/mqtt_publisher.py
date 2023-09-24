import paho.mqtt.client as mqtt   

"""
send "stove is on" alert to mqtt broker

general idea: whenever a message needs to be sent:
1. create a mqtt client
2. connect to broker (specified via the constructor)
3. publish a message to the broker: 
topic = "stove_alert"
message = "stove is on"
4. disconnect from broker

"""
class MqttPublisher:
    def __init__(self, broker_ip, broker_port, test_client=None):
        self.broker_ip = broker_ip
        self.broker_port = broker_port
        self.test_client = test_client

    def publish_message(self, topic, message):
        if self.test_client:
            client = self.test_client
        else:
            client = mqtt.Client()
        #
        client.connect(self.broker_ip, self.broker_port)
        client.publish(topic, message)
        client.disconnect()

"""
initialization:
    read the config JSON file, return a dictionary with config values

main loop:
    every minute
        - check if there are any new files in the directory
        - if there are any new files, process them with the stove classifier
        - if the stove classifier returns a positive result, publish an alert via mqtt_publisher
        - if the stove classifier returns a negative result, do nothing
"""
import sys
sys.path.append('./src')
import config_store
import json
import mqtt_publisher
import os
import stove_classifier
import time
import enum
from  mqtt_topics import MqttTopics
import sys
import dir_mon
import stove_state

class StoveState(enum.Enum): 
    OFF = enum.auto()
    ON = enum.auto()
    TURNING_OFF = enum.auto()

class StoveWatcher:

    def __init__(self, config_fname):
        self.config = config_store.ConfigStore(config_fname)
        self.dirmon = dir_mon.DirMon(self.config.ftp_dir, self.config.holding_dir)
        self.classifier = stove_classifier.StoveClassifier(self.config.locater_model_path,
                                                        self.config.classifier_model_path,
                                                        self.config.reject_path,
                                                        self.config.debug_out_path)
        self.mqtt_pub = mqtt_publisher.MqttPub(self.config.mqtt_host)
        self.stove_state = stove_state.StoveState(self.mqtt_pub, self.config.update_interval_sec)

    def _request_image(self):
        self.mqtt_pub.publish(MqttTopics.IC_CAPTURE_NOW, None)

    def run(self):
        while True:
            time.sleep(self.loop_interval_seconds)
            self._request_image()
            time.sleep(1.0)  # give a bit of time for image to arrive
            img_files_l = self.dirmon.get_new_files()
            for img_file in img_files_l:
                stove_is_on = self.classifier.stove_is_on(img_file)
                self.stove_state.set_state(stove_is_on)
            #
            self.stove_state.update()
        #



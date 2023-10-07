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
import argparse
from pathlib import Path
import helplib

class StoveWatcher:

    def __init__(self, 
                 config_fname, 
                 mqtt_test_client = None, # specify mock mqtt client for testing
                ):      

        self.config = config_store.ConfigStore(Path(config_fname).resolve())
        self.dirmon = dir_mon.DirMon(self.config.ftp_dir, Path(self.config.holding_dir).resolve() )
        self.classifier = stove_classifier.StoveClassifier( Path(self.config.locater_model_path).resolve(),
                                                            Path(self.config.classifier_model_path).resolve(),
                                                            Path(self.config.reject_path).resolve(),
                                                            Path(self.config.debug_out_path).resolve() )
        self.mqtt_pub = mqtt_publisher.MqttPublisher(self.config.mqtt_broker_ip, test_client = mqtt_test_client)
        self.stove_state = stove_state.StoveState(self.mqtt_pub, 
                                                  self.config.alert_interval_sec)
        self.loop_interval_sec = self.config.loop_interval_sec
        self.iter_count = 0

    def _request_image(self):
        self.mqtt_pub.publish(MqttTopics.IC_CAPTURE_NOW, None)

    def _process_img(self, img_file, write_img_flag):
        # read the image
        img_path = self.config.ftp_dir / img_file
        img = helplib.read_image(img_path)

        # knob_on_conf_l is a list of P(knob=on) for each knob
        knob_on_conf_l = self.classifier.classify_image(img, write_img_flag)
        return knob_on_conf_l


    def run(self, 
            max_iter=-1,
            write_img_flag=False):
        loop_flag = True

        while loop_flag:
            time.sleep(self.loop_interval_sec)
            self._request_image()
            res_d = self.dirmon.get_new_files()  # this will block until timeout or a file appears
            img_files_l = res_d['new_files']
            hold_files_l = res_d['hold_files']  

            # if hold_files_l not empty, then print the list of files 
            if hold_files_l:
                print("The following files are in the holding directory:")
                for fname in hold_files_l:
                    print(fname)
                #
            #

            for img_file in img_files_l:
                knob_on_conf_l = self._process_img(img_file, write_img_flag)
                self.stove_state.update(knob_on_conf_l)

                stove_state_d = self.stove_state.get_state()
                #self._send_alerts(latest_state)

                # after processing img_file, delete it
                os.remove(img_file)                
            #

            self.iter_count += 1
            if max_iter > 0 and self.iter_count >= max_iter:
                loop_flag = False
            else:
                if self.iter_count > 999:  # bound max_iter
                    self.iter_count = 0
                #
            #
        #

    def get_state(self):
        """
        returns a dictionary with the stove's state
        keys:
            is_on: True or False
            on_countdown_sec: number of seconds in the on state
        """
        return self.stove_state.get_state()
    

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("config_fname", type=Path, help="path to config file")
    return parser.parse_args()

if __name__=="__main__":
    args = parse_args()
    watcher = StoveWatcher(args.config_fname)
    watcher.run()

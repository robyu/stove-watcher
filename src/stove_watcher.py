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
import nn_models

class StoveWatcher:
    def __init__(self, 
                 config_fname, 
                 mqtt_test_client = None, # specify mock mqtt client for testing
                ):      

        self.config = config_store.ConfigStore(Path(config_fname).resolve())

        # self._init_dir(self.config.ftp_dir)
        # self._init_dir(self.config.holding_dir)
        self.dirmon = dir_mon.DirMon(self.config.ftp_dir, Path(self.config.holding_dir).resolve() )

        # self._init_dir(debug_out_path)
        # self._init_dir(reject_out_path)
        self.classifier = stove_classifier.StoveClassifier( nn_models.get_model_path( nn_models.KNOB_SEGMENTER), 
                                                            nn_models.get_model_path( nn_models.KNOB_CLASSIFIER),
                                                            debug_out_path = Path(self.config.debug_out_path).resolve(),
                                                            reject_out_path = Path(self.config.reject_path).resolve(),
                                                            )
        self.mqtt_pub = mqtt_publisher.MqttPublisher(self.config.mqtt_broker_ip, test_client = mqtt_test_client)
        self.stove_state = stove_state.StoveState()
        self.loop_interval_sec = self.config.loop_interval_sec
        assert self.loop_interval_sec > 0
        self.warn_interval_sec = 60*5
        self.iter_count = 0


    @staticmethod
    def _init_dir(dir_path):
        if dir_path.exists():
            print(f"emptying directory {dir_path}")
            # remove all files in dir_path
            for f in dir_path.glob('*'):
                f.unlink()
        else:
            print(f"creating directory {dir_path}")
            dir_path.mkdir(parents=True, exist_ok=True)
        #

    def _publish_alerts(self, stove_state_d):
        """
        d = {'curr_state': self.curr_state,
        'prev_state': self.prev_state,
        'on_duration_sec': self.on_duration_sec,
        'off_duration_sec': self.off_duration_sec,
        'reject_inputs_flag': self.reject_inputs_flag,
        }
        """
        if stove_state_d['reject_inputs_flag']:
            return

        prev_state = stove_state_d['prev_state']
        curr_state = stove_state_d['curr_state']
        on_duration_sec = stove_state_d['on_duration_sec']
        off_duration_sec = stove_state_d['off_duration_sec']


        # if the prev state is ON and the current state is ON and the on_duration_sec is a multiple of warn_interval_sec,
        # then publish a warning
        if prev_state == stove_state.StoveStates.ON and curr_state == stove_state.StoveStates.ON:
            # publish only when we've been on for warn_interval_sec,
            # and then every warn_interval_sec thereafter
            mod_interval_sec = on_duration_sec % self.warn_interval_sec
            if mod_interval_sec < self.loop_interval_sec and on_duration_sec > self.warn_interval_sec:
                self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_ON_DURATION_MIN, int(on_duration_sec/60))
            #
        elif prev_state == stove_state.StoveStates.ON and curr_state == stove_state.StoveStates.OFF:
            #
            # newly transitioned from ON to OFF
            if off_duration_sec <= self.loop_interval_sec:
                self.mqtt_pub.publish(MqttTopics.STOVE_STATUS_OFF, None)
        

    def run(self, 
            max_iter=-1,
            write_img_flag=False,
            now_dt = None):
        loop_flag = True

        while loop_flag:
            time.sleep(self.loop_interval_sec)
            self.mqtt_pub.publish(MqttTopics.IC_CAPTURE_NOW, None)  
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
                print(f"processing {img_file}")
                knob_on_conf_l = self.classifier.classify_image(img_file)
                self.stove_state.update(knob_on_conf_l,
                                        now_dt = now_dt)

                stove_state_d = self.stove_state.get_state()
                self._publish_alerts(stove_state_d)

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

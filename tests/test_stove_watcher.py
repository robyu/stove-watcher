import unittest
import sys
sys.path.append('./src')
from src.stove_watcher import StoveWatcher
import shutil
from unittest.mock import MagicMock
from src.config_store import ConfigStore
from pathlib import Path
import stove_state
import datetime as dt
from mqtt_topics import MqttTopics

#import pudb; pudb.set_trace()

class TestStoveWatcher(unittest.TestCase):


    CONFIG_FNAME = Path("./tests/in/config.json").resolve()
    STOVE_ON_IMG = Path( "./tests/in/test_stove_classifier/borest1-0000.jpg").resolve()
    STOVE_OFF_IMG = Path("./tests/in/test_stove_classifier/borest1-0023.jpg").resolve()
    STOVE_DARK_IMG = Path("./tests/in/test_stove_classifier/borest1-0044.jpg").resolve()


    @classmethod
    def setUpClass(cls):
        print("setUpClass")
        # execute function before test suite runs

        # read CONFIG_FNAME into a ConfigStore
        config = ConfigStore(cls.CONFIG_FNAME)

        reject_path = Path(config.reject_path).resolve()
        StoveWatcher._init_dir(reject_path)

        debug_out_path = Path(config.debug_out_path).resolve()
        StoveWatcher._init_dir(debug_out_path)

        ftp_path = Path(config.ftp_dir).resolve()
        StoveWatcher._init_dir(ftp_path)

        holding_path = Path(config.holding_dir).resolve()
        StoveWatcher._init_dir(holding_path)

    def setUp(self):
        self.config = ConfigStore(TestStoveWatcher.CONFIG_FNAME)

    def tearDown(self):
        # delete all files in the ftp directory
        for f in Path(self.config.ftp_dir).glob('*'):
            f.unlink()  

    def test_smoke(self):

        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME)
        self.assertTrue(True)

    def test_stove_is_on(self):
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.STOVE_ON_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        # return dictionary has keys:
        #  {'curr_state': self.curr_state,
        #      'prev_state': self.prev_state,
        #     'on_duration_sec': self.on_duration_sec,
        #     'off_duration_sec': self.off_duration_sec,
        #     }
        self.assertTrue(ret_d['reject_inputs_flag'] == False)
        self.assertTrue(ret_d['prev_state'] == stove_state.StoveStates.OFF)
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.ON)

    def test_stove_is_off(self):
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.STOVE_OFF_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        # return dictionary has keys:
        #  {'curr_state': self.curr_state,
        #      'prev_state': self.prev_state,
        #     'on_duration_sec': self.on_duration_sec,
        #     'off_duration_sec': self.off_duration_sec,
        #     }
        self.assertTrue(ret_d['reject_inputs_flag'] == False)
        self.assertTrue(ret_d['prev_state'] == stove_state.StoveStates.OFF)
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.OFF)

    
    def test_stove_is_dark(self):

        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.STOVE_DARK_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        # return dictionary has keys:
        #  {'curr_state': self.curr_state,
        #      'prev_state': self.prev_state,
        #     'on_duration_sec': self.on_duration_sec,
        #     'off_duration_sec': self.off_duration_sec,
        #     }
        self.assertTrue(ret_d['reject_inputs_flag'] == True)
        self.assertTrue(ret_d['prev_state'] == stove_state.StoveStates.OFF)
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.OFF)

    def test_publish_transition_on(self):
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)    

        # stove goes on
        now_dt = dt.datetime.now()
        shutil.copy(TestStoveWatcher.STOVE_ON_IMG, watcher.config.ftp_dir)
        watcher.run(max_iter=1, 
                    now_dt=now_dt)
        ret_d = watcher.get_state()

        # it's on
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.ON)       
        # "capture image" request got published
        # 1 item got published?
        self.assertTrue(mock_client.publish.call_count == 1)
        pub_l = mock_client.publish.call_args
        topic, arg = pub_l[0]
        self.assertTrue(topic == MqttTopics.IC_CAPTURE_NOW)
        mock_client.reset_mock()

        # 10 minutes later, it's still on
        delta_sec = (2 * watcher.warn_interval_sec) + 1
        self.assertTrue(delta_sec % watcher.warn_interval_sec < watcher.loop_interval_sec)
        now_dt = now_dt + dt.timedelta(seconds=delta_sec)
        shutil.copy(TestStoveWatcher.STOVE_ON_IMG, watcher.config.ftp_dir)
        watcher.run(max_iter=1, 
                    now_dt=now_dt)
        ret_d = watcher.get_state()
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.ON)       
        # 2 items got published:
        # 1. "get image now"
        # 2. "stove is on"
        self.assertTrue(mock_client.publish.call_count == 2)
        # examine what got published
        published = mock_client.publish.call_args_list
        self.assertTrue(published[0][0][0] == MqttTopics.IC_CAPTURE_NOW)
        self.assertTrue(published[1][0][0] == MqttTopics.STOVE_STATUS_ON_DURATION_MIN)
        self.assertTrue(published[1][0][1] == 2 * watcher.warn_interval_sec/60)


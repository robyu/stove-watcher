import unittest
import sys
sys.path.append('./src')
from src.stove_watcher import StoveWatcher
import shutil
from unittest.mock import MagicMock
from src.config_store import ConfigStore
from pathlib import Path
import stove_state

class TestStoveWatcher(unittest.TestCase):

STOP - GET STOVE CLASSIFIER WORKING FIRST
    CONFIG_FNAME = Path("./tests/in/config.json").resolve()
    ON_STOVE_IMG = Path( "./tests/in/test_stove_classifier/borest1-0000.jpg").resolve()
    OFF_STOVE_IMG = Path("./tests/in/test_stove_classifier/borest1-0019.jpg").resolve()
    DARK_IMG =      Path("./tests/in/test_stove_classifier/borest1-0044.jpg").resolve()

    @classmethod
    def setUpClass(cls):
        print("setUpClass")
        # execute function before test suite runs

        # read CONFIG_FNAME into a ConfigStore
        # and create REJECT and DEBUG directories in ./tests/out 
        config = ConfigStore(cls.CONFIG_FNAME)

        reject_path = Path(config.reject_path).resolve()
        if not reject_path.exists():
            reject_path.mkdir(parents=True, exist_ok=True)
        else:
            # remove all files in reject_path
            for f in reject_path.glob('*'):
                f.unlink()

        debug_out_path = Path(config.debug_out_path).resolve()
        if not debug_out_path.exists():
            debug_out_path.mkdir(parents=True, exist_ok=True)
        else:
            # remove all files in debug_out_path
            for f in debug_out_path.glob('*'):
                f.unlink()

        ftp_path = Path(config.ftp_dir).resolve()
        if not ftp_path.exists():
            ftp_path.mkdir(parents=True, exist_ok=True)
        else:
            # remove all files in ftp_path
            for f in ftp_path.glob('*'):
                f.unlink()


        holding_path = Path(config.holding_dir).resolve()
        if not holding_path.exists():
            holding_path.mkdir(parents=True, exist_ok=True)



    def setUp(self):
        self.config = ConfigStore(TestStoveWatcher.CONFIG_FNAME)

    def tearDown(self):
        # delete all files in the ftp directory
        for f in Path(self.config.ftp_dir).glob('*'):
            f.unlink()  

    def test_smoke(self):

        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME)
        self.assertTrue(True)

    def test_classify_stove_as_on(self):
        import pudb;pudb.set_trace()
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.ON_STOVE_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        # return dictionary has keys:
        #  {'curr_state': self.curr_state,
        #      'prev_state': self.prev_state,
        #     'on_duration_sec': self.on_duration_sec,
        #     'off_duration_sec': self.off_duration_sec,
        #     }
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.ON)

    def Xtest_classify_stove_as_off(self):
        import pudb;pudb.set_trace()
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.OFF_STOVE_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        # return dictionary has keys:
        #  {'curr_state': self.curr_state,
        #      'prev_state': self.prev_state,
        #     'on_duration_sec': self.on_duration_sec,
        #     'off_duration_sec': self.off_duration_sec,
        #     }
        self.assertTrue(ret_d['curr_state'] == stove_state.StoveStates.ON)

    

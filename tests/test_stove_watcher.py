import unittest
from src.stove_watcher import StoveWatcher
import shutil
from unittest.mock import MagicMock
from src.config_store import ConfigStore
from pathlib import Path

class TestStoveWatcher(unittest.TestCase):

    CONFIG_FNAME = "./tests/in/config.json"    
    ON_STOVE_IMG = "./tests/in/out-renamed/general/general-0026.jpg"
    OFF_STOVE_IMG = "./tests/in/out-renamed/general/general-0004.jpg"

    def setUp(self):
        self.config = ConfigStore(Path(TestStoveWatcher.CONFIG_FNAME).resolve())

    def tearDown(self):
        # delete all files in the ftp directory
        for f in Path(self.config.ftp_dir).glob('*'):
            f.unlink()  


    def test_smoke(self):
        # import pudb;pudb.set_trace
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME)
        self.assertTrue(True)

    # def test_identify_stove_as_on(self):
    #     mock_client = MagicMock()
    #     watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
    #                            mqtt_test_client=mock_client)

    #     # copy ON_STOVE_IMG to the ftp directory
    #     shutil.copy(TestStoveWatcher.ON_STOVE_IMG, watcher.config.ftp_dir)

    #     watcher.run(max_iter=1, write_img_flag=True)
    #     ret_d = watcher.get_state()

    #     self.assertTrue(ret_d['is_on'] == True)
    #     self.assertTrue(ret_d['on_countdown_sec'] >= 0)

    def test_identify_stove_as_off(self):
        mock_client = MagicMock()
        watcher = StoveWatcher(TestStoveWatcher.CONFIG_FNAME,
                               mqtt_test_client=mock_client)

        # copy ON_STOVE_IMG to the ftp directory
        shutil.copy(TestStoveWatcher.OFF_STOVE_IMG, watcher.config.ftp_dir)

        watcher.run(max_iter=1, write_img_flag=True)
        ret_d = watcher.get_state()

        self.assertTrue(ret_d['is_on'] == False)

    

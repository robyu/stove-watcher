import unittest
import os
from pathlib import Path
from src.dir_mon import DirMon

class TestDirMon(unittest.TestCase):
    def setUp(self):
        self.ftp_dir = Path('./tests/out/ftp_dir').resolve()
        if not self.ftp_dir.exists():
            self.ftp_dir.mkdir(parents=False, exist_ok=True)
        
        self.holding_dir = Path('./tests/out/holding_dir').resolve()
        if not self.holding_dir.exists():
            self.holding_dir.mkdir(parents=False, exist_ok=True)
        self.dir_mon = DirMon(self.ftp_dir, self.holding_dir, timeout_sec=1)

    def tearDown(self):
        # Remove all files in ftp_dir and holding_dir
        for f in os.listdir(self.ftp_dir):
            os.remove(self.ftp_dir / f)
        for f in os.listdir(self.holding_dir):
            os.remove(self.holding_dir / f)

    def test_get_new_files(self):
        # Create two test files in ftp_dir
        with open(self.ftp_dir / 'test1.png', 'w') as f:
            f.write('test1')
        with open(self.ftp_dir / 'test2.jpg', 'w') as f:
            f.write('test2')

        # Call get_new_files() method
        res_d = self.dir_mon.get_new_files()

        # Check that the returned list contains the two test files
        self.assertListEqual(res_d['new_files'], [Path(self.ftp_dir / 'test1.png'),
                                                  Path(self.ftp_dir / 'test2.jpg')])

    def test_get_new_files_empty(self):
        # Call get_new_files() method when ftp_dir is empty
        res_d = self.dir_mon.get_new_files()

        # Check that the returned list is empty
        self.assertListEqual(res_d['new_files'], [])


    def test_hold_filter(self):
        # Create two test files in ftp_dir
        with open(self.ftp_dir / 'test1.png', 'w') as f:
            f.write('test1')
        with open(self.ftp_dir / 'hold-test2.png', 'w') as f:
            f.write('test2')

        # Call get_new_files() method
        res_d = self.dir_mon.get_new_files()

        self.assertListEqual(res_d['new_files'], [Path(self.ftp_dir / 'test1.png')])
        self.assertListEqual(res_d['hold_files'], [Path(self.holding_dir / 'hold-test2.png')])

        # Check that the holding_dir contains hold-test2.png
        self.assertTrue((self.holding_dir / 'hold-test2.png').exists())

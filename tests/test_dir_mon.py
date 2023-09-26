import unittest
import os
from pathlib import Path
from src.dir_mon import DirMon

class TestDirMon(unittest.TestCase):
    def setUp(self):
        self.ftp_dir = Path('./tests/in/ftp_dir')
        if not self.ftp_dir.exists():
            self.ftp_dir.mkdir(parents=False, exist_ok=True)
        
        self.holding_dir = Path('./tests/out/holding_dir')
        if not self.holding_dir.exists():
            self.holding_dir.mkdir(parents=False, exist_ok=True)
        self.dir_mon = DirMon(self.ftp_dir, self.holding_dir)

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
        new_files = self.dir_mon.get_new_files()

        # Check that the returned list contains the two test files
        self.assertListEqual(new_files, ['test1.png', 'test2.jpg'])

    def test_get_new_files_empty(self):
        # Call get_new_files() method when ftp_dir is empty
        new_files = self.dir_mon.get_new_files()

        # Check that the returned list is empty
        self.assertListEqual(new_files, [])


    def test_hold_filter(self):
        # Create two test files in ftp_dir
        with open(self.ftp_dir / 'test1.png', 'w') as f:
            f.write('test1')
        with open(self.ftp_dir / 'hold-test2.png', 'w') as f:
            f.write('test2')

        # Call get_new_files() method
        new_files = self.dir_mon.get_new_files()

        # Check that the returned list contains the two test files
        self.assertListEqual(new_files, ['test1.png'])

        # Check that the holding_dir contains hold-test2.png
        self.assertTrue((self.holding_dir / 'hold-test2.png').exists())

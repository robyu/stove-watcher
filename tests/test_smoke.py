import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')

import unittest

class TestSmokeTest(unittest.TestCase):
    def setUp(self):
        print('setup')

    def tearDown(self):
        print('teardown')
        
    def test_smoke(self):
        self.assertTrue(True)
    #

if __name__== "__main__":
    unittest.main()
    

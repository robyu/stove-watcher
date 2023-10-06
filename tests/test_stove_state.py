import unittest
import datetime as dt
import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
from stove_state import StoveState, StoveStates
import numpy as np

class test_stove_state(unittest.TestCase):
    #import pudb; pudb.set_trace()

    def setUp(self):
        pass
    
    def tearDown(self):
        pass

    def test_initial_state(self):
        s = StoveState()
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.OFF)

    def test_turn_on(self):
        s = StoveState()
        conf_on_l = np.array([1 for i in range(StoveState.NUM_KNOBS)])

        now_dt = dt.datetime.now() + dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.ON)
        self.assertTrue(d['prev_state'] == StoveStates.OFF)
        self.assertTrue(d['on_duration_sec'] == 0)
        self.assertTrue(d['off_duration_sec'] >= 10)


    def test_turn_on_off(self):
        s = StoveState()
        conf_on_l = np.array([1 for i in range(StoveState.NUM_KNOBS)])

        now_dt = dt.datetime.now() + dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.ON)
        self.assertTrue(d['prev_state'] == StoveStates.OFF)
        self.assertTrue(d['on_duration_sec'] == 0)  # time spent in ON state
        self.assertTrue(d['off_duration_sec'] >= 10) # time spnet in OFF state

        conf_on_l = 0 * conf_on_l
        now_dt += dt.timedelta(seconds=10)
        d = s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.OFF)
        self.assertTrue(d['prev_state'] == StoveStates.ON)
        self.assertTrue(d['on_duration_sec'] >= 10)
        self.assertTrue(d['off_duration_sec'] == 0)

    def test_update_on_on(self):
        s = StoveState()
        conf_on_l = np.array([1 for i in range(StoveState.NUM_KNOBS)])

        now_dt = dt.datetime.now() + dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.ON)
        self.assertTrue(d['prev_state'] == StoveStates.OFF)
        self.assertTrue(d['on_duration_sec'] == 0)   # time spent in ON state
        self.assertTrue(d['off_duration_sec'] >= 10) # time spnet in OFF state

        now_dt += dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.ON)
        self.assertTrue(d['prev_state'] == StoveStates.ON)
        self.assertTrue(d['on_duration_sec'] >= 10)
        self.assertTrue(d['off_duration_sec'] >= 10)

    def test_dont_transition_with_wrong_number_of_knobs(self):
        s = StoveState()
        conf_on_l = np.array([1 for i in range(StoveState.NUM_KNOBS - 1)])

        now_dt = dt.datetime.now() + dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.OFF)
        self.assertTrue(d['prev_state'] == StoveStates.OFF)
        self.assertTrue(d['on_duration_sec'] == 0)
        self.assertTrue(d['off_duration_sec'] >= 10)

    def test_dont_transition_with_poor_confidence(self):
        s = StoveState()
        conf_on_l = np.array([0.5 for i in range(StoveState.NUM_KNOBS)])

        now_dt = dt.datetime.now() + dt.timedelta(seconds=10)
        s.update(conf_on_l, now_dt)
        d = s.get_state()
        self.assertTrue(d['curr_state'] == StoveStates.OFF)
        self.assertTrue(d['prev_state'] == StoveStates.OFF)
        self.assertTrue(d['on_duration_sec'] == 0)
        self.assertTrue(d['off_duration_sec'] >= 10)
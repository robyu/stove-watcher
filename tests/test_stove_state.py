import unittest
import datetime as dt
import sys
sys.path.insert(0, './tests')
sys.path.insert(0, './src')
import stove_state

class test_stove_state(unittest.TestCase):
    #import pudb; pudb.set_trace()

    def setup():
        pass

    def teardown():
        pass

    def test_initial_state(self):
        s = stove_state.StoveState()
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_duration'] == dt.timedelta(0))


    def test_turn_on(self):
        s = stove_state.StoveState()
        s.turn_on()
        d = s.get_state()
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_duration'] > dt.timedelta(0))

    def test_on_duration(self):

        s = stove_state.StoveState()
        current_dt = dt.datetime.now()
        s.turn_on(current_dt)

        
        new_dt = current_dt + dt.timedelta(minutes=5)
        s.turn_on(new_dt)
        d = s.get_state(new_dt)
        self.assertTrue(d['is_on'] == True)
        self.assertTrue(d['on_duration'] == dt.timedelta(minutes=5))
        print(d)

    def test_on_off(self):
        # turn it on, turn it off, check the state
        s = stove_state.StoveState()
        current_dt = dt.datetime.now()
        s.turn_on(current_dt)
        s.turn_off()
        d = s.get_state()
        self.assertTrue(d['is_on'] == False)
        self.assertTrue(d['on_duration'] == dt.timedelta(minutes=0))




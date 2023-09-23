import datetime as dt

class StoveState:
    def __init__(self):
        # keep track of whether stove is on or off
        # if on, track for how long
        self.is_on = False
        self.start_dt = None

    def turn_on(self, now_dt = None):

        if self.is_on==False:
            if now_dt==None:
                now_dt = dt.datetime.now()
            else:   
                assert type(now_dt) == dt.datetime
            #
            # off -> on
            self.is_on = True
            self.start_dt = now_dt
        else:
            # it's already on
            pass
        #


    def turn_off(self):
        if self.is_on==True:
            self.is_on = False
            self.start_dt = None
        else:
            pass
        #


    def get_state(self, now_dt=None):
        d = {}
        d['is_on'] = self.is_on
        if self.is_on:
            if now_dt==None:
                now_dt = dt.datetime.now()
            else:   
                assert type(now_dt) == dt.datetime
            #
            d['on_duration'] = now_dt - self.start_dt
        else:
            d['on_duration'] = dt.timedelta(0)

        return d
    

    





    
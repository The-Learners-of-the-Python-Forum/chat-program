'''
Tkinter time widgets.

AUTHORS:
v0.2.2+         --> pydsigner
'''

import tkinter2x as tk
from tkinter2x.constants import *
import time
import datetime


class DigitalClock(tk.Label):
    '''
    A digital clock display based on Label().
    
    AUTHORS:
    v0.2.2+         --> pydsigner
    '''
    def __init__(self, master=None, time_format='%H:%M:%S', **kw):
        '''
        @time_format is passed to time.strftime() to obtain the displayed 
        time look. **@kw is passed to the Label() constructor.
        '''
        self.time_format = time_format
        kw['text'] = self.givetime()
        tk.Label.__init__(self, master, **kw)
        self.setdisplay()
    
    def givetime(self):
        try:
            return time.strftime(self.time_format)
        except TypeError:
            return time.strftime('%I:%M:%S %p')
    
    def setdisplay(self):
        self['text'] = self.givetime()
        self.after(100, self.setdisplay)


class BasicChronograph(tk.Label):
    '''
    A basic chronograph widget that must be code controlled.
    
    AUTHORS:
    v0.2.2+         --> pydsigner
    '''
    def __init__(self, master=None, **kw):
        '''
        **@kw is passed to the Label() constructor.
        '''
        kw['text'] = '00:00:00.00'
        tk.Label.__init__(self, master, **kw)
        self.reset()
        self.update()
    
    def start(self):
        if not self.on:
            self.reset()
            self.on = True
    
    def stop(self):
        self.on = False
    
    def switch(self):
        if self.on:
            self.on = False
        else:
            self.on = True
    
    def reset(self):
        self.on = False
        self.starttime = datetime.timedelta(seconds=time.time())
        self['text'] = '00:00:00.00'
        self.time_expired = datetime.timedelta()
    
    def update(self):
        timedif = (datetime.timedelta(seconds=time.time()) - 
                (self.starttime + self.time_expired))
        
        if self.on:
            self.time_expired += timedif
            hrs = str(self.time_expired.days * 24).zfill(2)
            mins = str(self.time_expired.seconds // 60).zfill(2)
            secs = str(self.time_expired.seconds % 60).zfill(2)
            hundrths = str(self.time_expired.microseconds // 10000).zfill(2)
            self['text'] = '%s:%s:%s.%s' % (hrs, mins, secs, hundrths)
        else:
            self.starttime += timedif
        
        self.after(20, self.update)


class Chronograph(tk.Frame):
    '''
    A more advanced chronograph using BasicChronograph(). This one has 
    external controls.
    
    AUTHORS:
    v0.2.2+         --> pydsigner
    '''
    def __init__(self, master=None, **kw):
        '''
        **@kw is passed to the BasicChronograph() constructor.
        '''
        tk.Frame.__init__(self, master)
        
        self.chron = BasicChronograph(self, **kw)
        self.chron.pack(side=TOP)
        
        self.bbar = tk.Frame(self)
        self.bbar.pack(side=BOTTOM)
        
        self.stopstart = tk.Button(self.bbar, text='start', command=self.flip)
        self.reset = tk.Button(self.bbar, text='reset', command=self.reset)
        self.stopstart.pack(side=LEFT)
        self.reset.pack(side=RIGHT)
    
    def flip(self):
        if self.chron.on:
            self.stopstart['text'] = 'start'
        else:
            self.stopstart['text'] = 'stop'
        self.chron.switch()
    
    def reset(self):
        self.chron.reset()
        self.stopstart['text'] = 'start'

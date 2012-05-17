import sys
import getpass

from twisted.internet import reactor, tksupport
import pgpu.tkinter2x as tk
from pgpu.tkinter2x.constants import *
# NOTE: Once we have user listing commands, we can import SList here too.
from pgpu.tk_utils import SConsole

from passive_client import PassiveClient, PassiveFactory
from common import *


class TkInterface(tk.Frame):
    '''
    This class intercepts PassiveClient()s prints for output and provides a 
    standard IRC input.
    '''
    def __init__(self, master, protocol):
        tk.Frame.__init__(self, master)
        
        self.msg_var = tk.StringVar()
        eframe = tk.Frame(self)
        
        e = tk.Entry(eframe, textvariable=self.msg_var)
        e.pack(side=LEFT, expand=True, fill=X)
        
        # Click the button or hit enter, it doesn't matter
        tk.Button(eframe, text='Send', command=self.send_msg).pack(side=RIGHT)
        e.bind('<Return>', self.send_msg)
        
        eframe.pack(side=BOTTOM, expand=True, fill=X)
        
        
        ## TODO: we need the server to send out notifications when users join
        ## before this will do us any good.
        #self.slist = SList(self)
        #self.slist.pack(side = RIGHT, expand = YES, fill = BOTH)
        
        # We build and pack an SConsole(), which can act like a file.
        display = SConsole(self)
        display.pack(side=LEFT)
        # Then we use it as sys.stdout. This allows us to reuse PassiveClient.
        sys.stdout = display
        
        self.protocol = protocol
    
    def send_msg(self, *args):
        # Strip whitespace off the right, but NOT off the left.
        msg = self.msg_var.get().rstrip()
        
        # Don't send empty strings.
        if msg:
            self.protocol.process_command(msg)
        
        # Empty the EntryBox() for the user!
        self.msg_var.set('')


class TkFactory(PassiveFactory):
    def __init__(self, user, pswd, win):
        PassiveFactory.__init__(self, user, pswd)
        # Need to save a reference to the main window for the interface.
        self.win = win
        self.win.protocol('WM_DELETE_WINDOW', self.quit)
    
    def buildProtocol(self, addr):
        '''
        A customized buildProtocol() to build the interface
        '''
        p = PassiveFactory.buildProtocol(self, addr)
        TkInterface(self.win, p).pack()
        return p
    
    def quit(self):
        self.instance.dc()
        self.win.destroy()
        reactor.stop()


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else STD_PORT
    
    user = input('NoobChat username for %s: ' % host)
    pswd = getpass.getpass('NoobChat password for %s: ' % user)
    
    # Install Tkinter onto Twisted
    win = tk.Tk()
    win.title('NoobChat: %s@%s' % (user, host))
    tksupport.install(win)
    
    # Let's go!
    reactor.connectTCP(host, port, TkFactory(user, pswd, win))
    reactor.run()

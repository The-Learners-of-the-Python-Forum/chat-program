import getpass
import sys

from twisted.internet import reactor

from common import Print, input, STD_PORT
from client import ChatClient, ChatClientFactory


class PassiveClient(ChatClient):    
    def handle_msg(self, time, user, what, to=None, **data):
        line = self.form_time(time) + ' '
        if to:
            if user == self.factory.user:
                line += '(aside to %s) ' % to
            else:
                line += '(aside) '
        line += '<%s> %s' % (user, what)
        Print(line)
    
    def handle_describe(self, time, user, what, **data):
        Print('%s * %s %s' % (self.form_time(time), user, what))
    
    def handle_bye(self, time, msg=None, **data):
        t = self.form_time(time)
        if msg:
            Print(t + ' *** Your connection was terminated because ' + msg)
        else:
            Print(t + '*** Your connection was terminated.')
    
    def handle_info(self, time, msg, **data):
        Print(self.form_time(time) + ' *** ' + msg)


class PassiveFactory(ChatClientFactory):
    protocol = PassiveClient


if __name__ == '__main__':
    host = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    port = int(sys.argv[2]) if len(sys.argv) > 2 else STD_PORT
   
    user = input('NoobChat username for %s: ' % host)
    pswd = getpass.getpass('NoobChat password for %s: ' % user)
    
    reactor.connectTCP(host, port, PassiveFactory(user, pswd))
    reactor.run()

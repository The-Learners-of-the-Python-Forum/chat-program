import json

from twisted.protocols.basic import LineReceiver

from pgpu.compatibility import Print, input


STD_PORT = 61514
# This value determines whether or not to print debug messages that should not 
# be displayed during standard operation.
DEBUG = True


class JSONReceiver(LineReceiver):
    def esend(self, obj):
        self.sendLine(json.dumps(obj))
    
    def cmd_send(self, cmd, d={}, **kw):
        m = {'cmd': cmd}
        m.update(kw)
        m.update(d)
        self.esend(m)
    

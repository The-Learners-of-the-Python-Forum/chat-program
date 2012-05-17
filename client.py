import time

from twisted.internet.protocol import ClientFactory

from common import *


class ChatClient(JSONReceiver):
    
    def form_time(self, t):
        return time.strftime('%H:%M:%S', time.localtime(t))
    
    def dc(self):
        '''
        DisConnect.
        '''
        self.transport.loseConnection()
    
    ### Input ######
    
    def lineReceived(self, line):
        try:
            data = json.loads(line)
        except:
            # If we aren't speaking the same language, hang up!
            self.loseConnection()
            return
        
        # Look for a handler
        getattr(self, 'handle_' + data['cmd'].lower(), self.unsupported)(**data)
    
    def unsupported(self, **kw):
        # Aaagh! Unsupported features!!
        pass
    
    ### Handlers ###
    
    def handle_auth(self, **data):
        self.cmd_send('auth', user=self.factory.user, pswd=self.factory.pswd)
    
    ### Output #####
    
    def process_command(self, s):
        '''
        Performs an action based upon text entered by a user. Several IRC-style 
        commands are recognized:
            '/msg {user} {message}' sends {message} as an aside to {user}
            '/me {action}' sends {action} to describe the user's action
            '/easter {key} {ustring}' does something amusing
        '''
        # Because this method is complex, we'll follow the progression with
        #   s = '/msg user hi there'.
        
        # If we don't have a command, just say the string
        if not s.startswith('/'):
            self.send_msg(s)
            return
        
        # Strip off the leading '/':
        # '/msg user hi there' --> 'msg user hi there'
        s = s[1:]
        
        # split the string into parts:
        # 'msg user hi there' --> ['msg', 'user', 'hi', 'there']
        parts = s.split(' ')
        
        # This dictionary is keyed by command name, with the values being 
        # [callable, arg_count] pairs
        com_dict = {
                'msg': [self.send_aside, 2],
                'me': [self.send_describe, 1],
                'easter': [self.send_easter, 2]
                }
        
        # Get either the pair for the command given, or a null command pair
        t = com_dict.get(parts[0].lower(), [lambda a: None, 1])
        
        # Make sure that there are enough parts for the command
        if len(parts) < t[1]:
            # Ignore the command if there aren't enough parts
            return
        
        # This is very complex, but here is what it does:
        # 't[0](*(...))': call <callable> with some unpacked args
        # 'parts[1:t[1]]': get the first <arg_count> - 1 parts after the 
        #   command (['msg', 'user', 'hi', 'there'] --> ['user'])
        # '+': Join the list just formed with the one about to be formed
        # '[...]': Stick something into a list
        # "' '.join(...)": ['1', '2'] --> '1 2'; this reverses the formation of 
        #   parts
        # 'parts[t[1]:]': get all the parts that we didn't get previously
        #   ()['msg', 'user', 'hi', 'there'] --> ['hi', 'there']
        # In all, if our imaginary input above was run through, the equivalent
        #   would be:
        #   self.send_aside(*(parts[1:2] + [' '.join(parts[2:])]))
        #   self.send_aside(*(['user'] + [' '.join(['hi', 'there'])]))
        #   self.send_aside(*(['user'] + ['hi there']))
        #   self.send_aside(*(['user', 'hi there']))
        #   self.send_aside(*['user', 'hi there'])
        #   self.send_aside('user', 'hi there')
        t[0](*(parts[1:t[1]] + [' '.join(parts[t[1]:])]))
    
    def send_msg(self, message, to=None):
        '''
        The standard speech command. Optional {to} argument creates an aside.
        
        Without {to}, will appear to all as something like this:
        
            10:41:32 <jrandomuser> Hey!
        
        With {to}, will appear to {to} as:
        
            10:41:32 (aside) <jrandomuser> Hey!
        
        and to the sender as:
        
            10:41:32 (aside to {to}) <jrandomuser> Hey!
        '''
        d = {'what': message}
        if to is not None:
            d['to'] = to
        self.cmd_send('msg', d)
    
    def send_aside(self, to, message):
        '''
        Wraps send_msg() for process_command() and for a more standard feel.
        '''
        self.send_msg(message, to)
    
    def send_describe(self, action):
        '''
        Send an action done by the user:
        
            10:41:32 * jrandomuser pats himself on the back
        '''
        self.cmd_send('describe', what=action)
    
    def send_easter(self, key, ustring):
        '''
        [Classified] :)
        '''
        self.cmd_send('easter', key=key, ustring=ustring)


class ChatClientFactory(ClientFactory):
    protocol = ChatClient
    def __init__(self, user, pswd):
        self.user = user
        self.pswd = pswd
    
    def buildProtocol(self, addr):
        p = ClientFactory.buildProtocol(self, addr)
        self.instance = p
        return p

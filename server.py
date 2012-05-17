import time
import sys
## We will use bash style regexps for IP banning
#import fnmatch

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from pgpu import iter_utils

from common import *


class Permissions(object):
    '''
    Represents a user's permissions.
    '''
    # Every mode available. See README, paragraph 2 for a description of each.
    all_perms = 'oamtqsb'
    # What each mode allows. Those not here don't allow any special privileges.
    allow = dict(o='amtqsb', a='mtqsb', m='tqm')
    def __init__(self):
        self.perms = {p: False for p in self.all_perms}
        self.modeset = set()
    
    def __getattr__(self, mode):
        return self.perms[mode.lower()]
    
    def __setattr__(self, mode, value):
        m = mode.lower)_
        assert m in self.all_perms, 'No such mode as %s!' % m
        self.perms[m] = bool(value)
    
    def refresh_modeset(self):
        '''
        Refresh the set of modes that we are able to set.
        '''
        # All of the modes that are set on us
        setmodes = (mode for mode in self.perms if self.pers[mode])
        self.modeset.clear()
        for mode in setmodes:
            for m in self.allow.get(mode, ''):
                self.modeset.add(m)
    
    def set_modes(self, modes=[]):
        '''
        Set modes on this permission set. 
        Each mode must be in one of the following formats (where c is replaced 
        with any mode-letter):
            c
            +c
            -c
        The first two formats will set the permission, the last will unset it.
        '''
        for mode in modes:
            if len(mode) == 2 and mode[0] == '-':
                self.perms[mode[1]] = False
            else:
                self.perms[mode[-1]] = True
    
    def read_modes(self, modestring):
        '''
        Filters out the modes in modestring that this permission set cannot 
        apply, and returns them in a list suitable for passing to set_modes().
        '''
        # Because this method is complex, we will run through a sample input.
        # The imaginary permission set has only the +m mode set. The imaginary 
        # modestring is "x+o-m+t#t-t+-+t1", which definitely needs cleanup.
        
        # If we have no permissions, we'll short circuit right here.
        if not self.modeset:
            return []
        # First and hardest, figure out what the modes actually are.
        # We first will remove all chars that aren't useful.
        s = iter_utils.keep_many(modestring, self.all_perms + '+-')
        # At this point we have: "+o-m+tt-t+-+t"
        # Now we'll do a stateful iteration over the string. The main problem 
        # is that we have three scenarios to recognize:
        #   1. Just a mode-letter. (1 char)
        #   2. A plus sign and a mode-letter. (2 chars)
        #   3. A minus sign and a mode-letter. (2 chars)
        modes = []
        mode = ''
        for c in s:
            if c in '+-':
                # If we already have a + or a -, we remove it.
                mode = c
            elif len(mode):
                # If we're here, we already have a + or -, and we're holding a 
                # mode, so now we just add our finished mode to the list,
                modes.append(mode + c)
                # and reset the mode string.
                mode = ''
            else:
                # No + or - yet, we default to +. Then we continue as above.
                modes.append('+' + c)
                mode = ''
        # At this point, we would have this: 
        # ['+o', '-m', '+t', '+t', '-t', '+t']
        # Now to filter out the modes we cannot set...
        modes = [mode for mode in modes if mode[1] in self.modeset]
        # Now we have this: ['+t', '+t', '-t', '+t'] and we're done:
        # set_modes() can handle this easily.
        return modes


class MemDB(object):
    '''
    This is a simple DB which stores its data in memory.
    '''
    def __init__(self):
        # This dict will be composed of usernames keying passwords
        # E.g. self.users['jrandomuser'] = 'insecure_password'
        self.users = {}
        ## This will eventually composed of usernames keying Permissions()s
        #self.modes = {}
        ## This will eventually be populated with the banned IP regexps
        #self.banned_ips = []
    
    def create_user(self, user, pswd):
        self.users[user] = pswd
        ## Create a permission set here
        # self.modes[user] = Permissions()
    
    def delete_user(self, user):
        del self.users[user]
        ## Delete permission set here
        # del self.modes[user]
    
    def authenticate(self, user, pswd):
        '''
        The username and password of the user attempting to authenticate will 
        be passed. Returns a boolean representing the success or failure of 
        authentication. This database will only choke on preexisting users with 
        the wrong password.
        '''
        # If the user doesn't yet exist, we create it.
        if user not in self.users:
            self.make_user(user, pswd)
            return True
        if self.users[user] == pswd:
            return True
        # This else clause is unneccessary (bool(None) is False),
        # but avoids confusion.
        else:
            return False


class ChatHandler(JSONReceiver):
        
    def __init__(self):
        # This will be set to the selected username after authentication
        self.user = None
    
    def esend(self, d):
        d.setdefault('time', time.time())
        JSONReceiver.esend(self, d)
    
    def connectionMade(self):
        self.hostname = self.transport.getHost().host
        # TODO: Add check for banned IPs
        
        # Authentication first!
        self.authed = False
        # TODO: We should, perhaps, add support for anonymous chatting;
        # But that would be a real pain...
        self.cmd_send('auth')
    
    def connectionLost(self, reason):
        # This will be called when the connection is ended, regardless of who 
        # actually ended it.
        try:
            self.factory.users.pop(self.user)
        except KeyError:
            # Perhaps we lost the connection before authentication?
            pass
    
    def lineReceived(self, line):
        # See common.py to change this
        if DEBUG:
            Print(line)
        try:
            data = json.loads(line)
        except:
            # If we aren't speaking the same language, hang up!
            self.disconnect('a malformed line was received.')
            return
        
        # Make sure we received a command!
        if data.get('cmd') is None:
            self.disconnect('client must send a command.')
            return
        cmd = data.pop('cmd').lower()
        
        if self.authed:
            # Look for a handler
            com = getattr(self, 'handle_' + cmd, self.unsupported)
        
        else:
            if cmd != 'auth':
                self.disconnect(
                        'the client must authenticate before using service.')
                return
            
            com = self.do_auth
        
        try:
            com(**data)
        except  TypeError:
            self.cmd_send('info', 
                    msg='The "%s" command was called with the wrong arguments.' 
                        % cmd)
    
    def unsupported(self, cmd, **kw):
        self.cmd_send('info', 
                msg='This server does not support the %s command.' % cmd)
    
    
    key = 'box'[2] + 'you'[0:1] + chr(122) + chr(int('7a', 16)) + chr(11**2)
    
    ### Commands ###
    
    def do_auth(self, user, pswd, **data):
        # In Python 2, these should be unicode
        if not (isinstance(user, basestring) and isinstance(user, basestring)):
            self.disconnect('passwords and usernames must be strings.')
            return
        
        # TODO: Add check for banned users
        
        # ('User1', 'mypass'), ('1111', '2222'), ('1', 'aBba') work;
        # ('jake_', 'mypass'), ('xx1', '#5'), ('', '') do not.
        if not (user.isalnum() and pswd.isalnum()):
            self.disconnect('passwords and usernames must be alphanumeric ' + 
                    'and non-empty.')
            return
        
        if user in self.factory.users:
            self.disconnect('the desired username is already in use.')
            return
        
        if self.factory.db.authenticate(user, pswd):
            self.authed = True
            self.user = user
            self.cmd_send('info', msg='Authentication is complete!')
            self.factory.users[user] = self
        else:
            self.disconnect('authentication failed.')
    
    def disconnect(self, msg=None):
        d = {'msg': msg} if msg else {}
        # Say goodbye,
        self.cmd_send('bye', d)
        # And actually drop the connection.
        self.transport.loseConnection()
    
    # Command handlers
    
    def handle_msg(self, what, to=None):
        d = {'cmd': 'msg', 'user': self.user, 'what': what}
        if to:
            # We won't allow asides to oneself.
            if to != self.user:
                d['to']  = to
                self.factory.esend(d, [to, self.user])
        else:
            self.factory.esend(d)
    
    def handle_easter(self, key, ustring, **kw):
        if key != self.key or kw:
            users = [self.user]
        else:
            users = [u for u in ustring.split(' ') if u in self.factory.users]
        for u in users:
            self.factory.esend(
                    {'cmd': 'info', 'msg': '%s has been eaten by a grue!' % u})
    
    def handle_describe(self, what):
        self.factory.esend({'cmd': 'describe', 'user': self.user, 'what': what})


class ChatServer(Factory):
    # A new instance of this class will be created for every connection
    protocol = ChatHandler
    def __init__(self, db, port):
        self.db = db
        self.users = {}
        Print('Listening on port', port)
    
    def esend(self, obj, targets=None):
        '''
        Send data to many users at once
        '''
        # By default, send message to everyone
        targets = self.users if targets is None else targets
        for u in targets:
            self.users[u].esend(obj)


if __name__ == '__main__':
    # If we are passed a port on the cmdline, use it
    port = int(sys.argv[1]) if len(sys.argv) > 1 else STD_PORT
    # The standard way to listen on a port
    reactor.listenTCP(port, 
            # Here we hardcode use of MemDB.
            ChatServer(MemDB(), port))
    # Fire up the reactor!
    reactor.run()

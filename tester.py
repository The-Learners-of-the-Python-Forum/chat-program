import readline

from client import *
from twisted.internet import reactor

fact = ChatClientFactory('pine', 'lol')

def runner():
    while 1:
        exec raw_input('>>> ')

reactor.callLater(.5, runner)
reactor.connectTCP('localhost', STD_PORT, fact)
reactor.run()

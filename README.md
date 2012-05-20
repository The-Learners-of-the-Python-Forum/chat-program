The Learners of the Python Forum
---

chat-program
===

The Learners of the Python Forum chat-program is a project that has been created to provide
a common interest task for members of the http://www.python-forum.org/ forums.  We aim to create a
multiuser client/server application that will allow users to communicate using various front and back
ends.  The primary goal of the project is for all participants to learn something new and fun using
the Python programming language and various third party packages.


The Python version we will use for development is 2.7.3.  To begin with, some members will be using 
Twisted (http://www.twistedmatrix.com/), an event driven networkign engine.  Others will choose to 
write their own networking code using the included sockets module.


Visit the following link to get involved!
http://www.python-forum.org/pythonforum/viewtopic.php?f=7&t=34372


Tasks
===

General decisions to be made:
---
    How to handle user authentication.
    How to store user information.
    Generic features: Status' (Op, Mod, User, etc)
                      Banning capability (By Username, IP Address, etc)
                      ?? Add More Here ??
    Determine how many and what kinds of back ends (Telnet, SSH, HTTP, etc)
    Determine how many and what kinds of front ends (Telnet, SSH, HTTP, Pygame, Tkinter, etc)
    ?? Add more front/back ends ??
    ?? Add more general decisions to be made ??


server.py - The server backend:
---
    Develop an IO loop that will allow connections from all the various back ends.
    Determine any logging/statistical capabilities
    Determine (per above) authentication, user information handling.
    ??  Add more for server development ??


client.py - The client frontend:
---
    Determine the type of front end:
        Generic Telnet connection
        SSH connection
        Web interface
        Graphical interface (PyGame, Tkinter, etc)
    ?? Add more for client development ??


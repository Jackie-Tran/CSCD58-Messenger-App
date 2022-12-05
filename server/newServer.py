import socket
import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

if __name__ == '__main__':
    server = XMPPServer('', socket.gethostbyname(socket.gethostname()), '')
    server.start()

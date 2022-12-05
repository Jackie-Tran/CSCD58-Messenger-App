import socket
import sys
import os
from clientUI import ClientWindow
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

if __name__ == '__main__':
    # TODO: add cli arg for name, host, port
    client = XMPPClient(sys.argv[1], socket.gethostbyname(
        socket.gethostname()), 'desktop', ClientWindow)
    client.start()

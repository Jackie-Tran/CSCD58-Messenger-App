import socket
import sys
import os
import argparse
from clientUI import ClientWindow
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

DEFAULT_PORT = '8080'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Client application for CSCD58 group chat')
    parser.add_argument("-n", "--name", help="Name of the user")
    parser.add_argument('-s', '--server', help='Location of the server')
    parser.add_argument('-p', '--port', nargs='?', help='Port of the server')
    args = parser.parse_args()
    client = XMPPClient(args.name, socket.gethostbyname(
        socket.gethostname()), 'desktop', args.server, int(args.port if args.port else DEFAULT_PORT), ClientWindow)
    client.start()

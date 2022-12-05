import socket
import sys
import os
import argparse
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

DEFAULT_PORT = '8080'

if __name__ == '__main__':
    # TODO: add cli arg for port number
    parser = argparse.ArgumentParser(
        description='Server application for CSCD58 group chat')
    parser.add_argument('-p', '--port', nargs='?', help='Port of the server')
    args = parser.parse_args()
    server = XMPPServer('', socket.gethostbyname(socket.gethostname()), '', int(
        args.port if args.port else DEFAULT_PORT))
    server.start()

import socket
import sys
import os
import argparse
import ssl
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QListWidget
from threading import Thread
from clientUI import ClientWindow
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

DEFAULT_PORT = '8080'


class XMPPClient(XMPPEntity):
    def __init__(self, local: str, domain: str, resource: str, port: int, tlsEnabled: bool, ClientUI: any) -> None:
        super().__init__(local, domain, resource)
        self.server = domain
        self.port = port
        self.tlsEnabled = tlsEnabled
        self.ClientUI = ClientUI
        self.window: any = None

    def start(self):
        if self.tlsEnabled:
            print('-----Starting Client Application (TLS Enabled)-----')
        else:
            print('-----Starting Client Application-----')

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.tlsEnabled:
            s = ssl.wrap_socket(
                s, keyfile='./device.key', certfile='./device.crt')
        s.connect((self.server, self.port))
        app = QApplication(sys.argv)
        self.window = self.ClientUI(s, self.JID)
        self.window.show()
        recvThread = Thread(target=self.recv, args=(s,))
        try:
            recvThread.start()
        except:
            print('Error: unable to start thread')
            recvThread.join()

        # Setup XMPP
        self.openStream(s, self.JID, self.server)

        # Start the UI
        app.exec()

    def recv(self, s: socket.socket):
        while True:
            if not s or s.fileno() == -1:
                break
            data = s.recv(1024)
            self.parseXML(s, data)
            if not data:
                break

    def openStream(self, sock: socket.socket, fromJID: str, to: str):
        print('opening stream')
        xml = """<?xml version='1.0'?>
        <stream:stream
            from='{fromJID}'
            to='{toJID}'
            version='1.0'
            xml:lang='en'
            xmlns='jabber:client'
            xmlns:stream='http://etherx.jabber.org/streams'>""".format(fromJID=fromJID, toJID=to)
        sock.sendall(xml.encode('utf-8'))

    def closeStream(self, sock: socket.socket):
        xml = "</stream:stream>"
        sock.sendall(xml.encode('utf-8'))

    def handleStreamRequest(self, sock: socket.socket, root: etree._Element):
        print('handle stream response')
        # notify other clients that we are online by sending a presence stanza
        xml = """<presence from='{fromJID}'>
            <status>ONLINE</status>
            </presence>""".format(fromJID=self.JID)
        sock.sendall(xml.encode('utf-8'))
        # update user list
        usersList: QListWidget = self.window.findChild(
            QListWidget, 'usersList')
        usersList.addItem(self.JID + ' (You)')

    def handleStreamClose(self, sock: socket.socket):
        super().handleStreamClose(sock)
        self.closeStream(sock)
        sock.close()

    def handleMessage(self, sock: socket.socket, root: etree._Element):
        print('handle message')
        src = root.attrib['from']
        dest = root.attrib['to']
        body: etree._Element = root.find('body')
        messageText = body.text
        self.window.emitMessageSignal(messageText, src)

    def handlePresence(self, sock: socket.socket, root: etree._Element):
        print('handling presence')
        usersList: QListWidget = self.window.findChild(
            QListWidget, 'usersList')
        user = root.attrib['from']
        print(user)
        statusElement: etree._Element = root.find('status')
        status = statusElement.text
        # update the online users list
        if status == 'ONLINE':
            usersList.addItem(user)
        elif status == 'OFFLINE':
            for u in usersList.findItems(user, Qt.MatchFlag.MatchContains):
                usersList.takeItem(usersList.row(u))
        else:
            print('unexpected status value')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Client application for CSCD58 group chat')
    parser.add_argument("-n", "--name", help="Name of the user")
    parser.add_argument('-s', '--server', help='Location of the server')
    parser.add_argument('-p', '--port', nargs='?', help='Port of the server')
    parser.add_argument('-t', '--tls', action='store_true',
                        help='Run client with TLS')
    args = parser.parse_args()
    client = XMPPClient(args.name, args.server, 'desktop', int(
        args.port if args.port else DEFAULT_PORT), args.tls, ClientWindow)
    client.start()

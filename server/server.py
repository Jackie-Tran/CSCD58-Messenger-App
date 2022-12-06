import socket
import sys
import os
import argparse
import ssl
from threading import Thread
from typing import List
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from xmpp import *  # nopep8

DEFAULT_PORT = '8080'


class XMPPServer(XMPPEntity):
    def __init__(self, local: str, domain: str, resource: str, port, tlsEnabled: bool) -> None:
        super().__init__(local, domain, resource)
        self.port = port
        self.tlsEnabled = tlsEnabled
        self.xmlStreams: List[tuple[str, socket.socket]] = []

    def start(self):
        if self.tlsEnabled:
            print('-----Starting Server Application (TLS Enabled)-----')
        else:
            print('-----Starting Server Application-----')
        # create an INET, STREAMing socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host and a port
        host = socket.gethostbyname(socket.gethostname())
        print('socket open at: ' + host + ':' + str(self.port))
        serverSocket.bind((host, self.port))
        # become a server socket
        serverSocket.listen(5)
        # serverSocket.settimeout(10)

        while True:
            # accept connections from outside
            (clientsocket, address) = serverSocket.accept()
            if clientsocket:
                if self.tlsEnabled:
                    clientsocket = ssl.wrap_socket(
                        clientsocket, server_side=True, keyfile='./rootCA.key', certfile='./rootCA.pem')
                clientThread = Thread(target=self.handleClientSocket,
                                      args=(clientsocket, address, ))
                try:
                    clientThread.start()
                except:
                    print('Error: unable to start client socket thread')
                    clientThread.join()

    def handleClientSocket(self, clientsocket: socket.socket, address: any):
        print('new connection: ', address)
        while True:
            data = clientsocket.recv(1024)
            try:
                self.parseXML(clientsocket, data)
                print(self.xmlStreams)
            except etree.parseEr:
                print('error in xml parse')
            if not data:
                break
        print('Closing connection to client: ', address)
        clientsocket.close()

    def handleStreamRequest(self, sock: socket.socket, root: etree._Element):
        print(root.attrib)
        # check if stream already exists
        if root.attrib['from'] in self.xmlStreams:
            print('connection already exists')
            return
        self.xmlStreams.append((root.attrib['from'], sock))
        senderJID = root.attrib['from']
        print('Created XML stream for ' + root.attrib['from'])
        xml = """<?xml version='1.0'?>
        <stream:stream
            from='{fromJID}'
            id='++TR84Sm6A3hnt3Q065SnAbbk3Y='
            to='{toJID}'
            version='1.0'
            xml:lang='en'
            xmlns='jabber:client'
            xmlns:stream='http://etherx.jabber.org/streams'>""".format(fromJID='localhost', toJID=root.attrib['from'])
        print(xml)
        sock.sendall(xml.encode('utf-8'))

        self.sendUserList(sock)

    def handleMessage(self, sock: socket.socket, root: etree._Element):
        src = root.attrib['from']
        dest = root.attrib['to']
        body: etree._Element = root.find('body')
        messageText = body.text
        # TODO: update message logs so that new clients are up to date
        # send update to rest of the connected clients
        print(messageText)
        self.broadcastMessage(sock, src, messageText)

    def handlePresence(self, sock: socket.socket, root: etree._Element):
        src = root.attrib['from']
        statusElement: etree._Element = root.find('status')
        status = statusElement.text
        # we need to broadcast the new status to the other clients
        self.broadcastPresence(sock, src, status)

    def handleStreamClose(self, sock: socket.socket):
        super().handleStreamClose(sock)
        # client is closing the stream
        self.broadcastPresence(sock, self.getJIDOfSocket(sock), 'OFFLINE')
        for conn in self.xmlStreams:
            if conn[1] == sock:
                self.xmlStreams.remove(conn)
                break
        sock.sendall(b'</stream:stream>')

    def getJIDOfSocket(self, sock: socket.socket):
        for jid, s in self.xmlStreams:
            if sock == s:
                return jid
        return None

    def broadcastMessage(self, sock: socket.socket, sender: str, messageBody: str):
        # broadcast a message to the rest of the connections
        for jid, s in self.xmlStreams:
            if s == sock:
                # we don't want to send the message back to the original sender
                continue
            message = "<message from='{fromJID}' to='{toJID}'><body>{messageBody}</body></message>".format(
                fromJID=sender, toJID=jid, messageBody=messageBody)
            s.sendall(message.encode('utf-8'))

    def broadcastPresence(self, sock: socket.socket, sender: str, status: str):
        # broadcast sender's status to rest of the clients
        for jid, s in self.xmlStreams:
            if s == sock:
                # we don't need to update the sender about its own status
                continue
            xml = "<presence from='{fromJID}'><status>{status}</status></presence>".format(
                fromJID=sender, status=status)
            s.sendall(xml.encode('utf-8'))

    def sendUserList(self, sock: socket.socket):
        print('sending user list')
        for jid, s in self.xmlStreams:
            if s == sock:
                # we don't need to update the sender about its own status
                continue
            xml = "<presence from='{fromJID}'><status>ONLINE</status></presence>".format(
                fromJID=jid)
            print(xml)
            sock.sendall(xml.encode('utf-8'))


if __name__ == '__main__':
    # TODO: add cli arg for port number
    parser = argparse.ArgumentParser(
        description='Server application for CSCD58 group chat')
    parser.add_argument('-p', '--port', nargs='?', help='Port of the server')
    parser.add_argument('-t', '--tls', action='store_true',
                        help='Run server with TLS')
    args = parser.parse_args()
    server = XMPPServer('', socket.gethostbyname(socket.gethostname()), '', int(
        args.port if args.port else DEFAULT_PORT), args.tls)
    server.start()

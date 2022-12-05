import socket
from typing import List
from threading import Thread
from io import StringIO
import re
from lxml import etree


class JID:
    def __init__(self, local: str, domain: str, resource: str):
        self.local = local
        self.domain = domain
        self.resource = resource
        self.bareJID = local + '@' + domain


class XMPPEntity:
    def __init__(self, local: str, domain: str, resource: str) -> None:
        self.local = local
        self.domain = domain
        self.resource = resource
        self.bareJID = local + '@' + domain
        self.JID = local + '@' + domain + '/' + resource

    def removeNameSpace(self, tag: str) -> str:
        tagRegex = re.compile(r'({.*})?(.*)')
        return tagRegex.search(tag).group(2)

    def handleStreamRequest(self, sock: socket.socket, root: etree._Element):
        pass

    def handleMessage(self, sock: socket.socket, root: etree._Element):
        pass

    def handlePresence(self, sock: socket.socket, root: etree._Element):
        pass

    def handleStreamClose(self, sock: socket.socket):
        pass

    def parseXML(self, sock: socket.socket, xml: bytes):
        parser = etree.XMLParser(encoding='utf-8', recover=True)
        newXml = "<root>"+xml.decode('utf-8')+"</root>"
        # only done on the server
        if xml.decode('utf-8') == '</stream:stream>':
            self.handleStreamClose(sock)
            return
        root: etree._ElementTree = etree.parse(StringIO(newXml), parser)
        rootElement: etree._Element = root.getroot()
        children = rootElement.getchildren()

        for child in children:
            if not type(child) is etree._Element:
                continue
            childTag = self.removeNameSpace(child.tag)
            if childTag == 'stream':
                # recieved request or response for an xml stream
                self.handleStreamRequest(sock, child)
                # send users on the server
                # sendUserList(sock)
            elif childTag == 'message':
                # client has sent a message stanza
                self.handleMessage(sock, child)
            elif childTag == 'presence':
                # client is updating their presence
                self.handlePresence(sock, child)


class XMPPServer(XMPPEntity):
    def __init__(self, local: str, domain: str, resource: str, port=8080) -> None:
        super().__init__(local, domain, resource)
        self.port = port
        self.xmlStreams: List[tuple[str, socket.socket]] = []

    def start(self):
        print("-----Starting Server Application-----")
        # create an INET, STREAMing socket
        serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # bind the socket to a public host and a port
        host = socket.gethostbyname(socket.gethostname())
        print('socket open at: ' + host + ':' + str(self.port))
        serverSocket.bind((host, self.port))
        # become a server socket
        serverSocket.listen(5)
        serverSocket.settimeout(10)

        while True:
            # accept connections from outside
            (clientsocket, address) = serverSocket.accept()
            if clientsocket:
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

import socket
from typing import List
from lxml import etree
from io import StringIO
import re
from threading import Thread

xmlStreams: List[tuple[str, socket.socket]] = []
senderJID = ''


def handleStreamRequest(sock: socket.socket, req: etree._Element):
    print(req.attrib)
    # check if stream already exists
    if req.attrib['from'] in xmlStreams:
        print('connection already exists')
        return
    xmlStreams.append((req.attrib['from'], sock))
    senderJID = req.attrib['from']
    print('Created XML stream for ' + req.attrib['from'])
    xml = """<?xml version='1.0'?>
      <stream:stream
          from='{fromJID}'
          id='++TR84Sm6A3hnt3Q065SnAbbk3Y='
          to='{toJID}'
          version='1.0'
          xml:lang='en'
          xmlns='jabber:client'
          xmlns:stream='http://etherx.jabber.org/streams'>""".format(fromJID='localhost', toJID=req.attrib['from'])
    sock.sendall(xml.encode('utf-8'))


def broadcastMessage(sock: socket.socket, sender: str, messageBody: str):
    # broadcast a message to the rest of the connections
    for jid, s in xmlStreams:
        if s == sock:
            # we don't want to send the message back to the original sender
            continue
        message = "<message from='{fromJID}' to='{toJID}'><body>{messageBody}</body></message>".format(
            fromJID=sender, toJID=jid, messageBody=messageBody)
        s.sendall(message.encode('utf-8'))


def broadcastPresence(sock: socket.socket, sender: str, status: str):
    # broadcast sender's status to rest of the clients
    for jid, s in xmlStreams:
        if s == sock:
            # we don't need to update the sender about its own status
            continue
        xml = "<presence from='{fromJID}'><status>{status}</status></presence>".format(
            fromJID=sender, status=status)
        s.sendall(xml.encode('utf-8'))


def handleMessage(sock: socket.socket, root: etree._Element):
    src = root.attrib['from']
    dest = root.attrib['to']
    body: etree._Element = root.find('body')
    messageText = body.text
    # TODO: update message logs so that new clients are up to date
    # send update to rest of the connected clients
    print(messageText)
    broadcastMessage(sock, src, messageText)


def handlePresence(sock: socket.socket, root: etree._Element):
    src = root.attrib['from']
    statusElement: etree._Element = root.find('status')
    status = statusElement.text
    # we need to broadcast the new status to the other clients
    broadcastPresence(sock, src, status)


def removeNameSpace(tag: str) -> str:
    tagRegex = re.compile(r'({.*})?(.*)')
    return tagRegex.search(tag).group(2)


def sendUserList(sock: socket.socket):
    print('sending user list')
    for jid, s in xmlStreams:
        if s == sock:
            # we don't need to update the sender about its own status
            continue
        xml = "<presence from='{fromJID}'><status>ONLINE</status></presence>".format(
            fromJID=jid)
        print(xml)
        sock.sendall(xml.encode('utf-8'))


def getJIDOfSocket(sock: socket.socket):
    for jid, s in xmlStreams:
        if sock == s:
            return jid
    return None


def parseXML(sock: socket.socket, xml: bytes):
    parser = etree.XMLParser(encoding='utf-8', recover=True)
    newXml = "<root>"+xml.decode('utf-8')+"</root>"
    if xml.decode('utf-8') == '</stream:stream>':
        # client is closing the stream
        broadcastPresence(sock, getJIDOfSocket(sock), 'OFFLINE')
        for conn in xmlStreams:
            if conn[1] == sock:
                xmlStreams.remove(conn)
                break
        sock.sendall(b'</stream:stream>')
        return
    root: etree._ElementTree = etree.parse(StringIO(newXml), parser)
    rootElement: etree._Element = root.getroot()
    children = rootElement.getchildren()

    for child in children:
        if not type(child) is etree._Element:
            continue
        childTag = removeNameSpace(child.tag)
        if childTag == 'stream':
            # client is attempting to open a xml stream
            handleStreamRequest(sock, child)
            # send users on the server
            sendUserList(sock)
        elif childTag == 'message':
            # client has sent a message stanza
            handleMessage(sock, child)
        elif childTag == 'presence':
            # client is updating their presence
            handlePresence(sock, child)


def handleClientSocket(clientsocket: socket.socket, address):
    print('New Connection: ', address)
    while True:
        data = clientsocket.recv(1024)
        try:
            parseXML(clientsocket, data)
            print(xmlStreams)
        except etree.parseEr:
            print('error in xml parse')
        if not data:
            break
    print('Closing connection to client: ', address)
    clientsocket.close()


if __name__ == '__main__':
    print("Starting Server Application")

    # create an INET, STREAMing socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host and a port
    print(socket.gethostname())
    serverSocket.bind(('localhost', 8080))
    # become a server socket
    serverSocket.listen(5)
    serverSocket.settimeout(10)

    while True:
        # accept connections from outside
        (clientsocket, address) = serverSocket.accept()
        if clientsocket:
            clientThread = Thread(target=handleClientSocket,
                                  args=(clientsocket, address, ))
            try:
                clientThread.start()
            except:
                print('Error: unable to start client socket thread')
                clientThread.join()

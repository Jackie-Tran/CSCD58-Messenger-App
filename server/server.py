import socket
from lxml import etree
from io import BytesIO
import re
from threading import Thread

xmlStreams = []
senderJID = ''


def handleStreamRequest(sock: socket.socket, req: etree._Element):
    print(req.attrib)
    # check if stream already exists
    if req.attrib['from'] in xmlStreams:
        print('connection already exists')
        return
    xmlStreams.append(req.attrib['from'])
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


def removeNameSpace(tag: str) -> str:
    tagRegex = re.compile(r'\}.*')
    return tagRegex.search(tag).group()[1:]


def parseXML(sock: socket.socket, xml: bytes):
    parser = etree.XMLParser(encoding='utf-8', recover=True)
    print(xml.decode('utf-8'))
    root: etree._ElementTree = etree.parse(BytesIO(xml), parser)
    rootElement: etree._Element = root.getroot()
    rootTag = removeNameSpace(rootElement.tag)

    if rootTag == 'stream':
        # client is attempting to open a xml stream
        handleStreamRequest(sock, rootElement)


def handleClientSocket(clientsocket: socket.socket, address):
    print('New Connection: ', address)
    while True:
        try:
            data = clientsocket.recv(1024)
            try:
                parseXML(clientsocket, data)
            except etree.parseEr:
                print('error in xml parse')
            if not data:
                break
        except:
            # TODO: check what time of error occurs when the client closes its connection
            print('socket error')
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
        break

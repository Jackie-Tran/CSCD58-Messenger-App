import socket
from lxml import etree
import re
from io import BytesIO


class JID:
    def __init__(self, local: str, domain: str, resource: str):
        self.local = local
        self.domain = domain
        self.resource = resource
        self.bareJID = local + '@' + domain


class XMPPEntity:
    def __init__(self, local: str, domain: str, resource: str) -> None:
        self.jid = JID(local, domain, resource)

    def removeNameSpace(self, tag: str) -> str:
        tagRegex = re.compile(r'\}.*')
        return tagRegex.search(tag).group()[1:]

    def handleStreamHeader(self, sock: socket.socket, root: etree._ElementTree):
        pass

    def parseXML(self, sock: socket.socket, xml: bytes):
        parser = etree.XMLParser(encoding='utf-8', recover=True)
        print(xml.decode('utf-8'))
        root: etree._ElementTree = etree.parse(BytesIO(xml), parser)
        rootElement: etree._Element = root.getroot()
        rootTag = self.removeNameSpace(rootElement.tag)

        if rootTag == 'stream':
            self.handleStreamHeader(sock, root)


class XMPPServer(XMPPEntity):
    def __init__(self, local: str, domain: str, resource: str) -> None:
        super().__init__(local, domain, resource)
        self.xmlStreams = []
        self.senderJID = ''

    def handleStreamHeader(self, sock: socket.socket, root: etree._ElementTree):
        super().handleStreamHeader(sock, root)
        rootElement: etree._Element = root.getroot()
        print(rootElement.attrib)
        # check if stream already exists
        if rootElement.attrib['from'] in self.xmlStreams:
            print('connection already exists')
            return
        self.xmlStreams.append(rootElement.attrib['from'])
        self.senderJID = rootElement.attrib['from']
        print('Created XML stream for ' + rootElement.attrib['from'])
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

import socket
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

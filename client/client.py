#!/usr/bin/python

import socket
from PyQt6.QtWidgets import QApplication, QMainWindow
from clientUI import ClientWindow
import sys
from threading import Thread
from lxml import etree
from io import BytesIO
import re

HOST = 'localhost'
PORT = 8080
LOCAL = 'jackie'
RESOURCE = 'desktop'
BARE_JID = LOCAL + '@' + HOST
JID = BARE_JID + '/' + RESOURCE


def openStream(sock: socket.socket, fromJID: str, to: str):
    print('opening stream')
    xml = """<?xml version='1.0'?>
      <stream:stream
          from='{fromJID}'
          to='{toJID}'
          version='1.0'
          xml:lang='en'
          xmlns='jabber:client'
          xmlns:stream='http://etherx.jabber.org/streams'>""".format(fromJID=JID, toJID=HOST)
    sock.sendall(xml.encode('utf-8'))


def closeStream(sock: socket.socket, fromJID: str, to: str):
    xml = "</stream:stream>"


def startGUI(s: socket.socket):
    app = QApplication(sys.argv)
    window: QMainWindow = ClientWindow(s)
    window.show()

    app.exec()


def handleStreamResponse(sock: socket.socket):
    print('xml stream is now open!')


def removeNameSpace(tag: str) -> str:
    tagRegex = re.compile(r'({.*})?(.*)')
    return tagRegex.search(tag).group(2)


def parseXML(sock: socket.socket, xml: bytes):
    parser = etree.XMLParser(encoding='utf-8', recover=True)
    print(xml.decode('utf-8'))
    root: etree._ElementTree = etree.parse(BytesIO(xml), parser)
    rootElement: etree._Element = root.getroot()
    rootTag = removeNameSpace(rootElement.tag)

    if rootTag == 'stream':
        # server has responded to our stream response
        handleStreamResponse(sock)


def recv(s: socket.socket):
    if not s:
        return
    while True:
        try:
            data = s.recv(1024)
            parseXML(s, data)
            if not data:
                break
        except:
            print('socket error in recv thread')
            break
    # do i need to close the socket here?


if __name__ == '__main__':
    print('Starting Client Application')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))

    recvThread = Thread(target=recv, args=(s,))
    try:
        recvThread.start()
    except:
        print('Error: unable to start thread')
        recvThread.join()

    # Setup XMPP
    openStream(s, JID, HOST)
    startGUI(s)
    s.close()

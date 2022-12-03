#!/usr/bin/python

import socket
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget
from clientUI import ClientWindow
import sys
from threading import Thread
from lxml import etree
from io import BytesIO
import re

HOST = 'localhost'
PORT = 8080


def openStream(sock: socket.socket, fromJID: str, to: str):
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


def closeStream(sock: socket.socket, fromJID: str, to: str):
    xml = "</stream:stream>"


def startGUI(s: socket.socket, jid: str):
    app = QApplication(sys.argv)
    window: QMainWindow = ClientWindow(s, jid)
    window.show()

    app.exec()


def handleStreamResponse(sock: socket.socket, window, jid: str):
    # notify other clients that we are online by sending a presence stanza
    xml = """<presence from='{fromJID}'>
        <status>ONLINE</status>
        </presence>""".format(fromJID=jid)
    sock.sendall(xml.encode('utf-8'))
    # update user list
    usersList: QListWidget = window.findChild(QListWidget, 'usersList')
    usersList.addItem(jid + ' (You)')


def handlePresence(sock: socket.socket, root: etree._Element, window: QMainWindow):
    print('handling presence')
    usersList: QListWidget = window.findChild(QListWidget, 'usersList')
    user = root.attrib['from']
    print(user)
    statusElement: etree._Element = root.find('status')
    status = statusElement.text
    # update the online users list
    if status == 'ONLINE':
        usersList.addItem(user)
    elif status == 'OFFLINE':
        pass
    else:
        print('unexpected status value')


def removeNameSpace(tag: str) -> str:
    tagRegex = re.compile(r'({.*})?(.*)')
    return tagRegex.search(tag).group(2)


def parseXML(sock: socket.socket, xml: bytes, window: QMainWindow, jid: str):
    parser = etree.XMLParser(encoding='utf-8', recover=True)
    print(xml.decode('utf-8'))
    root: etree._ElementTree = etree.parse(BytesIO(xml), parser)
    rootElement: etree._Element = root.getroot()
    rootTag = removeNameSpace(rootElement.tag)
    print(rootTag)
    if rootTag == 'stream':
        # server has responded to our stream response
        handleStreamResponse(sock, window, jid)
    elif rootTag == 'message':
        print('got a message')
    elif rootTag == 'presence':
        handlePresence(sock, rootElement, window)


def recv(s: socket.socket, window: QMainWindow, jid: str):
    if not s:
        return
    while True:
        data = s.recv(1024)
        parseXML(s, data, window, jid)
        if not data:
            break
    # do i need to close the socket here?


if __name__ == '__main__':
    print('Starting Client Application')
    if len(sys.argv) < 2:
        print("missing arg")
    LOCAL = sys.argv[1]
    RESOURCE = 'desktop'
    BARE_JID = LOCAL + '@' + HOST
    JID = BARE_JID + '/' + RESOURCE
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    app = QApplication(sys.argv)
    window: QMainWindow = ClientWindow(s, JID)
    window.show()
    recvThread = Thread(target=recv, args=(s, window, JID,))
    try:
        recvThread.start()
    except:
        print('Error: unable to start thread')
        recvThread.join()

    # Setup XMPP
    openStream(s, JID, HOST)

    app.exec()
    # startGUI(s, JID)
    s.close()

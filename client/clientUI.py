import os
import socket
from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import QMainWindow, QPushButton, QPlainTextEdit, QScrollArea, QLabel, QVBoxLayout, QWidget


class ClientWindow(QMainWindow):
    def __init__(self, s: socket.socket, jid: str):
        super().__init__()
        self.sock = s
        pathToUI = os.path.dirname(__file__) + '\client.ui'
        uic.loadUi(pathToUI, self)
        self.sendButton: QPushButton = self.findChild(
            QPushButton, 'sendButton')
        self.sendButton.clicked.connect(lambda: self.onSendButtonClicked(jid))
        self.messageInput: QPlainTextEdit = self.findChild(
            QPlainTextEdit, 'messageInput')
        self.chatArea: QScrollArea = self.findChild(QScrollArea, 'chatArea')
        self.setWindowTitle("CSCD58 Chat Room - " + jid)

    def closeEvent(self, e: QtGui.QCloseEvent) -> None:
        xml = "</stream:stream>"
        self.sock.sendall(xml.encode('utf-8'))
        super().closeEvent(e)

    def onSendButtonClicked(self, jid: str):
        if not self.messageInput.toPlainText():
            return
        text = self.messageInput.toPlainText().strip()
        message = "<message from='{fromJID}' to='{toJID}'><body>{messageBody}</body></message>".format(
            fromJID=jid, toJID='localhost', messageBody=text)
        self.sock.sendall(message.encode('utf8'))
        self.messageInput.setPlainText('')

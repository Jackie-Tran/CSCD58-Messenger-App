import os
import socket
from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import QMainWindow, QPushButton, QPlainTextEdit


class ClientWindow(QMainWindow):
    def __init__(self, s: socket.socket):
        super().__init__()
        self.sock = s
        pathToUI = os.path.dirname(__file__) + '\client.ui'
        uic.loadUi(pathToUI, self)
        self.sendButton: QPushButton = self.findChild(
            QPushButton, 'sendButton')
        self.sendButton.clicked.connect(self.onSendButtonClicked)
        self.messageInput: QPlainTextEdit = self.findChild(
            QPlainTextEdit, 'messageInput')

    def onSendButtonClicked(self):
        if not self.messageInput.toPlainText():
            return
        text = self.messageInput.toPlainText().strip()
        message = "<message from='{fromJID}' to='{toJID}'><body>{messageBody}</body></message>".format(
            fromJID='jackie@localhost/desktop', toJID='localhost', messageBody=text)
        self.sock.sendall(message.encode('utf8'))
        self.messageInput.setPlainText('')

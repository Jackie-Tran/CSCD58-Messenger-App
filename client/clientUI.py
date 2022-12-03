import os
import socket
from PyQt6 import uic
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
        message = self.messageInput.toPlainText().strip()
        self.sock.sendall(message.encode('utf8'))
        self.messageInput.setPlainText('')

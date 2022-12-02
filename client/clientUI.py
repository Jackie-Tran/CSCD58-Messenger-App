import os
from PyQt6 import uic
from PyQt6.QtWidgets import QMainWindow, QPushButton, QPlainTextEdit


class ClientWindow(QMainWindow):
    def __init__(self):
        super().__init__()
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
        print("Sending Message: " + self.messageInput.toPlainText().strip())
        self.messageInput.setPlainText('')

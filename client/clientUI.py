import os
import socket
import typing
from PyQt6 import uic, QtGui, QtWidgets, QtCore
from PyQt6.QtWidgets import QMainWindow, QPushButton, QPlainTextEdit, QScrollArea, QLabel, QVBoxLayout, QWidget


class MessageBubble(QtWidgets.QWidget):
    """
    Custom QtWidget to display a message from a user
    """

    def __init__(self, message: str, sender: str, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        layout = QtWidgets.QVBoxLayout()
        messageText = QLabel()
        messageText.setText(message)
        messageText.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignTop)
        messageText.setStyleSheet('font: 12pt "MS Shell Dlg 2";')
        layout.addWidget(messageText)
        self.setLayout(layout)


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
        self.setWindowTitle("CSCD58 Chat Room - " + jid)
        self.chatArea: QScrollArea = self.findChild(QScrollArea, 'chatArea')
        self.chatAreaContents = self.findChild(QWidget, 'chatAreaContents')
        self.layout = QVBoxLayout()
        print(self.chatAreaContents)
        for i in range(50):
            messageBubble = MessageBubble("hello world {i}".format(i=i), jid)
            self.layout.addWidget(messageBubble)
        self.chatAreaContents.setLayout(self.layout)

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

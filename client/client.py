import socket
from PyQt6.QtWidgets import QApplication, QMainWindow
from clientUI import ClientWindow
import sys

HOST = 'localhost'
PORT = 8080


def startGUI():
    app = QApplication(sys.argv)
    window: QMainWindow = ClientWindow()
    window.show()

    app.exec()


if __name__ == '__main__':
    print('Starting Client Application')
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.sendall(b'Hello Server')
    data = s.recv(1024)
    print(repr(data))

    startGUI()
    s.close()

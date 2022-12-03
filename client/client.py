#!/usr/bin/python

import socket
from PyQt6.QtWidgets import QApplication, QMainWindow
from clientUI import ClientWindow
import sys
from threading import Thread
import time

HOST = 'localhost'
PORT = 8080


def startGUI(s: socket.socket):
    app = QApplication(sys.argv)
    window: QMainWindow = ClientWindow(s)
    window.show()

    app.exec()


def recv(s: socket.socket):
    while True:
        try:
            data = s.recv(1024)
            print(repr(data))
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
        startGUI(s)
    except:
        print('Error: unable to start thread')
        recvThread.join()
    s.close()

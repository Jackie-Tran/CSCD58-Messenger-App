import socket

if __name__ == '__main__':
    print("Starting Server Application")

    # create an INET, STREAMing socket
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket to a public host and a port
    print(socket.gethostname())
    serverSocket.bind(('localhost', 8080))
    # become a server socket
    serverSocket.listen(5)

    while True:
        # accept connections from outside
        (clientsocket, address) = serverSocket.accept()
        if clientsocket:
            print('New Connection: ', address)
            while True:
                try:
                    res = clientsocket.recv(1024)
                    print(repr(res))
                    if not res:
                        break
                    clientsocket.sendall(b'Server response!')
                except:
                    # TODO: check what time of error occurs when the client closes its connection
                    print('socket error')
                    break
            print('Closing connection to client: ', address)
            clientsocket.close()

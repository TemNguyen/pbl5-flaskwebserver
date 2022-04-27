import time
import socket

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 9000  # The port used by the server

soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
soc.connect((HOST, PORT))

while True:
    soc.sendall(b'hello server')
    data = soc.recv(1024)
    print(data)
    if data != b'':
        if ('success' in data.decode('utf-8')):
            print('do something')
        if ('fail' in data.decode('utf-8')):
            print('block something')
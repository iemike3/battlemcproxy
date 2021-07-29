# proxy.py
import os
import sys
import socket
from threading import Thread

def received_from(connection):
    buffer = b''
    connection.settimeout(2)
 
    try:
        recv_len = 1
        while recv_len:
            data = connection.recv(200000)
            buffer += data
            recv_len = len(data)
            if recv_len < 200000:
                break
    except:
        pass
 
    return buffer

def request_handler(buffer):
    return buffer
 
def response_handler(buffer):
    return buffer

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))
 
    if receive_first:
        remote_buffer = received_from(remote_socket)
        #hexdump(remote_buffer)
 
        remote_buffer = response_handler(remote_buffer)
 
        if len(remote_buffer):
            print('[<==] Sending {} bytes to localhost.'.format(len(remote_buffer)))
            client_socket.send(remote_buffer)
 
    while True:
        local_buffer = received_from(client_socket)
        if len(local_buffer):
            print('[==>] Received {} bytes from localhost.'.format(len(local_buffer)))
            #hexdump(local_buffer)
 
            local_buffer = request_handler(local_buffer)
 
            remote_socket.send(local_buffer)
            print('[==>] Sent to remote.')
 
        remote_buffer = received_from(remote_socket)
 
        if len(remote_buffer):
            print('[<==] Received {} bytes from remote.'.format(len(remote_buffer)))
            #hexdump(remote_buffer)
 
            remote_buffer = response_handler(remote_buffer)
            client_socket.send(remote_buffer)
 
            print('[<==] Sent to localhost.')

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
    try:
        server.bind((local_host, local_port))
    except:
        print('[!!] Failed to listen on {}:{}'.format(local_host, local_port))
        print('Check for other listening sockets or correct permissions.')
        sys.exit(0)
 
    print('[*] Listening on {}:{}'.format(local_host, local_port))
    server.listen(5)
 
    while True:
        client_socket, addr = server.accept()
        print(socket.gethostbyaddr(addr[0]))
        print(client_socket.getpeername())
        print('[==>] Received incoming connection from {}:{}'.format(addr[0], addr[1]))
        proxy_thread = Thread(target=proxy_handler,
                        args=[client_socket,remote_host, remote_port, receive_first])
 
        proxy_thread.start()

def main():

    local_host = "0.0.0.0"
    local_port = int(os.environ.get("PORT", 25565))
    print(int(os.environ.get("PORT", 5000)))
 
    remote_host = "nezuu.f5.si"
    remote_port = 25567
 
    receive_first = "True"
 
    if 'True' in receive_first:
        receive_first = True
    else:
        receive_first = False
 
    server_loop(local_host, local_port, remote_host, remote_port, receive_first)
 
if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit()

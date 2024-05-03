import threading
import socket

host = '127.0.0.1'
port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()

clients = []
nicknames = []


def broadcast(message):
    for client in clients:
        client.send(message)


def handle(client):
    while True:
        try:
            message = client.recv(1024)
            if not message:
                break
            broadcast(message)
        except (ConnectionError, ConnectionAbortedError):
            index = clients.index(client)
            clients.remove(client)
            with client:
                client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} has left the room.'.encode('ascii'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client, address = server.accept()
        print(f'Connected with {address}')

        client.send('NICK'.encode('ascii'))
        nickname = client.recv(1024).decode('ascii')
        nicknames.append(nickname)
        clients.append(client)

        if nickname == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != 'keystone':
                client.send('REFUSE'.encode('ascii'))
                client.close()
                continue

        print(f'nickname of the client is {nickname}')
        broadcast(f'{nickname} has joined the room.'.encode('ascii'))
        client.send('Join to the server'.encode('ascii'))

        thread = threading.Thread(target=handle, args=(client,))
        thread.start()


print('Server is listening')
print('Waiting for connections...')

receive()

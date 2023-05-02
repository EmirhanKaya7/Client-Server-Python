import threading
import socket

host = '127.0.0.1'# localhost
port = 55555

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
server.bind((host,port))
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
            broadcast(message)
        except:
            index = clients.index(client)
            clients.remove(client)
            client.close()
            nickname = nicknames[index]
            broadcast(f'{nickname} left the chat!'.encode('ascii'))
            nicknames.remove(nickname)
            break


def receive():
    while True:
        client,address = server.accept()
        print(f"Connected with {str(address)}")

        client.send("NICK".encode("ascii"))
        nickname = client.recv(1024).decode("ascii")
        nicknames.append(nickname)
        clients.append(client)

        print(f"Nick name of the client is {nickname}")
        broadcast(f"{nickname} joined the chat!".encode("ascii"))
        client.send("Connected to the server!".encode("ascii"))

        thread = threading.Thread(target=handle,args=(client,))
        thread.start()
print("Server is listenning...")
receive()

def read_questions(self) -> None:
        """
        Read questions from file
        :return: None
        """
        with open('questions.txt', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in range(0, len(lines), 2):
                self.questions[lines[line].strip()] = int(lines[line + 1].strip())

        file.close()  # close file
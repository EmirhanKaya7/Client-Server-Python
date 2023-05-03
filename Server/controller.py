from typing import Tuple, Dict, List, Union, Any
from socket import socket, AF_INET, SOCK_STREAM, timeout
from json import dumps
from threading import Thread
import random

from msg_box import MessageBox
from NewClient import NewClient


class ServiceController:
    def __init__(self, port: int, layout: Any):
        """
        Initialize the service controller
        :param port: Port to listen
        :param question_count: number of questions to ask
        """
        # set global variables
        self.server: Union[socket, None] = None
        self.port: int = port
        self.layout: Any = layout

        # set players and questions dictionary
        self.clients: Dict[str: NewClient] = {}

        self._is_terminated = False  # set is_terminated to True to terminate the game
        self._is_started = False  # set is_started to True to start the game

    def connect(self) -> None:
        """
        Connect to server
        :return: None
        """
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind(('localhost', self.port))
        self.server.listen(5)
        print('Server is listening')

    def close(self) -> None:
        """
        Close server
        :return: None
        """
        self.server.close()
        print('Server closed')

    def wait_clients(self) -> None:
        """
        Wait for clients to connect
        :param layout: layout of the game
        """

        self.layout.add_log('Waiting for client to connect...')

        # set timeout for server
        self.server.settimeout(1)

        # wait for a client to connect
        try:
            client, address = self.server.accept()
        except timeout:
            pass

        name = client.recv(1024).decode()

        # send message to client if name is empty
        if name == '':
            self.layout.add_log(f'Client {address} connected with empty name')
            client.send('Name cannot be empty'.encode())
            client.close()
            return

        # send message to client if name is already taken
        if name in self.clients:
            self.layout.add_log(f'Client {address} connected with taken name')
            client.send('Name already exists'.encode())
            client.close()
            return

        # add client to players dictionary
        newClient = NewClient(name=name, client=client, address=address)
        self.clients[name] = newClient

        # send message to client
        newClient.send('Connected')

        self.layout.add_log(f'Client {address} connected with name {name}')

        # remove timeout from server
        self.server.settimeout(None)


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


    def send_message_to_clients(self, message: str) -> None:
        """
        Send message to clients in the same time
        :param message: message to send
        :return: None
        """
        # send question to clients
        for clients in self.clients:
            self.clients[clients].send(message)

    def wait_for_answer_from_clients(self) -> None:
        """
        Wait for answer from clients
        :return: None
        """
        # create threads for clients
        threads = []
        for clients in self.clients:
            thread = Thread(target=self.wait_for_answer_from_client, args=(self.clients[clients],))
            thread.start()
            threads.append(thread)

        # wait for threads to finish
        for thread in threads:
            thread.join()

    def wait_for_answer_from_client(self, client: NewClient) -> None:
        """
        Wait for answer from client
        :param player: player object
        :return: None
        """
        # receive answer from client
        message = ''
        client.client.settimeout(1)

        while not self._is_terminated and message == '':
            try:
                message = client.receive()
            except timeout:
                continue
            except:
                client.answer = -1
                return
        if message != '':
            client.answer = int(message)
        client.client.settimeout(None)
        return

    
    def send_results_to_clients(self, answer: int) -> None:
        """
        Send results to clients
        :param answer: correct answer
        :return: None
        """

        # send results to clients
        for clients in self.clients:
            # create result message
            response: Dict[str: Any] = {}

            # set result message for player
            if self.clients[clients].score == 1:
                response["message"] = f'You won this round with {self.clients[clients].answer}.'
            elif self.clients[clients].score > 0:
                response["message"] = f'You tied with {self.clients[clients].answer}.'
            else:
                response["message"] = f'You lost this round with {self.clients[clients].answer}.'

           
            
            # send result message to player
            try:
                self.clients[clients].send(dumps(response))
            except:
                pass

       

    def check_connections(self) -> None:
        """
        Check connections
        :return: None
        """
        # check if server is terminated
        if self._is_terminated:
            return

        # check if players are disconnected
        for clients in self.clients:
            try:
                self.clients[clients].send('')
            except Exception:
                self.layout.add_log(f'Player {clients} with address {self.clients[clients].address} disconnected')
                self.clients[clients].client.close()
                
                

        return None


    
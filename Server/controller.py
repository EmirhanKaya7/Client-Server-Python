from typing import Tuple, Dict, List, Union, Any
from socket import socket, AF_INET, SOCK_STREAM, timeout
from json import dumps
import rsa
from threading import Thread
import random
import re
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

    def accept_clients(self) -> None:
        """
        Wait for clients to connect
        :param layout: layout of the game
        """

        # set timeout for server
        self.server.settimeout(1)

        # wait for clients to connect
        while not self._is_terminated:

            # check if server stop waiting for clients
            try:
                client, address = self.server.accept()
            except timeout:
                continue

            type = client.recv(1024).decode()

            # send message to client if name is empty
            if type == "Enrollment":
                client.send('Connected'.encode())
                newClient = NewClient(name="", client=client, address=address)
                print("next")
                self.enrollment_process(newClient)

                continue

            # send message to client if name is already taken
            if type == "Authentication":
                client.send('Connected'.encode())

                continue

            # add client to players dictionary
            # newClient = NewClient(name=name, client=client, address=address)
            # self.clients[name] = newClient

            # send message to client
            # newClient.send('Connected')

            # self.layout.add_log(f'Client {address} connected with name {name}')

        # remove timeout from server
        self.server.settimeout(None)

    def readkeys(self) ->None:
        """
        Read questions from file
        :return: None
        """
        temp = ""
        with open('server_enc_dec_pub_prv.txt', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in lines:
                temp += line
        self.sign_pub = temp
        file.close()  # close file
        temp = ""
        with open('server_sign_verify_pub_prv', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in lines:
                temp += line
        self.RSA_prv = temp
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

    def enrollment_process(self, client: NewClient) -> None:
        """
        Wait for answer from client
        :param player: player object
        :return: None
        """
        # receive answer from client
        message = None
        client.client.settimeout(1)

        while not self._is_terminated and message == None:
            try:
                message = client.receive_bytes()
            except timeout:
                continue
            except:
                return
        if message != None:
            new_message = rsa.decrypt(message,self.RSA_prv)
            d = message[64:]
            
            res = re.split(":",d.decode())
            password = res[0]
            username = res[1]            
            channel = res[2]
            print(password, username, channel)    
            client.send("get")     

        client.client.settimeout(None)
        return

       

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


    
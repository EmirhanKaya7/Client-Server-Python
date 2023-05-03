import json
from threading import Thread
from tkinter import Tk, Label, Entry, Button, messagebox, Text, Radiobutton, StringVar
from typing import Union, Dict, Any
import hashlib
from controller import ClientController


class ClientInterface:
    def __init__(self):
        self.controller: Union[ClientController, None] = None

        self.root = Tk()
        self.root.title("Ali-Emirhan Client")
        self.root.geometry("800x600")

        self.root.resizable(False, False)
        self.log_count = 1
        self.is_end = False
        self.readkeys()
        self.start_client_layout()

        self.root.mainloop()
        self.connection_thread.join()
        print("Client closed")
        self.enrollment_thread.join()
        self.controller.close()



    def readkeys(self) ->None:
        """
        Read questions from file
        :return: None
        """
        temp = ""
        with open('server_sign_verify_pub.txt', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in lines:
                temp += line
        self.sign_pub = temp
        file.close()  # close file
        temp = ""
        with open('server_enc_dec_pub.txt', 'r') as file:
            # read question and answer from file line by line and add them to questions dictionary
            lines = file.readlines()
            for line in lines:
                temp += line
        self.RSA_pub = temp
        file.close()  # close file



    def start_client_layout(self) -> None:
        """
        Set start client layout
        :return:
        """
        # write welcome message
        welcome_message = Label(self.root, text="Welcome to the Enrollment Client", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.1, anchor="center")

        # get host and port number from user under the welcome message
        host_label = Label(self.root, text="Host Address:", font=("Arial", 12))
        host_label.place(relx=0.25, rely=0.2, anchor="center")

        self.host_entry = Entry(self.root, width=38)
        self.host_entry.insert(0, "localhost")
        self.host_entry.place(relx=0.65, rely=0.2, anchor="center")


        port_number_label = Label(self.root, text="Port Number: ", font=("Arial", 12))
        port_number_label.place(relx=0.25, rely=0.3, anchor="center")

        self.port_number_entry = Entry(self.root, width=38)
        self.port_number_entry.insert(0, "5000")
        self.port_number_entry.place(relx=0.65, rely=0.3, anchor="center")

        self.name_label = Label(self.root, text="Name:", font=("Arial", 12))
        self.name_label.place(relx=0.25, rely=0.4, anchor="e")

        self.name_entry = Entry(self.root, width=38)
        self.name_entry.place(relx=0.65, rely=0.4, anchor="center")

        self.pass_label = Label(self.root, text="Password:", font=("Arial", 12))
        self.pass_label.place(relx=0.23, rely=0.5, anchor="center")

        self.pass_entry = Entry(self.root, width=38)
        self.pass_entry.place(relx=0.65, rely=0.5, anchor="center")
        # create a label for the radio button group
        self.group_label = Label(self.root, text="Choose an option:", font=("Arial", 12))
        self.group_label.place(relx=0.21, rely=0.7, anchor="center")

        # create a variable to store the selected option
        self.selected_option = StringVar()

        # create three radio buttons with the options
        self.option1_button = Radiobutton(self.root, text="Option 1", font=("Arial", 12), variable=self.selected_option, value="option1")
        self.option1_button.place(relx=0.5, rely=0.7, anchor="center")

        self.option2_button = Radiobutton(self.root, text="Option 2", font=("Arial", 12), variable=self.selected_option, value="option2")
        self.option2_button.place(relx=0.65, rely=0.7, anchor="center")

        self.option3_button = Radiobutton(self.root, text="Option 3", font=("Arial", 12), variable=self.selected_option, value="option3")
        self.option3_button.place(relx=0.8, rely=0.7, anchor="center")
        self.selected_option.set("option1")

        

        # start client button
        self.start_client_button = Button(self.root, text="Enrollment", font=("Arial", 12),
                                          command=self.start_client)
        self.start_client_button.place(relx=0.5, rely=0.8, anchor="center")

    def auth_layout(self) -> None:
        """
        Set start client layout
        :return:
        """
        # write welcome message
        welcome_message = Label(self.root, text="Welcome to the Quiz Game Client", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.25, anchor="center")

        # get host and port number from user under the welcome message
        host_label = Label(self.root, text="Host Address:", font=("Arial", 12))
        host_label.place(relx=0.25, rely=0.4, anchor="center")

        self.host_entry = Entry(self.root, width=38)
        self.host_entry.insert(0, "localhost")
        self.host_entry.place(relx=0.65, rely=0.4, anchor="center")


        port_number_label = Label(self.root, text="Port Number: ", font=("Arial", 12))
        port_number_label.place(relx=0.25, rely=0.5, anchor="center")

        self.port_number_entry = Entry(self.root, width=38)
        self.port_number_entry.insert(0, "5000")
        self.port_number_entry.place(relx=0.65, rely=0.5, anchor="center")

        self.name_label = Label(self.root, text="Name:", font=("Arial", 12))
        self.name_label.place(relx=0.25, rely=0.6, anchor="e")

        self.name_entry = Entry(self.root, width=38)
        self.name_entry.place(relx=0.65, rely=0.6, anchor="center")

        # start client button
        self.start_client_button = Button(self.root, text="Start Client", font=("Arial", 12),
                                          command=self.start_client)
        self.start_client_button.place(relx=0.5, rely=0.8, anchor="center")


    def start_client(self):
        """
        Start client after button clicked
        :return:
        """
        # add loading image under the start button
        loading_image = Label(self.root, text="Loading...", font=("Arial", 12))
        loading_image.place(relx=0.5, rely=0.9, anchor="center")

        # lock the start client button
        self.start_client_button.config(state="disabled")

        try:
            # get host and port number from user
            self.host = self.host_entry.get()
            self.port = int(self.port_number_entry.get())
            self.name = self.name_entry.get()
            self.password = self.pass_entry.get()
            self.channel = self.selected_option.get()
            
            # create controller and start client
            self.controller = ClientController(self.host, self.port, self.name,self.password,self.channel)
           
            message = self.controller.connect()
            #burda hata

            # raise error if connection failed
            if message != "Connected":
                messagebox.showerror("Error", message)
                loading_image.destroy()
                self.start_client_button.config(state="normal")
                self.host_entry.delete(0, "end")
                self.port_number_entry.delete(0, "end")
                self.name_entry.delete(0, "end")
                return

        except ValueError:
            # if port number is not integer
            messagebox.showerror("Error", "Port number must be integer")
            loading_image.destroy()
            self.start_client_button.config(state="normal")
            self.host_entry.delete(0, "end")
            self.port_number_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            return

        except Exception as e:
            # if any other error occurred
            messagebox.showerror("Error", e.args[0])
            loading_image.destroy()
            self.start_client_button.config(state="normal")
            self.host_entry.delete(0, "end")
            self.port_number_entry.delete(0, "end")
            self.name_entry.delete(0, "end")
            return

        # remove all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # set client layout
        self.client_layout()

    def client_layout(self):
        # set geometry
        self.root.geometry("750x500")

        # write welcome message
        welcome_message = Label(self.root, text="Enrollment Process", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.15, anchor="center")

        # set rich text box for see logs
        log_label = Label(self.root, text="Process Log:")
        log_label.place(relx=0.375, rely=0.1975, relwidth=0.4)

        self.log = Text(self.root, width=80, height=20)
        self.log.place(relx=0.55, rely=0.25, relwidth=0.4, relheight=0.5)

        self.log.insert('end', f'Scores will be shown after the first question is answered')
        self.log.config(state='disabled')

        # start game
        self.enrollment_thread = Thread(target=self.enrollment)
        self.enrollment_thread.start()

    def enrollment(self):
        """
        Start game
        :return:
        """

        # check server status
        self.connection_thread = Thread(target=self.check_connection)
        self.connection_thread.start()
        
        # start game
        while not self.controller.is_terminated:
            hash_pass = hashlib.sha3_512()
            byte_pass = bytes(self.password, 'utf-8')
            hash_pass.update(byte_pass)
            byte_name = bytes(self.name,'utf-8')
            byte_channel = bytes(self.channel,'utf-8')
            message = hash_pass.digest() + byte_name + byte_channel
            self.controller.send_message_bytes(message)
            
            is_start = self.controller.receive_message()

            if is_start == "get":
                print("Success")
            if is_start == "start":
                # remove waiting message and set question layout
                self.scores.config(state='normal')
                self.scores.delete('1.0', 'end')
                self.scores.insert('end', f'Scores will be shown after the first question is answered')
                self.scores.config(state='disabled')

                self.waiting_message.config(text="")
                self.question_label = Label(self.root)
                self.question_label.place(relx=0.25, rely=0.1975, anchor="center")

                self.answer_entry = Entry(self.root, width=38)
                self.answer_entry.place(relx=0.25, rely=0.25, anchor="center")

                self.answer_button = Button(self.root, text="Answer", command=self.send_answer)
                self.answer_button.place(relx=0.275, rely=0.4, anchor="center")

                self.is_end = False
                question_count = 1

                while not self.is_end:
                    # get question from server
                    question = self.controller.receive_message()

                    # set waiting message
                    self.waiting_message.config(text="")

                    # set question
                    self.question_label.config(text=f'Question {question_count}: {question}')

                    # get message from server
                    message = self.controller.receive_message()
                    if message == "only_one_player":
                        # if there is only one player in the game
                        messagebox.showinfo("Error", "There is only one player in the game. You win")
                        self.question_label.destroy()
                        self.answer_button.destroy()
                        self.answer_entry.destroy()

                        # wait restart message
                        self.wait_restart_message()

                    else:
                        result = json.loads(message)

                        # set scores
                        self.show_results(result)

                        # check if game is end
                        if result['is_end']:
                            self.is_end = True

                            messagebox.showinfo("Game is end", "Game is end")
                            self.question_label.destroy()
                            self.answer_button.destroy()
                            self.answer_entry.destroy()

                            # wait restart message
                            self.wait_restart_message()

                    # increase question count
                    question_count += 1

                    # clear answer entry
                    if not self.is_end:
                        self.answer_entry.delete(0, "end")

    def send_answer(self):
        """
        Send answer to server
        :return:
        """
        answer = self.answer_entry.get()
        self.controller.send_message(answer)

        # set waiting message
        self.waiting_message.config(text="Waiting for other players answer")

    def show_results(self, response: Dict[str, Any]):
        """
        Show scores in rich text box and messagebox
        :param response: response from server

        :return:
        """
        self.scores.config(state='normal')
        self.scores.delete('1.0', 'end')
        for name, score in response['scores'].items():
            self.scores.insert('end', f'{name}: {score} points \n')
        self.scores.config(state='disabled')

        messagebox.showinfo("Result", f"{response['message']} \n Correct answer: {response['answer']}")

    def check_connection(self):
        """
        Check connection with server
        :return:
        """
        while not self.is_end:
            if not self.controller.is_connected:
                messagebox.showerror("Error", "Connection is lost")
                self.is_end = True
                self.waiting_message.config(text="Connection lost")
                self.question_label.destroy()
                self.answer_button.destroy()
                self.answer_entry.destroy()
                return

    
if __name__ == "__main__":
    ClientInterface()

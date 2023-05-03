import time
from tkinter import Tk, Label, Button, Entry, END, messagebox, Text, NORMAL, DISABLED, Frame
from typing import Union
from threading import Thread

from controller import ServiceController
from msg_box import MessageBox


class ServiceInterface:
    def __init__(self):
        self.controller: Union[ServiceController, None] = None

        self.root = Tk()
        self.root.title("Quiz Game Server")
        self.root.geometry("600x400")

        self.root.resizable(False, False)
        self.log_count = 1

        self.start_server_layout()

        self.root.mainloop()
        self.controller._is_terminated = True
        self.connection_thread.join()
        print("Connection thread joined")
        self.game_thread.join()
        print("Game thread joined")
        self.controller.close()
        exit(0)

    def start_server_layout(self) -> None:
        """
        Set start server layout
        :return:
        """
        # write welcome message
        welcome_message = Label(self.root, text="Welcome to the Quiz Game Server", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.25, anchor="center")

        # get port number and question count from user under the welcome message
        port_number_label = Label(self.root, text="Port Number:    ", font=("Arial", 12))
        port_number_label.place(relx=0.25, rely=0.4, anchor="center")

        self.port_number_entry = Entry(self.root, width=38)
        self.port_number_entry.insert(0, "5000")
        self.port_number_entry.place(relx=0.65, rely=0.4, anchor="center")


        
        # start server button
        self.start_server_button = Button(self.root, text="Start Server", font=("Arial", 12),
                                          command=self.start_server)
        self.start_server_button.place(relx=0.5, rely=0.7, anchor="center")

    def start_server(self):
        """
        Start server after button clicked
        :return:
        """
        # add loading image under the start button
        loading_image = Label(self.root, text="Loading...", font=("Arial", 12))
        loading_image.place(relx=0.5, rely=0.8, anchor="center")

        # lock the start server button
        self.start_server_button.config(state="disabled")

        try:
           
            self.port_number = int(self.port_number_entry.get())
            

            # connect server
            self.controller = ServiceController(self.port_number, self)
            self.controller.connect()

        except ValueError:
            messagebox.showerror("Error", "Port Number")
            loading_image.destroy()
            self.start_server_button.config(state="normal")
            self.port_number_entry.delete(0, END)
            
            return

        except Exception as e:
            messagebox.showerror("Error", e.args[0])
            loading_image.destroy()
            self.start_server_button.config(state="normal")
            self.port_number_entry.delete(0, END)
            
            return

        # remove all widgets from the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # set service layout
        self.service_layout()

        # add log
        self.add_log("Server started on port " + str(self.port_number))

        # start game
        self.start_game()

    def service_layout(self):
        """
        Set service layout
        :return:
        """
        # set geometry
        self.root.geometry("750x500")
        # write welcome message
        welcome_message = Label(self.root, text="Quiz Game Server", font=("Arial", 20))
        welcome_message.place(relx=0.5, rely=0.15, anchor="center")

        # set rich text box for see logs
        self.outputs = Text(self.root, width=80, height=20, state=DISABLED)
        self.outputs.place(relx=0.1, rely=0.25, relwidth=0.8, relheight=0.5)

        self.start_game_button = Button(self.root, text="Start Game", font=("Arial", 12),
                                        command=self.start_game)
        self.start_game_button.place(relx=0.5, rely=0.9, anchor="center")



    def start_game(self) -> None:
        """
        Start game
        :return: None
        """

        # start waiting for players
        self.game_thread = Thread(target=self.game)
        self.game_thread.start()

    def game(self):
        """
        Thread for game
        :return: None
        """


        # check connections in thread
        self.connection_thread = Thread(target=self.check_connections)
        self.connection_thread.start()

        while not self.controller._is_terminated:

            self.controller._is_started = False
           

            # activate start game button
            self.start_game_button.config(state="normal")

            # accept clients
            self.controller.accept_clients()
           
        return None

    def check_connections(self):
        """
        Check connections in thread
        :return: None
        """
        while not self.controller._is_terminated:
            if self.controller._is_started:
                self.controller.check_connections()

        return None

    def ask_question(self, question_number: int = 0) -> int:
        """
        Ask question to all players
        :return: answer
        """
        question, answer = self.controller.select_question()
        self.add_log(f'Question {question_number + 1}: {question}, Answer: {answer}')

        # send question to all players
        self.controller.send_message_to_clients(question)
        self.add_log("Question sent to all players")

        return answer

    def get_answers(self, correct_answer: int) -> None:
        """
        Get answers from all players
        :param correct_answer: correct answer of the question
        :return: None
        """
        # get answers from all players
        self.controller.wait_for_answer_from_clients()
        if not self.controller._is_terminated:
            self.add_log("Answers received from all players")

            # compare answers
            self.controller.compare_answers(correct_answer)
            self.add_log("Answers compared")

    def send_results(self, correct_answer: int) -> None:
        """
        Send results to all players
        :param correct_answer: correct answer of the question
        :return: None
        """

        # send results to all players
        if not self.controller._is_terminated:
            self.controller.send_results_to_clients(correct_answer)
            self.add_log("Results sent to all players\n")

    def add_log(self, log: str) -> None:
        """
        Add log to the rich text box
        :param log: log
        :return: None
        """
        self.outputs.config(state=NORMAL)
        self.outputs.insert(END, f'{self.log_count} - {log}\n')
        self.outputs.see(END)
        self.outputs.config(state=DISABLED)

        self.log_count += 1

    def terminate_game(self) -> None:
        """
        Terminate game
        :return: None
        """
        self.controller._is_terminated = True


if __name__ == '__main__':
    interface = ServiceInterface()

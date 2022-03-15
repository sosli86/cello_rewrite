from CelloControl import CelloControl, get_web3
from CelloMod import UserMod
from CelloDB import CelloDB
import time
from os import system, name
import tkinter as tk
from tkinter import ttk
from abc import abstractmethod
from typing import List
from threading import Thread
from web3 import Web3
    
def show_messages(model, c, contract_name, message_box):
    while True:
        messages = model.get_message_archive(contract_name)
        print(messages)
        while c < len(messages):
            print(messages)
            message_box.insert(c, str(c) + ". " + messages[c][0])
            c+=1
            print("yo-1")
        print("yo-2")
        time.sleep(1)
    
def send_message(control, contract_name, text):
    new_message = text.get()
    control.add_new_message(contract_name, new_message)
    text.delete(0, tk.END)

user_name = "test_user"
contract_name_txt = "test_contract"
contract_key = "test_key"

web3 = get_web3()

user_address = web3.eth.accounts[0]

db = CelloDB("cello.db")

model = UserMod(db, web3, user_name, user_address)

# web3 = Web3(Web3.HTTPProvider('http://127.0.0.1:7545'))
# web3.eth.default_account = input("Please enter your account number: ")

control = CelloControl(web3, model, user_name)

control.add_new_contract(contract_name_txt)

view = tk.Tk()
        # Create the chatlog frame.
chatlog_frame = tk.Frame(master=view)
message_box = tk.Listbox(master=chatlog_frame, width=40, height=20, justify="left", bg="white",)
message_box.pack()
chatlog_frame.pack()

        # Create the textentry frame.
textentry_frame = tk.Frame(master=view)
textentry = tk.Entry(master=textentry_frame,width=30)
textentry.pack()
textentry_frame.pack()

        # Create the send message button.
send_button = tk.Button(text="Send Message", master=textentry_frame,width=10,command=lambda: send_message(control, contract_name_txt, textentry))
send_button.pack()

c = 0

db_thread = Thread(target=show_messages,args=(model, c, contract_name_txt, message_box, ))
db_thread.start()

view.mainloop()
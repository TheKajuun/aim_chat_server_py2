#!/usr/bin/env python3
# Script for Tkinter GUI chat client.
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter

def receive():
    # Handles receiving of messages.
    while True:
        try:
            msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(tkinter.END, msg)
        except OSError:  # Possibly client has left the chat.
            break

def send(event=None):  # event is passed by binders.
    # Handles sending of messages.
    msg = my_msg.get()
    my_msg.set("")  # Clears input field.
    try:
        client_socket.send(bytes(msg, "utf8"))
        if msg == "exit":
            client_socket.close()
            top.quit()
    except NameError:
        msg_list.insert(tkinter.END, "You are not connected to the server.")    


def on_closing(event=None):
    # This function is called when the window is closed.
    my_msg.set("exit")
    send()

#----Now comes the sockets part----
HOST = input('Enter host (server IP or default "localhost"): ')
PORT = input('Enter port (must match the open port, integer only, and between 1025 and 65535): ')
if not HOST:
    HOST = "localhost"  # Default value if blank

if not PORT:
    PORT = 33000 # Default value
if int(PORT) < 1025 or int(PORT) > 65535:
    print("Port must be between 1025 and 65535, setting default arbitrarily to 33000.")
    PORT = 33000 # Default value, probably should re-prompt, but busy with other things
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)

try:
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect(ADDR)
    print(f"Connected to server at {ADDR}.")
except Exception as e:
    print(f"Error: Unable to connect to the server at {ADDR}.")
    print(f"Details: {e}")
    input('press enter to exit')
    client_socket = None  # Ensure client_socket is defined even if connection fails

# GUI part, using this tkinter toolkit since it's easy to just import this and use it.
top = tkinter.Tk()
top.title("Chatter")

messages_frame = tkinter.Frame(top)
my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("After requested name, type here")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
# This part will contain the messages.
msg_list = tkinter.Listbox(messages_frame, height=35, width=200, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()
messages_frame.pack()

entry_field = tkinter.Entry(top, textvariable=my_msg)
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

receive_thread = Thread(target=receive)
receive_thread.daemon = True  # Thread will exit when the main thread does.
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution

#!/usr/bin/env python3
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from datetime import datetime

LOG_FILE = "chat_log.txt"  # Define the log file name
clients = {}
addresses = {}

#----Now comes the sockets part----
HOST = input('Enter host (host IP or use "localhost"): ')
PORT = input('Enter port (Port to open, integer only, between 1025 and 65535): ')
if not HOST:
    HOST = "localhost" # Default value if blank
if not PORT:
    PORT = 33000 # Default value, probably should put error handling here and re-prompt if not within range
if int(PORT) < 1025 or int(PORT) > 65535:
    print("Port must be between 1025 and 65535, setting default arbitrarily to 33000.")
    PORT = 33000 # Default value, probably should put error handling here and re-prompt if not within range
else:
    PORT = int(PORT)

BUFSIZ = 1024
ADDR = (HOST, PORT)
SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

def accept_incoming_connections():
    # Sets up handling for incoming clients.
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(bytes("Greetings! First type your name and press enter, then chat will show up here", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()

def handle_client(client):  # Takes client socket as argument.
    # Handles a single client connection.

    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type only "exit" to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        try:            
            msg = client.recv(BUFSIZ)
            if msg.decode("utf8") != "exit":
                broadcast(msg, name+": ")
            else:
                client.send(bytes("exit", "utf8"))
                client.close()
                del clients[client]
                broadcast(bytes("%s has left the chat." % name, "utf8"))
                break
        except OSError:
            break

def broadcast(msg, prefix=""):  # prefix is for name identification.
    # Broadcasts to all the clients.
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")  # Format: [YYYY-MM-DD HH:MM:SS]
    formatted_msg = timestamp + prefix + msg.decode("utf8")
    formatted_msg = str(formatted_msg)  # Ensure the message is a string
    with open(LOG_FILE, "a", encoding="utf8") as log_file:  # Open the log file in append mode
        log_file.write(formatted_msg + "\n")  # Write the message with a newline, nothing fancy, but doesn't work...
    
    for sock in list(clients): # list(clients) to avoid RuntimeError: dictionary changing size during iteration.
        try:
            sock.send(bytes(formatted_msg, "utf8"))
        except Exception as e:
            print(f"Error sending message to {clients[sock]}: {e}")
            sock.close()
            del clients[sock]

if __name__ == "__main__":
    SERVER.listen(5)
    print(f"Waiting for connection at {ADDR} ...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    input('press enter to exit')
    SERVER.close()
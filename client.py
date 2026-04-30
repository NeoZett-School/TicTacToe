import network
import socket
import sys

with open("config.txt", "r") as f:
    host = f.read().strip()
    client = network.Client(host=host, port=5000)
    client.connect()

active = True
while active:
    for event in client.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.sock.getsockname()}")
        elif event.type == network.CONNECTION_LOST:
            print(f"Connection to server lost.")
            active = False
    message = input("Enter a message to send to the server (or 'exit' to quit): ")
    if message.lower() == "exit":
        active = False
    else:
        try:
            client.socket.sendall(message.encode("utf-8"))
        except (BrokenPipeError, ConnectionResetError):
            print(f"Connection to server lost.")
            active = False

client.socket.close()

sys.exit()
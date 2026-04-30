import network
import socket
import sys

client = network.Client(host=socket.gethostname(), port=5000)
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
import network
import socket
import sys

import pygame

server = network.Server(port=5000)
server.start()

active = True
while active:
    for event in server.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.sock.getsockname()}")
        elif event.type == network.CONNECTION:
            print(f"Client connected from {event.sock.getpeername()}")
        elif event.type == network.MESSAGE:
            print(f"Received message: {event.data.decode('utf-8')} from {event.sock.getpeername()}")
        elif event.type == network.CONNECTION_LOST:
            print(f"Client disconnected.")
        elif event.type == network.SERVER_EXIT:
            print("Server is shutting down.")

server.socket.close()
sys.exit()
import network
import socket
import sys

from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
pygame.display.set_caption("TicTacToe - Server")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

server = network.Server(port=5000)
with open("config.txt", "w") as f:
    f.write(socket.gethostbyname(socket.gethostname()))
print("Starting server... Remember to share the config.txt file with your clients so they can connect!")
server.start()

board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
board.fill((255, 0, 0))
update_requested = True

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

active = True
while active:
    delta_time = clock.tick(60.0) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
    
    for event in server.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.sock.getsockname()}")
        elif event.type == network.CONNECTION:
            print(f"Client connected from {event.sock.getpeername()}")
            update_requested = True
        elif event.type == network.MESSAGE:
            ...
        elif event.type == network.CONNECTION_LOST:
            print(f"Client disconnected.")
        elif event.type == network.SERVER_EXIT:
            print("Server is shutting down.")
    
    if update_requested:
        data = pygame.image.tobytes(board, "RGBA")
        for conn in server.connections.values():
            conn["socket"].sendall(network.pack(data))
        update_requested = False
    
    screen.fill((255, 255, 255))

    screen.blit(board, board.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

server.socket.close()

pygame.quit()
sys.exit()
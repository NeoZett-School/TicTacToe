import network
import socket
import sys
import json

from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

pygame.init()

def decode_message(data: bytes):
    payload = json.loads(data.decode())
    return payload["type"], payload["data"]

WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
pygame.display.set_caption("TicTacToe - Server")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

server = network.Server(port=5000)
with open("config.txt", "w") as f:
    f.write(socket.gethostbyname(socket.gethostname()))
print("Starting server... Remember to share the config.txt file with your clients so they can connect!")
server.start()

font = pygame.font.SysFont("Georgia", 24)

title = font.render("TicTacToe - Server", True, (0, 0, 0))
title_rect = title.get_rect(center=(WIDTH // 2, 30))

board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))
board.fill((255, 255, 255))

board_state = [[None, None, None], [None, None, None], [None, None, None]]

update_requested = True

player_count = 0

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

board_image = pygame.image.load("assets/board.png").convert_alpha()
board_image = pygame.transform.scale(board_image, (BOARD_SIZE, BOARD_SIZE))
board.blit(board_image, (0, 0))

x_image = pygame.image.load("assets/x.png").convert_alpha()
x_image = pygame.transform.scale(x_image, (80, 80))
o_image = pygame.image.load("assets/o.png").convert_alpha()
o_image = pygame.transform.scale(o_image, (80, 80))

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
            player_count += 1
            update_requested = True
        elif event.type == network.MESSAGE:
            msg_type, data = decode_message(event.data)
            if msg_type == "PLACE":
                row, column, symbol = data["row"], data["column"], data["symbol"]
                board_state[row][column] = symbol
                x = column * (BOARD_SIZE // 3) + (BOARD_SIZE // 6) - 40
                y = row * (BOARD_SIZE // 3) + (BOARD_SIZE // 6) - 40
                if symbol == "X":
                    board.blit(x_image, (x, y))
                else:
                    board.blit(o_image, (x, y))
                update_requested = True
        elif event.type == network.CONNECTION_LOST:
            print(f"Client disconnected.")
            player_count -= 1
        elif event.type == network.SERVER_EXIT:
            print("Server is shutting down.")
            active = False
    
    if update_requested:
        data = pygame.image.tobytes(board, "RGBA")
        for conn in server.connections.values():
            conn["socket"].sendall(network.pack(data))
        update_requested = False
    
    screen.fill((255, 255, 255))

    screen.blit(title, title_rect)
    screen.blit(board, board.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

server.socket.close()

pygame.quit()
sys.exit()
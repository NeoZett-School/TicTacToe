import network
import socket
import sys
import json
import io
import base64

from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

pygame.init()

def encode_message(msg_type: str, **data) -> bytes:
    payload = {
        "type": msg_type,
        "data": data
    }
    return network.pack(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

def decode_message(data: bytes) -> tuple[str, dict]:
    payload = json.loads(data.decode())
    return payload["type"], payload["data"]

WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
pygame.display.set_caption("TicTacToe - Client")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

with open("config.txt", "r") as f:
    host = f.read().strip()
    client = network.Client(host=host, port=5000)
    client.connect()

header = pygame.font.SysFont("Georgia", 24)
paragraph = pygame.font.SysFont("Georgia", 18)

title = header.render("TicTacToe - Client", True, (0, 0, 0))
title_rect = title.get_rect(center=(WIDTH // 2, 30))

info = paragraph.render("Waiting for server...", True, (0, 0, 0))
info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))

name = "[Loading...]"

board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

active = True
while active:
    delta_time = clock.tick(60.0) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_x, mouse_y = event.pos
                board_x = (mouse_x - (WIDTH - BOARD_SIZE) // 2) // (BOARD_SIZE // 3)
                board_y = (mouse_y - (HEIGHT - BOARD_SIZE) // 2) // (BOARD_SIZE // 3)
                if 0 <= board_x < 3 and 0 <= board_y < 3:
                    client.socket.sendall(encode_message("place", row=board_y, column=board_x))

    for event in client.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.sock.getsockname()}")
        elif event.type == network.MESSAGE:
            msg_type, data = decode_message(event.data)
            if msg_type == "board_update":
                image_bytes = base64.b64encode(data["content"].encode('ascii'))
                img_io = io.BytesIO(base64.b64decode(data["content"]))
                board = pygame.image.load(img_io, "PNG") 
            elif msg_type == "turn":
                turn = data["turn"]
                info = paragraph.render(f"Player {turn}'s turn" if turn != name else f"It is your turn to place your '{name}'", True, (0, 0, 0))
                info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            elif msg_type == "player":
                name = data["name"]
                title = header.render(f"TicTacToe - Player {name}", True, (0, 0, 0))
                title_rect = title.get_rect(center=(WIDTH // 2, 30))
            elif msg_type == "game_over":
                winner = data["winner"]
                if winner is None:
                    info = paragraph.render("Game over! It's a tie!", True, (0, 0, 0))
                elif winner == name:
                    info = paragraph.render("Game over! You win!", True, (0, 0, 0))
                else:
                    info = paragraph.render(f"Game over! Player {winner} wins!", True, (0, 0, 0))
                info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
        elif event.type == network.CONNECTION_LOST:
            print(f"Connection to server lost.")
            active = False
    
    screen.fill((255, 255, 255))

    screen.blit(title, title_rect)
    screen.blit(info, info_rect)
    screen.blit(board, board.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

client.socket.close()

pygame.quit()
sys.exit()
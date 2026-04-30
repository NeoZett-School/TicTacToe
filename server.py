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

header = pygame.font.SysFont("Georgia", 24)
paragraph = pygame.font.SysFont("Georgia", 18)

title = header.render("TicTacToe - Server", True, (0, 0, 0))
title_rect = title.get_rect(center=(WIDTH // 2, 30))

info = paragraph.render("Waiting for players...", True, (0, 0, 0))
info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))

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

o_player = None
x_player = None

turn = None

active = True
while active:
    delta_time = clock.tick(60.0) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False
    
    for event in server.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.addr}")
        elif event.type == network.CONNECTION:
            print(f"Client connected from {event.addr}")
            player_count += 1
            if player_count == 1:
                o_player = event.addr
                event.sock.sendall(encode_message("player", name="o"))
                print("Assigned O to player.")
                if turn is None:
                    turn = o_player
                    for conn in server.connections.values():
                        conn["socket"].sendall(encode_message("turn", turn="o"))
                    info = paragraph.render(f"Player o's turn", True, (0, 0, 0))
                    info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            elif player_count == 2:
                x_player = event.addr
                event.sock.sendall(encode_message("player", name="x"))
                print("Assigned X to player.")
                if turn is None:
                    turn = x_player
                    for conn in server.connections.values():
                        conn["socket"].sendall(encode_message("turn", turn="x"))
                    info = paragraph.render(f"Player x's turn", True, (0, 0, 0))
                    info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
                server.can_connect = False
            else:
                print("Too many players connected. Disconnecting client.")
                event.sock.close()
                player_count -= 1
            update_requested = True
        elif event.type == network.MESSAGE:
            msg_type, data = decode_message(event.data)
            if msg_type == "place":
                if turn not in (o_player, x_player):
                    turn = None
                    continue
                if turn != event.addr:
                    continue
                row, column = data["row"], data["column"]
                x = column * (BOARD_SIZE // 3) + (BOARD_SIZE // 6) - 40
                y = row * (BOARD_SIZE // 3) + (BOARD_SIZE // 6) - 40
                if event.addr == x_player:
                    board.blit(x_image, (x, y))
                    board_state[row][column] = "X"
                    for conn in server.connections.values():
                        conn["socket"].sendall(encode_message("turn", turn="o"))
                    info = paragraph.render(f"Player o's turn", True, (0, 0, 0))
                    info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
                    turn = o_player
                else:
                    board.blit(o_image, (x, y))
                    board_state[row][column] = "O"
                    for conn in server.connections.values():
                        conn["socket"].sendall(encode_message("turn", turn="x"))
                    info = paragraph.render(f"Player x's turn", True, (0, 0, 0))
                    info_rect = info.get_rect(center=(WIDTH // 2, HEIGHT - 30))
                    turn = x_player
                update_requested = True
        elif event.type == network.CONNECTION_LOST:
            print(f"Client disconnected.")
            server.can_connect = True
            player_count -= 1
        elif event.type == network.SERVER_EXIT:
            print("Server is shutting down.")
            active = False
    
    if update_requested:
        buffer = io.BytesIO()
        pygame.image.save(board, buffer, "PNG")
        data = buffer.getvalue()
        content_b64 = base64.b64encode(data).decode('ascii')
        for conn in server.connections.values():
            conn["socket"].sendall(encode_message("board_update", content=content_b64))
        update_requested = False
    
    screen.fill((255, 255, 255))

    screen.blit(title, title_rect)
    screen.blit(info, info_rect)
    screen.blit(board, board.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

server.socket.close()

pygame.quit()
sys.exit()
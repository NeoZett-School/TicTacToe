import network
import socket
import sys

from os import environ

environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
BOARD_SIZE = 400
pygame.display.set_caption("TicTacToe - Client")
pygame.display.set_icon(pygame.image.load("assets/icon.png"))

with open("config.txt", "r") as f:
    host = f.read().strip()
    client = network.Client(host=host, port=5000)
    client.connect()

board = pygame.Surface((BOARD_SIZE, BOARD_SIZE))

screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

active = True
while active:
    delta_time = clock.tick(60.0) / 1000.0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            active = False

    for event in client.get_events():
        if event.type == network.SERVER_START:
            print(f"Server started on {event.sock.getsockname()}")
        elif event.type == network.MESSAGE:
            board = pygame.image.frombytes(event.data, (BOARD_SIZE, BOARD_SIZE), "RGBA")
        elif event.type == network.CONNECTION_LOST:
            print(f"Connection to server lost.")
            active = False
    
    screen.fill((255, 255, 255))

    screen.blit(board, board.get_rect(center=(WIDTH // 2, HEIGHT // 2)))

    pygame.display.flip()

client.socket.close()

pygame.quit()
sys.exit()
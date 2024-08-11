import sys

import pygame

pygame.init()

HEIGHT = pygame.display.Info().current_h
WIDTH = pygame.display.Info().current_w

FPS = 25


def handle_events():
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                sys.exit()


def update_window():
    global WIDTH, HEIGHT
    WIDTH = wdw.get_width()
    HEIGHT = wdw.get_height()
    wdw.fill((0, 0, 0))
    pygame.draw.rect(wdw, (255, 0, 0), (WIDTH / 2 + 5, HEIGHT / 2 + 5, 10, 10))


if __name__ == '__main__':

    wdw = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('denoiser')

    while True:
        handle_events()
        update_window()

        pygame.display.update()

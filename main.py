import sys

import pygame

pygame.init()

HEIGHT = pygame.display.Info().current_h
WIDTH = pygame.display.Info().current_w

wdw = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('denoiser')

BG_PATH = "images/test1.png"
bg_img = pygame.image.load(BG_PATH)

wdw_width = wdw.get_width()
wdw_height = wdw.get_height()


def handle_events():
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                sys.exit()
            case pygame.VIDEORESIZE:
                update_sizing()


def update_sizing():
    global wdw_width, wdw_height
    wdw_width = wdw.get_width()
    wdw_height = wdw.get_height()

    # make bg image full screen. Assume it is thinner than screen width
    global bg_img
    new_height = wdw_height
    new_width = (wdw_height / bg_img.get_height()) * bg_img.get_width()
    bg_img = pygame.transform.scale(bg_img, (new_height, new_width))


def update_drawing():
    global bg_img
    global wdw_width
    global wdw_height

    wdw.fill((0, 0, 0))

    # draw the background image
    bg_top_left_x = (wdw_width / 2) - (bg_img.get_width() / 2)
    bg_top_left_y = (wdw_height / 2) - (bg_img.get_height() / 2)
    wdw.blit(bg_img, (bg_top_left_x, bg_top_left_y))

    # draw noise
    pygame.draw.rect(wdw, (255, 0, 0), (wdw_width / 2 + 5, wdw_height / 2 + 5, 10, 10))


if __name__ == '__main__':

    while True:
        handle_events()
        update_drawing()

        pygame.display.update()
        pygame.display.flip()

import copy
import sys
import threading
import random
from tkinter import Tk
import numpy as np

import pygame
from PIL import Image, ImageFilter

pygame.init()

thread_settings = None

HEIGHT = pygame.display.Info().current_h
WIDTH = pygame.display.Info().current_w

NOISE_PXL_WDHT = 5
NOISE_PXL_HGHT = 5

wdw = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('denoiser')

FPS = 15
clk = pygame.time.Clock()

CODE_IMG_PATH = "images/test1.png"
img_orig = Image.open(CODE_IMG_PATH)
img_curr = img_orig.filter(ImageFilter.GaussianBlur(2))
visibility = 0

wdw_width = wdw.get_width()
wdw_height = wdw.get_height()


def handle_events():
    global wdw, thread_settings
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()

                sys.exit()
            case pygame.VIDEORESIZE:
                update_sizing()
            case pygame.MOUSEBUTTONDOWN:
                pygame.display.toggle_fullscreen()
                update_sizing()


def update_sizing():
    global wdw_width, wdw_height
    wdw_width = wdw.get_width()
    wdw_height = wdw.get_height()

    # make code_img image full screen. Assume it is thinner than screen width
    global img_curr, img_orig
    new_height = wdw_height
    new_width = int((wdw_height / img_curr.height) * img_curr.width)
    img_curr = img_orig.resize((new_width, new_height)).filter(ImageFilter.GaussianBlur(200))


def draw_noise_pixel(wdw: pygame.Surface, color: tuple[int, int, int], coord: tuple[int, int]) -> None:
    global NOISE_PXL_WDHT, NOISE_PXL_HGHT
    coord_x = coord[0] - NOISE_PXL_WDHT / 2
    coord_y = coord[1] - NOISE_PXL_HGHT / 2
    pygame.draw.rect(wdw, color, (coord_x, coord_y, NOISE_PXL_WDHT, NOISE_PXL_HGHT))


def calc_code_value(x, y):
    return (0, 0, 0)


def draw_noise():
    global img_curr
    global wdw_width, wdw_height

    wdw.fill((0, 0, 0))

    code_img_top_left_x = (wdw_width // 2) - (img_curr.width // 2)
    code_img_top_left_y = (wdw_height // 2) - (img_curr.height // 2)

    # code_img = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), 'RGB')
    # wdw.blit(code_img, (code_img_top_left_x, code_img_top_left_y)) # optionally show the code_img image for development purposes

    # distort the code image
    img_curr_size = copy.deepcopy(img_curr.size)
    img_curr = img_orig.filter(ImageFilter.GaussianBlur(visibility))
    img_curr = img_curr.resize(img_curr_size)
    pygme_code_img = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), 'RGB').convert()
    # wdw.blit(pygme_code_img, (code_img_top_left_x, code_img_top_left_y))

    # draw noise based on the state of the code image
    noise_pxls_horizontal = wdw_width // NOISE_PXL_WDHT
    noise_pxls_vertical = wdw_height // NOISE_PXL_HGHT

    # numpy noise code
    raster = np.random.normal(100, 75, (noise_pxls_vertical, noise_pxls_horizontal, 3)).astype(np.uint8)



    pil_noise = Image.fromarray(raster, 'RGB')
    pil_noise = pil_noise.resize((wdw_width, wdw_height))
    pyg_img = pygame.image.frombytes(pil_noise.tobytes(), (pil_noise.width, pil_noise.height), 'RGB')
    wdw.blit(pyg_img, (0, 0))


def dials_main():
    global tk_root
    # create root window
    tk_root = Tk()

    # root window title and dimension
    tk_root.title("Denoiser settings")
    # Set geometry (widthxheight)
    tk_root.geometry('350x200')

    # all widgets will be here
    # Execute Tkinter
    tk_root.mainloop()


if __name__ == '__main__':
    # thread_settings = threading.Thread(target=dials_main)
    # thread_settings.start()

    while True:
        handle_events()
        draw_noise()

        pygame.display.update()
        pygame.display.flip()

        visibility += 1
        visibility = visibility % 20

        clk.tick(FPS)

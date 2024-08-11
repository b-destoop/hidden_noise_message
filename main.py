import copy
import sys
from tkinter import Tk

import cv2 as cv
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

CODE_IMG_PATH = "images/test2_inv.png"
FORMAT = "RGB"
img_orig = Image.open(CODE_IMG_PATH).convert(FORMAT)
img_curr = img_orig.filter(ImageFilter.GaussianBlur(2))
invisibility = 0

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

    # distort the code image
    img_curr_size = copy.deepcopy(img_curr.size)
    img_curr = img_orig.filter(ImageFilter.GaussianBlur(invisibility))
    img_curr = img_curr.resize(img_curr_size)

    # draw noise based on the state of the code image
    noise_pxls_horizontal = wdw_width // NOISE_PXL_WDHT
    noise_pxls_vertical = wdw_height // NOISE_PXL_HGHT

    # numpy noise code
    code = np.asarray(img_curr)
    h_start, w_start, _ = code.shape
    code = cv.resize(code, (noise_pxls_horizontal, noise_pxls_vertical), interpolation=cv.INTER_NEAREST)  # less pixels

    raster_code = np.random.normal(0, invisibility, (noise_pxls_vertical, noise_pxls_horizontal, 3)).astype(np.uint8)
    raster_code = raster_code * code
    raster_code = cv.resize(raster_code, (wdw_width, wdw_height), interpolation=cv.INTER_AREA)

    raster_rand = np.random.normal(255 / 2, 255, (noise_pxls_vertical, noise_pxls_horizontal, 3)).astype(np.uint8)
    raster_rand = raster_rand * (np.invert(code) // 255)
    raster_rand = cv.resize(raster_rand, (wdw_width, wdw_height), interpolation=cv.INTER_AREA)

    result = np.bitwise_xor(raster_rand, raster_code)

    pil_noise = Image.fromarray(result, FORMAT)
    pyg_img = pygame.image.frombytes(pil_noise.tobytes(), (pil_noise.width, pil_noise.height), FORMAT)
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

        invisibility += 1
        invisibility = invisibility % 20

        print(invisibility)

        clk.tick(FPS)

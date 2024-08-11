import copy
import sys
import threading
import time
from tkinter import Tk

import cv2 as cv
import numpy as np
import pygame
from PIL import Image, ImageFilter

import sounddevice as sd
import wavio as wv

pygame.init()

# PYGAME
HEIGHT = pygame.display.Info().current_h
WIDTH = pygame.display.Info().current_w

NOISE_PXL_WDHT = 5
NOISE_PXL_HGHT = 5

wdw = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('denoiser')

FPS = 15
clk = pygame.time.Clock()

CODE_IMG_PATH = "static/test2_inv.png"
FORMAT = "RGB"
img_orig = Image.open(CODE_IMG_PATH).convert(FORMAT)
img_curr = img_orig.filter(ImageFilter.GaussianBlur(2))
invisibility = 0

wdw_width = wdw.get_width()
wdw_height = wdw.get_height()

# SOUND
volume = 0
volume_max = 0
volume_min = 1000
volume_rel = 0
volume_rel_avg = 0

# THREADS
running = True
threads = []


def handle_events():
    global wdw, thread_settings, threads, running
    for event in pygame.event.get():
        match event.type:
            case pygame.QUIT:
                pygame.quit()
                running = False
                for t in threads:
                    t.join()
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
    global running, tk_root
    # create root window
    tk_root = Tk()

    # root window title and dimension
    tk_root.title("Denoiser settings")
    # Set geometry (widthxheight)
    tk_root.geometry('350x200')

    # all widgets will be here
    # Execute Tkinter
    tk_root.mainloop()


def sound_main():
    global running, volume, volume_max, volume_min, volume_rel, volume_rel_avg
    sample_freq = 44100
    rec_duration = 0.3  # seconds
    run_avg_duration = 6  # seconds
    vol_arr = [0] * int(run_avg_duration // rec_duration)
    vol_arr_i = 0
    while running:
        # record
        recording = sd.rec(int(rec_duration * sample_freq), channels=1, dtype='int16')
        sd.wait()
        volume = 20 * np.log10(np.absolute(np.average(recording)))  # to dB

        # update metrics
        if volume > volume_max:
            volume_max = volume
        if volume < volume_min:
            volume_min = volume
        volume_rel = (volume + abs(volume_min)) / (volume_max + abs(volume_min))

        vol_arr[vol_arr_i] = volume_rel
        volume_rel_avg = np.average(vol_arr)

        vol_arr_i += 1
        vol_arr_i = vol_arr_i % len(vol_arr)

        print(
            f"vrel={volume_rel:.2f}, vrela={volume_rel_avg:.2f}, v={volume:.2f}, vmax={volume_max:.2f}, vmin={volume_min:.2f}")


def draw_volumes():
    font = pygame.font.Font('static/Uroob-Regular.ttf', 50)

    circle_x = wdw_width // 6
    circle_y = wdw_height - (wdw_height * volume_rel)
    pygame.draw.circle(wdw, (0, 255, 255), (circle_x, circle_y), 10)
    text = font.render('vrel', True, (100, 255, 100))
    wdw.blit(text, text.get_rect(center=(circle_x, wdw_height - 10)))

    circle_x = 2 * wdw_width // 6
    circle_y = wdw_height - (wdw_height * volume_rel_avg)
    pygame.draw.circle(wdw, (0, 255, 255), (circle_x, circle_y), 10)
    text = font.render('vrela', True, (100, 255, 100))
    wdw.blit(text, text.get_rect(center=(circle_x, wdw_height - 10)))

    circle_x = 3 * wdw_width // 6
    circle_y = wdw_height // 2 - volume
    pygame.draw.circle(wdw, (0, 255, 255), (circle_x, circle_y), 10)
    text = font.render('vol', True, (100, 255, 100))
    wdw.blit(text, text.get_rect(center=(circle_x, wdw_height - 10)))

    circle_x = 4 * wdw_width // 6
    circle_y = wdw_height // 2 - volume_max
    pygame.draw.circle(wdw, (0, 255, 255), (circle_x, circle_y), 10)
    text = font.render('vmax', True, (100, 255, 100))
    wdw.blit(text, text.get_rect(center=(circle_x, wdw_height - 10)))

    circle_x = 5 * wdw_width // 6
    circle_y = wdw_height // 2 - volume_min
    pygame.draw.circle(wdw, (0, 255, 255), (circle_x, circle_y), 10)
    text = font.render('vmin', True, (100, 255, 100))
    wdw.blit(text, text.get_rect(center=(circle_x, wdw_height - 10)))


if __name__ == '__main__':
    # thread_settings = threading.Thread(target=dials_main)
    # thread_settings.start()

    thread_sound = threading.Thread(target=sound_main)
    thread_sound.start()

    while True:
        handle_events()

        wdw.fill((0, 0, 0))

        # draw_noise()
        draw_volumes()

        pygame.display.update()
        pygame.display.flip()

        invisibility += 1
        invisibility = invisibility % 20

        clk.tick(FPS)

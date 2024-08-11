import copy
import sys

import pygame
from PIL import Image, ImageFilter

pygame.init()

HEIGHT = pygame.display.Info().current_h
WIDTH = pygame.display.Info().current_w

NOISE_PXL_WDHT = 5
NOISE_PXL_HGHT = 5

wdw = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption('denoiser')

FPS = 25
clk = pygame.time.Clock()

CODE_IMG_PATH = "images/test1.png"
img_orig = Image.open(CODE_IMG_PATH)
img_curr = img_orig.filter(ImageFilter.GaussianBlur(2))
# code_img = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), "RGB")

wdw_width = wdw.get_width()
wdw_height = wdw.get_height()


def handle_events():
    global wdw
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
    img_curr = img_orig.filter(ImageFilter.GaussianBlur(20))
    img_curr = img_curr.resize(img_curr_size)
    code_img = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), 'RGB')

    # draw noise based on the state of the code image
    noise_pxls_horizontal = wdw_width // NOISE_PXL_WDHT
    noise_pxls_vertical = wdw_height // NOISE_PXL_HGHT

    for pxl in range(noise_pxls_horizontal * noise_pxls_vertical):
        # get the coordinates of the pixel
        pxl_tl_x = (pxl % noise_pxls_horizontal) * NOISE_PXL_WDHT
        pxl_tl_y = (pxl // noise_pxls_horizontal) * NOISE_PXL_HGHT

        pxl_mid_x = pxl_tl_x + NOISE_PXL_WDHT // 2
        pxl_mid_y = pxl_tl_y + NOISE_PXL_HGHT // 2

        # check if the pixel falls over the code image
        if (pxl_mid_x >= code_img_top_left_x) \
                and (pxl_mid_x < (code_img_top_left_x + code_img.get_width())) \
                and (pxl_mid_y >= code_img_top_left_y) \
                and (pxl_mid_y < code_img_top_left_y + code_img.get_height()):
            # get the color value of that part of the code_img image
            rel_x = pxl_mid_x - code_img_top_left_x
            rel_y = pxl_mid_y - code_img_top_left_y
            color = code_img.get_at((rel_x, rel_y))

            # color the pixel
            draw_noise_pixel(wdw, color, (pxl_mid_x, pxl_mid_y))
            continue

        # just draw if it does not fall over the image
        draw_noise_pixel(wdw, (0, 255, 0), (pxl_mid_x, pxl_mid_y))


if __name__ == '__main__':

    while True:
        handle_events()
        draw_noise()

        pygame.display.update()
        pygame.display.flip()

        clk.tick(FPS)

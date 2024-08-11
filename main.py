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
code_img = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), "RGB")

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

    # make code_img image full screen. Assume it is thinner than screen width
    global code_img, img_curr
    img_curr_pg = pygame.image.frombytes(img_curr.tobytes(), (img_curr.width, img_curr.height), 'RGB')
    new_height = wdw_height
    new_width = (wdw_height / img_curr_pg.get_height()) * img_curr_pg.get_width()
    code_img = pygame.transform.scale(img_curr_pg, (new_height, new_width))


def draw_noise_pixel(wdw: pygame.Surface, color: tuple[int, int, int], coord: tuple[int, int]) -> None:
    global NOISE_PXL_WDHT, NOISE_PXL_HGHT
    coord_x = coord[0] - NOISE_PXL_WDHT / 2
    coord_y = coord[1] - NOISE_PXL_HGHT / 2
    pygame.draw.rect(wdw, color, (coord_x, coord_y, NOISE_PXL_WDHT, NOISE_PXL_HGHT))


def update_drawing():
    global code_img
    global wdw_width
    global wdw_height

    wdw.fill((0, 0, 0))

    code_img_top_left_x = (wdw_width // 2) - (code_img.get_width() // 2)
    code_img_top_left_y = (wdw_height // 2) - (code_img.get_height() // 2)

    # wdw.blit(code_img, (code_img_top_left_x, code_img_top_left_y)) # optionally show the code_img image for development purposes

    # draw noise box per box
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
        update_drawing()

        pygame.display.update()
        pygame.display.flip()

        clk.tick(FPS)

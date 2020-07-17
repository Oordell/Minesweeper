#!/usr/bin/env python3

import pygame as py
from Constants import *


class Box(object):
    def __init__(self):
        self.clicked = False
        self.flag = False
        self.mine = False
        self.num_of_surrounding_mines = 0
        self.num_of_surrounding_boxes_total = 8
        self.num_of_surrounding_unchecked_boxed = 8
        self.locked = False


class GameUI(object):
    def __init__(self, rows=10, cols=10):
        self.num_of_rows = rows
        self.num_of_columns = cols

        py.init()
        py.display.set_caption("MineSweeper")

        # Load images:
        self.img_box_new = py.image.load('images/box_new.png')
        self.img_box_new = py.transform.scale(self.img_box_new, (BOX_WIDTH, BOX_HEIGHT))
        self.img_box_clicked = py.image.load('images/box_clicked.png')
        self.img_box_clicked = py.transform.scale(self.img_box_clicked, (BOX_WIDTH, BOX_HEIGHT))
        self.img_box_flag = py.image.load('images/box_flaged.png')
        self.img_box_flag = py.transform.scale(self.img_box_flag, (BOX_WIDTH, BOX_HEIGHT))
        self.img_mine_scale = BOX_HEIGHT / 10
        self.img_mine = py.image.load('images/mine.png')
        self.img_mine = py.transform.scale(self.img_mine, (int(BOX_WIDTH - self.img_mine_scale),
                                                           int(BOX_HEIGHT - self.img_mine_scale)))
        self.img_smiley_new_game = py.image.load('images/smiley_new_game.png')
        self.img_smiley_new_game = py.transform.scale(self.img_smiley_new_game,
                                                      (int(BOX_WIDTH * 1.5), int(BOX_HEIGHT * 1.5)))
        self.img_smiley_dead = py.image.load('images/smiley_dead.png')
        self.img_smiley_dead = py.transform.scale(self.img_smiley_dead, (int(BOX_WIDTH * 1.5), int(BOX_HEIGHT * 1.5)))
        self.img_smiley_win = py.image.load('images/smiley_win.png')
        self.img_smiley_win = py.transform.scale(self.img_smiley_win, (int(BOX_WIDTH * 1.5), int(BOX_HEIGHT * 1.5)))

        # Window dimensions:
        self.top_space = 90
        self.screen_height = BOX_HEIGHT * self.num_of_rows + self.top_space
        self.screen_width = BOX_WIDTH * self.num_of_columns

        # Display window:
        self.screen = py.display
        self.screen_surface = self.screen.set_mode((self.screen_width, self.screen_height))
        self.clock = py.time.Clock()
        self.fps = 25

    def draw_new_world(self, num_of_mines, minefield):
        # Cheating / debug variable to see all boxes
        view_all = False

        # Draw background:
        self.screen_surface.fill(COLOR_BACKGROUND)

        # ----------------------------------------------------------------------------------------
        # ---------------------------------- Draw top info ---------------------------------------
        # ----------------------------------------------------------------------------------------
        # Smiley:
        self.draw_smiley(self.img_smiley_new_game)

        # Mines:
        font = py.font.Font('freesansbold.ttf', SIZE_FONT_MINES)
        text = font.render("Mines: ", True, COLOR_TEXT_TOP)
        text_rect = text.get_rect()
        text_rect.center = (self.top_space - self.top_space / 3, self.top_space / 4)
        self.screen_surface.blit(text, text_rect)

        # Mine logo:
        self.screen_surface.blit(self.img_mine, (self.top_space / 4, self.top_space / 2))

        # Number of mines:
        text = font.render(str(num_of_mines), True, COLOR_TEXT_TOP)
        text_rect.center = (self.top_space + 15, self.top_space * 2 / 3)
        self.screen_surface.blit(text, text_rect)

        # Flags:
        text = font.render("Flags: ", True, COLOR_TEXT_TOP)
        text_rect.center = (self.screen_width - self.top_space / 2, self.top_space / 4)
        self.screen_surface.blit(text, text_rect)

        # Flag logo:
        self.screen_surface.blit(self.img_box_flag, (self.screen_width - self.top_space, self.top_space / 2))

        # Number of flags:
        self.draw_update_flag_counter(num=0)

        # ----------------------------------------------------------------------------------------
        # ---------------------------------- Draw the map ----------------------------------------
        # ----------------------------------------------------------------------------------------
        for row in range(0, self.num_of_rows):
            for col in range(0, self.num_of_columns):
                if not view_all:
                    self.screen_surface.blit(self.img_box_new, (col * BOX_WIDTH, row * BOX_HEIGHT + self.top_space))
                else:
                    self.screen_surface.blit(self.img_box_clicked, (col * BOX_WIDTH, row * BOX_HEIGHT + self.top_space))
                if view_all and minefield[row][col].mine:
                    self.screen_surface.blit(self.img_mine, (col * BOX_WIDTH + self.img_mine_scale,
                                                             row * BOX_HEIGHT + self.img_mine_scale + self.top_space))
                elif view_all and minefield[row][col].num_of_surrounding_mines > 0:
                    font = py.font.Font('freesansbold.ttf', SIZE_FONT_NUMBERS)
                    text = font.render(str(minefield[row][col].num_of_surrounding_mines), True,
                                       COLOR_TEXT_NUMBERS[minefield[row][col].num_of_surrounding_mines - 1])
                    text_rect = text.get_rect()
                    text_rect.center = ((col * BOX_WIDTH) + (BOX_WIDTH / 2),
                                        (row * BOX_HEIGHT) + (BOX_HEIGHT / 2) + self.top_space)
                    self.screen_surface.blit(text, text_rect)
        self.update_display()

    def draw_normal_box(self, pos):
        self.screen_surface.blit(self.img_box_new, (pos[0] * BOX_WIDTH, pos[1] * BOX_HEIGHT + self.top_space))

    def draw_clicked_box(self, pos):
        self.screen_surface.blit(self.img_box_clicked, (pos[0] * BOX_WIDTH, pos[1] * BOX_HEIGHT + self.top_space))

    def draw_mine(self, pos):
        self.screen_surface.blit(self.img_mine, (pos[0] * BOX_WIDTH + self.img_mine_scale,
                                                 pos[1] * BOX_HEIGHT + self.img_mine_scale + self.top_space))

    def draw_number_on_box(self, pos, num):
        font = py.font.Font('freesansbold.ttf', SIZE_FONT_NUMBERS)
        text = font.render(str(num), True, COLOR_TEXT_NUMBERS[num - 1])
        text_rect = text.get_rect()
        text_rect.center = ((pos[0] * BOX_WIDTH) + (BOX_WIDTH / 2),
                            (pos[1] * BOX_HEIGHT) + (BOX_HEIGHT / 2) + self.top_space)
        self.screen_surface.blit(text, text_rect)

    def draw_flag_on_box(self, pos):
        self.screen_surface.blit(self.img_box_flag, (pos[0] * BOX_WIDTH, pos[1] * BOX_HEIGHT + self.top_space))

    def draw_update_flag_counter(self, num):
        r = (self.screen_width - self.top_space * 3 / 5, self.top_space / 2, self.top_space, self.top_space / 2)
        py.draw.rect(self.screen_surface, COLOR_BACKGROUND, r)
        font = py.font.Font('freesansbold.ttf', SIZE_FONT_MINES)
        text = font.render(str(num), True, COLOR_TEXT_TOP)
        text_rect = text.get_rect()
        text_rect.center = (self.screen_width - self.top_space / 3, self.top_space * 2 / 3)
        self.screen_surface.blit(text, text_rect)

    def draw_smiley_dead(self):
        self.draw_smiley(self.img_smiley_dead)

    def draw_smiley_win(self):
        self.draw_smiley(self.img_smiley_win)

    def draw_smiley(self, img):
        self.screen_surface.blit(img, (self.get_smiley_location(img)))

    def get_smiley_location(self, img):
        col, row = self.screen_width / 2 - img.get_rect().size[0] / 2, self.top_space / 2 - img.get_rect().size[1] / 2
        return col, row

    def run(self):
        while True:
            for event in py.event.get():
                if event.type == py.QUIT:
                    py.quit()
                    quit()
                if event.type == py.KEYDOWN:
                    if event.key == py.K_ESCAPE:
                        py.quit()
                        quit()
                if event.type == py.MOUSEBUTTONDOWN:
                    val = [event.pos[0], event.pos[1], event.button]
                    return val
            self.update_display()

    def update_display(self):
        py.display.update()
        self.clock.tick(self.fps)


if __name__ == '__main__':
    pass

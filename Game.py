#!/usr/bin/env python3

import random as rand
import GameUI
from GameUI import GameUI as Gui
from GameUI import Box as Box

# --------------------------------------------------------
# Constants:
MAX_ROWS = 30
MAX_COLUMNS = 50
MIN_ROWS = 10
MIN_COLUMNS = 10
# --------------------------------------------------------


class MineSweeper(object):
    def __init__(self, rows=10, columns=10, view_gui=True):
        # Game settings:
        self.num_of_rows = MIN_ROWS if rows < MIN_ROWS else MAX_ROWS if rows > MAX_ROWS else rows
        self.num_of_columns = MIN_COLUMNS if columns < MIN_COLUMNS else MAX_COLUMNS if columns > MAX_COLUMNS else columns
        self.num_of_mines = int(self.num_of_rows * self.num_of_columns / 7)
        self.view_gui = view_gui
        self.minefield = [[Box()], [Box()]]
        self.new_game = True
        self.num_of_mines_left = self.num_of_mines
        self.num_of_flags_placed = 0

        # Game settings (Not visible by user or AI)
        self.num_of_correctly_placed_flags = 0
        self.num_of_wrongly_placed_flags = 0

        # Create GUI:
        self.gui = None
        if self.view_gui:
            self.gui = Gui(rows=self.num_of_rows, cols=self.num_of_columns)

        # Init new game
        self.create_new_game()

    def create_new_game(self):
        self.new_game = True
        self.num_of_mines_left = self.num_of_mines
        self.num_of_flags_placed = 0
        self.num_of_correctly_placed_flags = 0
        self.num_of_wrongly_placed_flags = 0
        self.place_mines()
        if self.view_gui:
            self.gui.draw_new_world(num_of_mines=self.num_of_mines, minefield=self.minefield)

    def game_over(self):
        for row in range(0, self.num_of_rows):
            for col in range(0, self.num_of_columns):
                self.minefield[row][col].locked = True
                if self.minefield[row][col].mine and self.view_gui:
                    self.gui.draw_mine([col, row])
        self.gui.draw_smiley_dead()

    def game_won(self):
        for row in range(0, self.num_of_rows):
            for col in range(0, self.num_of_columns):
                if not self.minefield[row][col].clicked:
                    self.minefield[row][col].clicked = True
                    if self.view_gui:
                        self.gui.draw_clicked_box([col, row])
                        if self.minefield[row][col].mine:
                            self.gui.draw_mine([col, row])
                        elif self.minefield[row][col].num_of_surrounding_mines > 0:
                            self.gui.draw_number_on_box([col, row], self.minefield[row][col].num_of_surrounding_mines)
        self.gui.draw_smiley_win()

    def place_mines(self):
        self.create_new_empty_minefield()
        valid_mines_placed = 0
        while valid_mines_placed < self.num_of_mines:
            row, col = rand.randint(0, self.num_of_rows - 1), rand.randint(0, self.num_of_columns - 1)
            if not self.minefield[row][col].mine:
                self.minefield[row][col].mine = True
                self.add_to_mine_counter([col, row])
                valid_mines_placed += 1
        if not self.valid_mine_placement():
            self.place_mines()

    def create_new_empty_minefield(self):
        self.minefield = []
        for row in range(0, self.num_of_rows):
            temp_row = []
            for col in range(0, self.num_of_columns):
                box = Box()
                if (row == 0 or row == self.num_of_rows - 1) and (col == 0 or col == self.num_of_columns - 1):
                    box.num_of_surrounding_boxes_total = 3
                    box.num_of_surrounding_unchecked_boxed = 3
                elif row == 0 or row == self.num_of_rows - 1 or col == 0 or col == self.num_of_columns - 1:
                    box.num_of_surrounding_boxes_total = 5
                    box.num_of_surrounding_unchecked_boxed = 5
                temp_row.append(box)
            self.minefield.append(temp_row)

    def add_to_mine_counter(self, pos):
        for row in range(pos[1] - 1, pos[1] + 2):
            for col in range(pos[0] - 1, pos[0] + 2):
                if row < 0 or row > self.num_of_rows - 1 or col < 0 or col > self.num_of_columns - 1:
                    pass
                else:
                    self.minefield[row][col].num_of_surrounding_mines += 1

    @staticmethod
    def valid_mine_placement():
        # TODO: Make validation function
        return True

    def left_click_box(self, pos):
        col = pos[0]
        row = pos[1]

        if self.minefield[row][col].clicked or self.minefield[row][col].locked:
            return
        self.minefield[row][col].clicked = True
        self.minefield[row][col].locked = True

        if self.view_gui:
            self.gui.draw_clicked_box([col, row])

        if self.minefield[row][col].mine:
            if self.view_gui:
                self.gui.draw_mine([col, row])
            self.game_over()
            return
        elif self.minefield[row][col].num_of_surrounding_mines > 0 and self.view_gui:
            self.gui.draw_number_on_box([col, row], self.minefield[row][col].num_of_surrounding_mines)

        # Check surrounding blocks:
        for r in range(row - 1, row + 2):
            for c in range(col - 1, col + 2):
                if r < 0 or r > self.num_of_rows - 1 or c < 0 or c > self.num_of_columns - 1:
                    pass
                else:
                    if self.minefield[row][col].num_of_surrounding_mines == 0:
                        self.left_click_box([c, r])
                    else:
                        self.minefield[row][col].num_of_surrounding_unchecked_boxed -= 1

    def flag_click_box(self, pos):
        col = pos[0]
        row = pos[1]
        if self.minefield[row][col].locked:
            return
        if self.minefield[row][col].flag:
            if self.view_gui:
                self.gui.draw_normal_box([col, row])

            self.minefield[row][col].flag = False
            self.minefield[row][col].clicked = False
            self.num_of_flags_placed -= 1
            if self.minefield[row][col].mine:
                self.num_of_correctly_placed_flags -= 1
            else:
                self.num_of_wrongly_placed_flags -= 1
        else:
            if self.view_gui:
                self.gui.draw_flag_on_box([col, row])

            self.minefield[row][col].flag = True
            self.minefield[row][col].clicked = True
            self.num_of_flags_placed += 1
            if self.minefield[row][col].mine:
                self.num_of_correctly_placed_flags += 1
            else:
                self.num_of_wrongly_placed_flags += 1
        if self.view_gui:
            self.gui.draw_update_flag_counter(self.num_of_flags_placed)

    def convert_pos_to_indices(self, pos):
        row = int(pos[0] / GameUI.BOX_WIDTH)
        col = int((pos[1] - self.gui.top_space) / GameUI.BOX_HEIGHT)
        return [row, col]

    def pressed_smiley(self, pos):
        if self.gui.img_smiley_new_game.get_rect(
                topleft=(self.gui.get_smiley_location(self.gui.img_smiley_new_game))).collidepoint(pos):
            self.create_new_game()

    def check_if_game_is_won(self):
        for row in range(0, self.num_of_rows):
            for col in range(0, self.num_of_columns):
                if not self.minefield[row][col].clicked and not self.minefield[row][col].mine:
                    return
                elif self.minefield[row][col].flag and not self.minefield[row][col].mine:
                    return
        self.game_won()

    def run(self, autorun=False):
        while True:
            if self.new_game:
                self.new_game = False

            if autorun:
                row, col = rand.randint(0, self.num_of_rows - 1), rand.randint(0, self.num_of_columns - 1)
                action = rand.randint(0, 1)
                print("Action: {}".format(action))
                if action == 0:
                    self.left_click_box([col, row])
                elif action == 1:
                    self.flag_click_box([col, row])
                self.gui.update_display()

            elif not autorun and self.view_gui:
                res = self.gui.run()
                pos = [res[0], res[1]]
                action = res[2]
                if pos[1] >= self.gui.top_space:
                    pos = self.convert_pos_to_indices(pos=pos)
                    if action == 1:
                        self.left_click_box(pos=pos)
                    elif action == 3:
                        self.flag_click_box(pos=pos)
                elif self.pressed_smiley(pos):
                    self.create_new_game()
            elif not autorun and not self.view_gui:
                # Not relevant
                pass
            self.check_if_game_is_won()


if __name__ == '__main__':
    r = 25
    c = 30
    gui = True
    ar = False

    MS = MineSweeper(rows=r, columns=c, view_gui=gui)
    MS.run(autorun=ar)

# Kevin Pham
# FALL 2018 32A.
# Hermans
import os
import random
from enum import Enum
import sys
import pygame


class Settings:
    background_color = (255, 255, 255)
    line_color = (180, 180, 180)
    alpha = 128
    row_count = 12
    column_count = 6
    square_width = 48
    space = 2
    move_distance = 16
    game_speed = 10


class Mode(Enum):
    FALLING = 1,
    FREEZING = 2
    MATCHING = 3,
    DISAPPEARING = 4,
    CLEANING_MATCH = 5,
    SHOW_FINISHED = 6,
    FINISHED = 6


class Triple:
    def __init__(self, number_of_squares):
        self.column = 2

        self.squares = []
        for i in range(3):
            self.squares.append(random.randint(0, number_of_squares - 1))

        self.left = (2 * Settings.square_width + 2 * Settings.space)
        self.top = -(3 * Settings.square_width + 3 * Settings.space)
        self.height = self.top * -1

        self.completely_visible = False

    def down(self, dist):
        self.top += min(Settings.move_distance, dist)

    def rotate(self):
        bottom_square = self.squares[2]
        self.squares[2] = self.squares[1]
        self.squares[1] = self.squares[0]
        self.squares[0] = bottom_square

    @staticmethod
    def top_free(table, c):
        for i in range(Settings.row_count):
            if table[i][c] != -1:
                return i * Settings.square_width + (i + 1) * Settings.space + Settings.move_distance

        return Settings.row_count * Settings.square_width + (Settings.row_count + 1) * Settings.space + Settings.move_distance

    def go_left(self, table):

        print(self.top_free(table, self.column - 1), self.top + self.height)

        if self.column > 0 and self.top_free(table, self.column - 1) >= self.top + self.height:
            self.column -= 1
            self.left -= Settings.square_width + Settings.space

    def go_right(self, table):
        if self.column + 1 < Settings.column_count and self.top_free(table, self.column + 1) >= self.top + self.height:
            self.column += 1
            self.left += Settings.square_width + Settings.space


class Game:
    def __init__(self):
        self.mode = Mode.FALLING
        self.squares = []
        self.squares_trans = []
        self.table = []
        self.screen = None
        self.clock = None
        self.prepare()

    def prepare_table(self):
        for i in range(Settings.row_count):
            this_row = []
            for j in range(Settings.column_count):
                this_row.append(-1)
            self.table.append(this_row)

    def update_table(self, triple):
        top_row = self.get_top_row(triple.column) - 2
        for i in range(len(triple.squares)):
            if top_row >= 0:
                self.table[top_row][triple.column] = triple.squares[i]
            top_row += 1

    @staticmethod
    def get_transparent(image):
        image.fill((255, 255, 255, Settings.alpha), None, pygame.BLEND_RGBA_MULT)
        return image

    def prepare_squares(self):
        self.squares.append(self.get_image("sq_blue.png"))
        self.squares.append(self.get_image("sq_brown.png"))
        self.squares.append(self.get_image("sq_green.png"))
        self.squares.append(self.get_image("sq_purple.png"))
        self.squares.append(self.get_image("sq_red.png"))
        self.squares.append(self.get_image("sq_yellow.png"))

        self.squares_trans.append(self.get_transparent(self.get_image("sq_blue.png")))
        self.squares_trans.append(self.get_transparent(self.get_image("sq_brown.png")))
        self.squares_trans.append(self.get_transparent(self.get_image("sq_green.png")))
        self.squares_trans.append(self.get_transparent(self.get_image("sq_purple.png")))
        self.squares_trans.append(self.get_transparent(self.get_image("sq_red.png")))
        self.squares_trans.append(self.get_transparent(self.get_image("sq_yellow.png")))

    def prepare(self):
        self.prepare_table()
        self.prepare_squares()

    @staticmethod
    def get_image(path):
        canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
        image = pygame.image.load(canonicalized_path)
        return image

    @staticmethod
    def get_window_width():
        return Settings.column_count * Settings.square_width + (Settings.column_count + 1) * Settings.space

    @staticmethod
    def get_window_height():
        return Settings.row_count * Settings.square_width + (Settings.row_count + 1) * Settings.space

    @staticmethod
    def get_window_size():
        return Game.get_window_width(), Game.get_window_height()

    def draw_lines(self):
        w1, h1 = 0, 0
        for j in range(Settings.column_count + 1):
            pygame.draw.rect(self.screen, Settings.line_color, (w1, h1, Settings.space, self.get_window_height()))
            w1 += Settings.square_width + Settings.space

        w1, h1 = 0, 0
        for i in range(Settings.row_count + 1):
            pygame.draw.rect(self.screen, Settings.line_color, (w1, h1, self.get_window_width(), Settings.space))
            h1 += Settings.square_width + Settings.space

    def draw_triple(self, triple):
        for i in range(3):
            self.screen.blit(self.squares[triple.squares[i]],
                             (triple.left + Settings.space, triple.top + Settings.space + (i * (Settings.square_width + Settings.space))))

    def get_full_distance(self, triple):
        row = self.get_top_row(triple.column) + 1
        return row * Settings.square_width + row * Settings.space

    def get_top_row(self, column):
        row = Settings.row_count - 1

        while row >= 0:
            if self.table[row][column] != -1:
                row -= 1
            else:
                break

        return row

    @staticmethod
    def is_in_range(xx, cnt):
        return 0 <= xx < cnt

    def match_exist(self):

        directions = [(0, 1), (1, 0), (1, 1), (-1, 1)]

        for i in range(Settings.row_count):
            for j in range(Settings.column_count):

                for direct in directions:
                    all_colors = set()
                    for k in range(3):
                        rr = i + k * direct[0]
                        cc = j + k * direct[1]

                        if self.is_in_range(rr, Settings.row_count) and self.is_in_range(cc, Settings.column_count):
                            all_colors.add(self.table[rr][cc])
                        else:
                            all_colors.add(-1)
                            break

                    if -1 not in all_colors and len(all_colors) == 1:
                        return True

        return False

    def get_square(self, rr, cc):
        if self.table[rr][cc] >= 100:
            return self.squares_trans[self.table[rr][cc] - 100]
        else:
            return self.squares[self.table[rr][cc]]

    def draw_squares(self):

        for i in range(Settings.row_count):
            for j in range(Settings.column_count):
                if self.table[i][j] != -1:
                    self.screen.blit(self.get_square(i, j),
                                     ((j + 1) * Settings.space + j * Settings.square_width,
                                      (i + 1) * Settings.space + i * Settings.square_width))

    def do_show_finished(self):
        pygame.draw.rect(self.screen, Settings.line_color,
                         (0, self.get_window_height() / 3, self.get_window_width(), self.get_window_height() / 3))

        font = pygame.font.SysFont("comicsansms", 40)
        finished_message = font.render("Finished", True, (0, 0, 0))
        self.screen.blit(finished_message, (self.get_window_width() / 4, self.get_window_height() / 2))

    def do_clean_match(self):
        for j in range(Settings.column_count):
            for i in range(Settings.row_count - 1):
                if self.table[i + 1][j] == -1 and self.table[i][j] != -1:

                    rr = i + 1
                    while rr < Settings.row_count:
                        if self.table[rr][j] == -1:
                            rr += 1
                        else:
                            break

                    rr -= 1
                    while rr > 0:
                        self.table[rr][j] = self.table[rr - 1][j]
                        rr -= 1

    def do_disappear(self):
        for i in range(Settings.row_count):
            for j in range(Settings.column_count):
                if self.table[i][j] >= 100:
                    self.table[i][j] = -1

    def do_match(self):
        directions = [(0, 1), (1, 0), (1, 1), (-1, 1),
                      (0, -1), (-1, 0), (-1, -1), (1, -1)]

        is_matched = []
        for i in range(Settings.row_count):
            is_matched.append([False] * Settings.column_count)

        for i in range(Settings.row_count):
            for j in range(Settings.column_count):

                for direct in directions:
                    all_colors = set()
                    for k in range(3):
                        rr = i + k * direct[0]
                        cc = j + k * direct[1]

                        if self.is_in_range(rr, Settings.row_count) and self.is_in_range(cc, Settings.column_count):
                            all_colors.add(self.table[rr][cc])
                        else:
                            all_colors.add(-1)
                            break

                    if -1 not in all_colors and len(all_colors) == 1:
                        for k in range(3):
                            rr = i + k * direct[0]
                            cc = j + k * direct[1]
                            is_matched[rr][cc] = True
                        break

        for i in range(Settings.row_count):
            for j in range(Settings.column_count):
                if is_matched[i][j]:
                    self.table[i][j] += 100

    def run(self):
        print(self.get_window_size())

        pygame.init()
        self.screen = pygame.display.set_mode(self.get_window_size())
        self.clock = pygame.time.Clock()
        pygame.display.set_caption('Kevins Columns')

        triple = Triple(len(self.squares))

        while self.mode != Mode.FINISHED:

            self.screen.fill(Settings.background_color)
            self.draw_lines()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.mode = Mode.FINISHED
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        triple.rotate()
                    elif event.key == pygame.K_LEFT:
                        triple.go_left(self.table)
                    elif event.key == pygame.K_RIGHT:
                        triple.go_right(self.table)
                    elif event.key == pygame.K_q:
                        self.mode = Mode.FINISHED
                        exit()
                        break

            if self.mode == Mode.FALLING:
                full_distance = self.get_full_distance(triple)
                remaining_distance = full_distance - triple.top - triple.height
                print("remaining_distance", remaining_distance, triple.top)

                if remaining_distance == 0:
                    if triple.top < 0:
                        print("finished", triple.top)
                        self.mode = Mode.SHOW_FINISHED
                        self.update_table(triple)
                    else:
                        self.mode = Mode.FREEZING
                        self.update_table(triple)
                else:
                    triple.down(remaining_distance)
                    self.draw_triple(triple)
            elif self.mode == Mode.FREEZING:

                if self.match_exist():
                    self.mode = Mode.MATCHING
                else:
                    self.mode = Mode.FALLING
                    triple = Triple(len(self.squares))

            elif self.mode == Mode.MATCHING:

                if not self.match_exist():
                    self.mode = Mode.FALLING
                    triple = Triple(len(self.squares))
                else:
                    self.do_match()
                    self.mode = Mode.DISAPPEARING

            elif self.mode == Mode.DISAPPEARING:
                self.do_disappear()
                self.mode = Mode.CLEANING_MATCH
            elif self.mode == Mode.CLEANING_MATCH:
                self.do_clean_match()
                self.mode = Mode.MATCHING

            self.draw_squares()
            if self.mode == Mode.SHOW_FINISHED:
                self.do_show_finished()

            pygame.display.flip()
            self.clock.tick(Settings.game_speed)


game = Game()
game.run()

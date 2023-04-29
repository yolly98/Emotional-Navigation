import pygame
import math


class PathProgress:

    def __init__(self, pos_x, pos_y, block_size, length_m):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.width = 4
        self.height = 26
        self.length_m = length_m
        self.residual_m = 0

    def set_residual_m(self, residual_m):
        self.residual_m = residual_m

    def get_pos_x(self):
        return self.pos_x

    def get_pos_y(self):
        return self.pos_y

    def set_pos_x(self, pos_X):
        self.pos_x = pos_X

    def set_pos_y(self, pos_y):
        self.pos_y = pos_y

    def get_block_size(self):
        return self.block_size

    def set_block_size(self, block_size):
        self.block_size = block_size

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def draw(self, win, colors, travelled_m):

        travelled_m = travelled_m + self.residual_m
        pos_x = self.pos_x
        pos_y = self.pos_y
        block_size = self.block_size
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                color = None
                if i == self.height - 1 or i == 0 or j == 0 or j == self.width - 1:
                    color = colors['white']
                else:
                    progress = math.floor(((self.height - 2) * travelled_m) / self.length_m)
                    if i > (self.height - 2 - progress):
                        color = colors['green']
                    else:
                        color = colors['white']
                pygame.draw.rect(win, color,
                                 pygame.Rect(pos_x + j * block_size, pos_y + i * block_size, block_size, block_size))
                j += 1
            i += 1


import pygame


class Alert:
    def __init__(self, pos_x, pos_y, block_size, primary_color, background_color):

        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.width = 13
        self.height = 11
        self.primary_color = primary_color,
        self.background_color = background_color
        self.alert_body = [[0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0],
                           [0, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0],
                           [0, 0, 1, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0],
                           [0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0],
                           [0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                           [0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0],
                           [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                           [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                           ]

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def set_color(self, color):
        self.primary_color = color

    def draw(self, win):
        pos_x = self.pos_x
        pos_y = self.pos_y
        block_size = self.block_size
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                color = None
                block = self.alert_body[i][j]
                if block == 1:
                    color = self.primary_color
                elif block == 0:
                    color = self.background_color
                pygame.draw.rect(win, color,
                                 pygame.Rect(pos_x + j * block_size, pos_y + i * block_size, block_size,
                                             block_size))
                j += 1
            i += 1
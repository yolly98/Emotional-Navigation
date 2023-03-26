import pygame


class Arrow:
    def __init__(self, pos_x, pos_y, block_size, speed, type, primary_color, background_color):
        self.speed = speed
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.width = 13
        self.height = 11
        self.speed_counter = speed
        self.arrow_body = None
        self.set_type(type)
        self.primary_color = primary_color
        self.background_color = background_color
        self.is_showed = False

    def get_width(self):
        return self.width

    def get_height(self):
        return self.height

    def get_speed(self):
        return self.speed

    def get_color(self):
        return self.primary_color

    def set_color(self, color):
        self.primary_color = color

    def get_showed(self):
        return self.is_showed

    def hide(self):
        self.is_showed = False

    def get_type(self):
        return self.type

    def set_type(self, type):
        self.type = type
        if type == 'right':
            self.arrow_body = [[0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
                               ]
        else:
            self.arrow_body = [[0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                               [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                               [0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                               ]

    def set_speed(self, speed):
        if self.speed == speed:
            return
        self.speed = speed
        self.speed_counter = speed

    def draw(self, win):
        self.is_showed = True
        if self.speed is not None:
            self.speed_counter -= 1
            if self.speed_counter < 0:
                if self.speed_counter <= - self.speed:
                    self.speed_counter = self.speed
                return
        pos_x = self.pos_x
        pos_y = self.pos_y
        block_size = self.block_size
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                color = None
                block = self.arrow_body[i][j]
                if block == 1:
                    color = self.primary_color
                elif block == 0:
                    color = self.background_color
                pygame.draw.rect(win, color,
                                 pygame.Rect(pos_x + j * block_size, pos_y + i * block_size, block_size, block_size))
                j += 1
            i += 1

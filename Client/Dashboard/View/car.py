import pygame


class Car:

    def __init__(self, pos_x, pos_y, block_size, max_car_speed, type):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.max_car_speed = max_car_speed
        self.car_speed = 0
        self.width = 10
        self.height = 7
        if type == 'back_car' or type == 'player':
            self.car_body = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                             [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
                             [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                             [1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
                             [1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
                             [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                             [0, 1, 1, 0, 0, 0, 0, 1, 1, 0]]
        else:
            self.car_body = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                         [0, 1, 1, 0, 0, 0, 0, 1, 1, 0],
                         [0, 1, 0, 0, 0, 0, 0, 0, 1, 0],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [1, 1, 2, 1, 1, 1, 1, 2, 1, 1],
                         [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                         [0, 1, 1, 0, 0, 0, 0, 1, 1, 0]]

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

    def get_speed(self):
        return self.car_speed

    def set_speed(self, speed):
        self.car_speed = speed

    def move_car(self, commands):
        up = commands['up']
        down = commands['down']

        if up:
            if self.car_speed < self.max_car_speed:
                self.car_speed += 0.5
            else:
                self.car_speed = self.max_car_speed
        if down:
            if self.car_speed > 0:
                self.car_speed -= 0.5
            else:
                self.car_speed = 0

    def draw(self, win, colors):
        black = colors['black']
        white = colors['white']
        red = colors['red']
        pos_x = self.pos_x
        pos_y = self.pos_y
        block_size = self.block_size
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                color = None
                block = self.car_body[i][j]
                if block == 1:
                    color = white
                elif block == 0:
                    color = black
                elif block == 2:
                    color = red
                pygame.draw.rect(win, color,
                                 pygame.Rect(pos_x+j*block_size, pos_y+i*block_size, block_size,  block_size))
                j += 1
            i += 1

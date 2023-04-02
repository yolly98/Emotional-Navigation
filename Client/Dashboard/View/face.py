import pygame


class Face:

    def __init__(self, pos_x, pos_y, block_size, type):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.car_speed = 0
        self.width = 10
        self.height = 10
        if type == 'happy' or type == 'surprise':
            self.face_body = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
                              [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [0, 0, 1, 1, 1, 1, 1, 1, 0, 0]]
        elif type == 'sad' or type == 'angry' or type == 'fear' or type == 'disgust':
            self.face_body = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 0, 0, 0, 0, 1, 1, 1],
                              [1, 1, 0, 1, 1, 1, 1, 0, 1, 1],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [0, 0, 1, 1, 1, 1, 1, 1, 0, 0]]
        else: # neutral
            self.face_body = [[0, 0, 1, 1, 1, 1, 1, 1, 0, 0],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 0, 1, 1, 0, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
                              [1, 1, 0, 0, 0, 0, 0, 0, 1, 1],
                              [0, 1, 1, 1, 1, 1, 1, 1, 1, 0],
                              [0, 0, 1, 1, 1, 1, 1, 1, 0, 0]]

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

    def draw(self, win, colors):
        black = colors['black']
        white = colors['white']
        pos_x = self.pos_x
        pos_y = self.pos_y
        block_size = self.block_size
        i = 0
        while i < self.height:
            j = 0
            while j < self.width:
                color = None
                block = self.face_body[i][j]
                if block == 1:
                    color = white
                elif block == 0:
                    color = black
                pygame.draw.rect(win, color,
                                 pygame.Rect(pos_x+j*block_size, pos_y+i*block_size, block_size,  block_size))
                j += 1
            i += 1

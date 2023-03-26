import pygame
import pygame_textinput
import math

class Terminal:

    def __init__(self, pos_x, pos_y, height, font_size, colors):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.height = height
        self.rows = []
        self.font_size = font_size
        self.colors = colors
        n_rows = math.floor((height / font_size)) - 2
        for i in range(n_rows):
            self.rows.append(f"row {i}")

        font = pygame.font.SysFont('times new roman', font_size)
        self.input = pygame_textinput.TextInputVisualizer(font_object=font)
        self.input.font_color = colors['green']
        self.input.value = "value"
        self.input.cursor_color = (0, 85, 170)
        self.input.cursor_blink_interval = 200
        self.input.cursor_width = 2

    def scroll(self):

        i = len(self.rows) - 1
        while i > 0:
            self.rows[i] = self.rows[i-1]
            i -= 1
        self.rows[0] = self.input.value
        command = self.input.value
        self.input.value = ""
        return command

    def write(self, events):
        self.input.update(events)

    def draw(self, win):

        i = len(self.rows) - 1
        font = pygame.font.SysFont('times new roman', self.font_size)
        while i >= 0:
            row = font.render(self.rows[i], True, self.colors['green'])
            row_rect = row.get_rect()
            row_rect.midleft = (self.pos_x + 10, self.pos_y + ((len(self.rows) - i) * self.font_size))
            win.blit(row, row_rect)
            i -= 1

        win.blit(self.input.surface, (self.pos_x + 10, self.pos_y + ((len(self.rows) + 1) * self.font_size) - 2))
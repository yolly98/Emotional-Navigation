import pygame
import sys
import math
from Core.map_engine import MapEngine
from Utility.utility import Point
import time


class PathProgress:

    def __init__(self, pos_x, pos_y, block_size, length_m):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.block_size = block_size
        self.width = 4
        self.height = 26
        self.length_m = length_m

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
                                 pygame.Rect(pos_x + j * block_size, pos_y + i * block_size, block_size,
                                             block_size))
                j += 1
            i += 1


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

    def move_car(self, commands, street_width):
        up = commands['up']
        down = commands['down']
        left = commands['left']
        right = commands['right']

        if up:
            #if self.car_position[1] % 20 == 0:
            #    self.car_block_size -= self.prospective_car_step
            #self.car_position[1] -= self.block_size
            if self.car_speed < self.max_car_speed:
                self.car_speed += 0.5
            else:
                self.car_speed = self.max_car_speed
        if down:
            #if self.car_position[1] % 20 == 0:
            #    self.car_block_size += self.prospective_car_step
            #self.car_position[1] += self.block_size
            if self.car_speed > 0:
                self.car_speed -= 0.5
            else:
                self.car_speed = 0
        if left:
            if self.pos_x > street_width / 2:
                self.pos_x -= self.car_speed / 10
        if right:
            if self.pos_x + self.width * self.block_size < street_width:
                self.pos_x += self.car_speed / 10

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


class DrivingSimulator:

    driving_simulator = None

    def __init__(self):
        # pygame initialization
        pygame.init()

        # set width and height of the window
        self.win_width = 800
        self.win_height = 600

        # create the window
        self.win = pygame.display.set_mode((self.win_width, self.win_height))

        # set window title
        pygame.display.set_caption('Smart Navigation')

        # get the clock to manage the frame rate
        self.clock = pygame.time.Clock()
        self.update_win_rate = 60

        # set block dimension (is the 'pixel' of the simulation)
        self.block_size = 10

        # define colors
        self.colors = dict()
        self.colors['black'] = (0, 0, 0)
        self.colors['white'] = (255, 255, 255)
        self.colors['red'] = (255, 0, 0)
        self.colors['green'] = (0, 255, 0)
        self.colors['blue'] = (0, 0, 255)
        self.colors['yellow'] = (254, 221, 0)

        self.prospective_street_step = 0.1
        self.prospective_car_step = 1
        self.commands = dict()
        self.commands['up'] = False
        self.commands['down'] = False
        self.commands['left'] = False
        self.commands['right'] = False

        self.street_lines = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        self.max_car_speed = 200
        self.car_speed_counter = 0
        self.street_width = self.win_height
        self.street_height = self.win_height - (self.win_height / 3)
        self.street_pos = [0, self.win_height / 3]
        self.player_car = Car(self.win_height - 250, self.win_height - 100, self.block_size, self.max_car_speed, 'player')
        self.path = None
        self.path_km = 0
        self.old_car_speed = 0
        self.old_timestamp = None
        self.start_time = None
        self.travel_time = None
        self.alert = Alert(10, 100, 5, self.colors['white'], self.colors['black'])
        self.arrow = Arrow(270, 100, 5, None, 'right', self.colors['white'], self.colors['black'])
        self.actual_street = None
        self.path_progress = None

    def get_path(self):
        # simulation
        source = Point('42.3333569', '12.2692692')
        destination = Point('42.3295099', '12.2659779')
        self.path = MapEngine.calculate_path(source, destination)['path']
        MapEngine.print_path(self.path)
        self.old_timestamp = time.time()
        self.old_car_speed = 0
        self.start_time = time.time()
        self.travel_time = 0
        path_length = 0
        for way in self.path:
            path_length += way['length']
        self.path_progress = PathProgress(self.street_width + (self.win_width - self.street_width - 30)/2, self.street_pos[1], self.block_size, path_length)

    def show(self):
        self.win.fill(pygame.Color(self.colors['black']))

        self.draw_street()
        self.player_car.draw(self.win, self.colors)

        # draw sections
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, 0, self.block_size, self.block_size * self.win_height))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, self.win_height - 100, self.block_size * 200, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_pos[0], self.street_pos[1], self.street_width, self.block_size / 2))

        font = pygame.font.SysFont('times new roman', 25)

        # draw car speed
        speed = self.player_car.get_speed()
        speed_surface = font.render(f"{math.floor(speed)} km/h", True, self.colors['white'])
        speed_rect = speed_surface.get_rect()
        speed_rect.midright = (self.win_width - 50, self.win_height - 50)
        self.win.blit(speed_surface, speed_rect)

        # draw m traveled
        t = time.time() - self.old_timestamp
        avg_speed = (self.player_car.get_speed() + self.old_car_speed) / 2
        traveled_km = (avg_speed / 3600) * t
        self.path_km += traveled_km
        self.old_timestamp = time.time()
        self.old_car_speed = self.player_car.get_speed()
        km_surface = font.render(f"{math.floor(self.path_km * 1000)} m", True, self.colors['white'])
        km_rect = km_surface.get_rect()
        km_rect.midtop = (self.street_width / 2, 50)
        self.win.blit(km_surface, km_rect)
        self.path_progress.draw(self.win, self.colors, math.floor(self.path_km * 1000))

        # draw street name
        actual_street = None
        traveled_m = (self.path_km * 1000)
        for street in self.path:
            if traveled_m < street['length']:
                actual_street = street
                break
            else:
                traveled_m -= street['length']
        if actual_street is None:
            if self.travel_time == 0:
                self.travel_time = time.time() - self.start_time
            message = f"destination reached in {math.floor(self.travel_time / 60)} min {math.floor(self.travel_time % 60)} sec"
            street_surface = font.render(message, True, self.colors['white'])
            self.end = True
        else:
            message = f"{actual_street['name']} ({actual_street['ref']}) lim: {actual_street['speed']} km/h"
            street_surface = font.render(message, True, self.colors['white'])
        street_rect = street_surface.get_rect()
        street_rect.midtop = (self.street_width / 2, 10)
        self.win.blit(street_surface, street_rect)
        if not actual_street == self.actual_street:
            self.actual_street = actual_street
            self.arrow.set_color(self.colors['white'])

        # draw arrow
        if (actual_street is not None) and (actual_street['length'] - traveled_m < 200):
            if actual_street['length'] - traveled_m <= 50:
                self.arrow.set_speed(5)
            elif actual_street['length'] - traveled_m <= 100:
                self.arrow.set_speed(10)
            else:
                self.arrow.set_speed(None)
            if len(actual_street['name']) % 2 == 0:
                self.arrow.set_type('right')
            else:
                self.arrow.set_type('left')
            self.arrow.draw(self.win)
        else:
            self.arrow.hide()
            self.arrow.set_color(self.colors['white'])

        # draw alert
        if (actual_street is not None) and (self.player_car.get_speed() > actual_street['speed']):
            self.alert.draw(self.win)

        pygame.display.flip()

    def draw_street(self):
        max_height = self.win_height / 3
        i = 0
        block_size = self.block_size
        line_width = block_size
        line_height = block_size*2
        step = line_width / len(self.street_lines)

        car_speed = self.player_car.get_speed()
        # print central lines
        if self.car_speed_counter > self.max_car_speed:
            self.street_lines = self.street_lines[1:] + self.street_lines[:1]
            self.car_speed_counter = 0
        else:
            self.car_speed_counter += car_speed
        while i < len(self.street_lines):
            if self.street_lines[i] == 1:
                pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width / 2, self.win_height - i*line_height, line_width - step, line_height))
            i += 1
            step += (line_width / len(self.street_lines))

        # print street edges
        i = self.win_height
        j = 0
        k = 0
        max_k = 1
        step = self.prospective_street_step
        while i > max_height:
            pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(j, i, block_size - step, block_size - step))
            pygame.draw.rect(self.win, self.colors['white'], pygame.Rect((self.win_height - j), i, block_size - step, block_size - step))

            i -= step
            k += 1
            if k > max_k:
                k = 0
                j += step
            step += self.prospective_street_step

    def wait(self):
        self.clock.tick(self.update_win_rate)

    def get_event(self):

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.commands['up'] = True
                if event.key == pygame.K_DOWN:
                    self.commands['down'] = True
                if event.key == pygame.K_LEFT:
                    if self.arrow.get_showed():
                        if self.arrow.get_color() == self.colors['white']:
                            if self.arrow.get_type() == "left":
                                self.arrow.set_color(self.colors['green'])
                            else:
                                self.arrow.set_color(self.colors['red'])
                    # else:
                    #    self.commands['left'] = True
                if event.key == pygame.K_RIGHT:
                    if self.arrow.get_showed():
                        if self.arrow.get_color() == self.colors['white']:
                            if self.arrow.get_type() == "right":
                                self.arrow.set_color(self.colors['green'])
                            else:
                                self.arrow.set_color(self.colors['red'])
                    # else:
                    #    self.commands['right'] = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.commands['up'] = False
                if event.key == pygame.K_DOWN:
                    self.commands['down'] = False
                if event.key == pygame.K_LEFT:
                    self.commands['left'] = False
                if event.key == pygame.K_RIGHT:
                    self.commands['right'] = False

        self.player_car.move_car(self.commands, self.street_width)

    @staticmethod
    def get_instance():
        if DrivingSimulator.driving_simulator is None:
            DrivingSimulator.driving_simulator = DrivingSimulator()
        return DrivingSimulator.driving_simulator


if __name__ == '__main__':

    sim = DrivingSimulator.get_instance()
    sim.get_path()
    while True:
        sim.get_event()
        sim.show()
        sim.wait()




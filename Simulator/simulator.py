import pygame
import pygame_textinput
import sys
import math
from Core.map_engine import MapEngine
from Persistence.map_sql_manager import MapSqlManager
from Utility.utility import Point, calculate_distance
from InputModule.gps_simulator import GPS
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
                                 pygame.Rect(pos_x + j * block_size, pos_y + i * block_size, block_size, block_size))
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


class DrivingSimulator:

    driving_simulator = None

    def __init__(self):

        self.sim = True

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
        self.textinput = pygame_textinput.TextInputVisualizer(font_object=pygame.font.SysFont('times new roman', 20))
        self.textinput.font_color = (0, 85, 170)
        self.textinput.value = "Insert Destination"
        self.textinput.cursor_color = (0, 85, 170)
        self.textinput.cursor_blink_interval = 200
        self.textinput.cursor_width = 2
        self.input_enabler = True
        self.button = pygame.Rect(self.street_width + 20, 50, 100, 20)

    def set_sim(self, simulation):
        self.sim = simulation

    def end_path(self):
        self.path = None
        self.path_km = 0
        self.old_car_speed = 0
        self.old_timestamp = None
        self.start_time = None
        self.travel_time = None
        self.path_progress = None
        self.input_enabler = True
        self.car_speed_counter = 0
        self.textinput.value = "Insert Destination"

    def get_path(self, destination_name):

        source = GPS.get_instance().get_coord(True, -1)
        # get destination from input
        sql_map = MapSqlManager.get_instance()
        sql_map.open_connection()
        ways = sql_map.get_way_by_name(destination_name)
        if not ways:
            self.textinput.value = "Not valid destination"
            return
        way = ways[0]
        destination_node = sql_map.get_node(way.get('start_node'))
        destination = Point(destination_node.get('lat'), destination_node.get('lon'))
        sql_map.close_connection()

        self.path = MapEngine.calculate_path(source, destination)
        if self.path is None:
            print("Path not found")
            return False
        GPS.get_instance().set_path(self.path)
        MapEngine.print_path(self.path)
        self.old_timestamp = time.time()
        self.old_car_speed = 0
        self.start_time = time.time()
        self.travel_time = 0
        path_length = 0
        for way in self.path:
            path_length += way['way'].get('length')
        self.path_progress = PathProgress(self.street_width + (self.win_width - self.street_width - 30)/2, self.street_pos[1], self.block_size, path_length)
        self.input_enabler = False

    def show(self):
        self.win.fill(pygame.Color(self.colors['black']))

        self.draw_street()
        self.player_car.draw(self.win, self.colors)

        # draw sections
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, 0, self.block_size, self.block_size * self.win_height))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, self.win_height - 100, self.block_size * 200, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_pos[0], self.street_pos[1], self.street_width, self.block_size / 2))

        # draw inputs
        if self.input_enabler:
            self.win.blit(self.textinput.surface, (self.street_width + 20, 10))
            pygame.draw.rect(self.win, self.colors['blue'], self.button)
            font = pygame.font.SysFont('times new roman', 20)
            text_surface = font.render('SUBMIT', True, (255, 255, 255))
            self.win.blit(text_surface, (self.button.x + (self.button.width - text_surface.get_width()) // 2,
                                       self.button.y + (self.button.height - text_surface.get_height()) // 2))

        font = pygame.font.SysFont('times new roman', 25)

        # draw m traveled
        if self.path is not None:
            # needed for simulation
            if self.sim:
                t = time.time() - self.old_timestamp
                avg_speed = (self.player_car.get_speed() + self.old_car_speed) / 2
                traveled_km = (avg_speed / 3600) * t
                self.path_km += traveled_km
                self.old_timestamp = time.time()
                self.old_car_speed = self.player_car.get_speed()
            # ------

            # get gps position
            position = GPS.get_instance().get_coord(self.sim, self.path_km)
            if not self.sim:
                self.player_car.set_speed(GPS.get_instance().get_speed())

            km_surface = font.render(f"{math.floor(self.path_km * 1000)} m", True, self.colors['white'])
            km_rect = km_surface.get_rect()
            km_rect.midtop = (self.street_width / 2, 50)
            self.win.blit(km_surface, km_rect)
            self.path_progress.draw(self.win, self.colors, math.floor(self.path_km * 1000))

            actual_street = None
            if position is None:
                print("GPS coordinates not found")
            else:
                # get street name
                distance = None
                nearest_point_index = 0
                i = 0
                while i < len(self.path):
                    node = self.path[i]['start_node']
                    p = Point(node.get('lat'), node.get('lon'))
                    d = calculate_distance(position, p)
                    if distance is None or distance > d:
                        nearest_point_index = i
                        distance = d
                    i += 1

                actual_street = self.path[nearest_point_index]

            # draw street name
            if actual_street is None:
                if self.travel_time == 0:
                    self.travel_time = time.time() - self.start_time
                message = f"destination reached in {math.floor(self.travel_time / 60)} min {math.floor(self.travel_time % 60)} sec"
                street_surface = font.render(message, True, self.colors['white'])
                self.end_path()
            else:
                message = f"{actual_street['way'].get('name')} ({actual_street['way'].get('ref')}) lim: {actual_street['way'].get('speed')} km/h"
                street_surface = font.render(message, True, self.colors['white'])
            street_rect = street_surface.get_rect()
            street_rect.midtop = (self.street_width / 2, 10)
            self.win.blit(street_surface, street_rect)

            if (actual_street is None or self.actual_street is None) or (not actual_street['way'].get('name') == self.actual_street['way'].get('name')):
                self.arrow.set_color(self.colors['white'])
            self.actual_street = actual_street

            # draw arrow
            if (actual_street is not None) and (not self.path.index(actual_street) == len(self.path) - 1):

                i = 0
                ms = 0
                while i < len(self.path):
                    street = self.path[i]
                    if i < self.path.index(actual_street) or street['way'].get('name') == actual_street['way'].get('name'):
                        ms += street['way'].get('length')
                    else:
                        break
                    i += 1

                # calculate arrow direction
                if i < len(self.path) - 1:
                    lat1 = float(self.path[i-1]['start_node'].get('lat'))
                    lon1 = float(self.path[i-1]['start_node'].get('lon'))
                    lat2 = float(self.path[i - 1]['end_node'].get('lat'))
                    lon2 = float(self.path[i - 1]['end_node'].get('lon'))
                    lat3 = float(self.path[i]['start_node'].get('lat'))
                    lon3 = float(self.path[i]['start_node'].get('lon'))
                    p1 = (lat1, lon1)
                    p2 = (lat2, lon2)
                    p3 = (lat3, lon3)
                    v1 = (p2[0] - p1[0], p2[1] - p1[1])
                    v2 = (p3[0] - p2[0], p3[1] - p2[1])
                    cross_product = v1[0] * v2[1] - v1[1] * v2[0]
                    if cross_product > 0:
                        self.arrow.set_type('right')
                    else:
                        self.arrow.set_type('left')

                traveled_m = self.path_km * 1000
                if ms - traveled_m <= 50:
                    self.arrow.set_speed(5)
                    self.arrow.draw(self.win)
                elif ms - traveled_m <= 100:
                    self.arrow.set_speed(10)
                    self.arrow.draw(self.win)
                elif ms - traveled_m <= 200:
                    self.arrow.set_speed(None)
                    self.arrow.draw(self.win)
                else:
                    self.arrow.hide()
                    self.arrow.set_color(self.colors['white'])
            else:
                self.arrow.hide()
                self.arrow.set_color(self.colors['white'])

            # draw alert
            if (actual_street is not None) and (self.player_car.get_speed() > actual_street['way'].get('speed')):
                self.alert.draw(self.win)

        # draw car speed
        speed = self.player_car.get_speed()
        speed_surface = font.render(f"{math.floor(speed)} km/h", True, self.colors['white'])
        speed_rect = speed_surface.get_rect()
        speed_rect.midright = (self.win_width - 50, self.win_height - 50)
        self.win.blit(speed_surface, speed_rect)

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

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button.collidepoint(event.pos):
                    self.get_path(self.textinput.value)
            if self.input_enabler:
                continue
            else:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.commands['up'] = True
                    if event.key == pygame.K_DOWN:
                        self.commands['down'] = True
                    if event.key == pygame.K_LEFT and self.arrow.get_showed() and self.arrow.get_color() == self.colors['white']:
                        if self.arrow.get_type() == "left" and (self.arrow.get_speed() is not None):
                            self.arrow.set_color(self.colors['green'])
                        else:
                            self.arrow.set_color(self.colors['red'])
                    if event.key == pygame.K_RIGHT and self.arrow.get_showed() and self.arrow.get_color() == self.colors['white']:
                        if self.arrow.get_type() == "right" and (self.arrow.get_speed() is not None):
                            self.arrow.set_color(self.colors['green'])
                        else:
                            self.arrow.set_color(self.colors['red'])
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.commands['up'] = False
                    if event.key == pygame.K_DOWN:
                        self.commands['down'] = False
                    if event.key == pygame.K_LEFT:
                        self.commands['left'] = False
                    if event.key == pygame.K_RIGHT:
                        self.commands['right'] = False

        if self.input_enabler:
            self.textinput.update(events)

        self.player_car.move_car(self.commands)

    @staticmethod
    def get_instance():
        if DrivingSimulator.driving_simulator is None:
            DrivingSimulator.driving_simulator = DrivingSimulator()
        return DrivingSimulator.driving_simulator


if __name__ == '__main__':

    sim = DrivingSimulator.get_instance()
    sim.set_sim(True)
    while True:
        sim.get_event()
        sim.show()
        sim.wait()




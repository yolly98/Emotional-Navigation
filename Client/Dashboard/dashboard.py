import pygame
import sys
import math
from Utility.utility_functions import calculate_distance, print_path, json_to_path
from Utility.point import Point
from Client.InputModule.gps_module import GPS
import time
from Client.Dashboard.View.alert import Alert
from Client.Dashboard.View.path_progress import PathProgress
from Client.Dashboard.View.car import Car
from Client.Dashboard.View.arrow import Arrow
from Client.Dashboard.View.terminal import Terminal
from Client.Dashboard.comunication_manager import CommunicationManager

SERVER_IP = "127.0.0.1"
SERVER_PORT = "5000"


class Dashboard:

    dashboard = None

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
        self.terminal_height = 100
        self.terminal_width = 800
        self.street_width = self.win_width - 200
        self.street_height = self.win_height / 3
        self.street_pos = [0, self.win_height / 3]
        self.player_car = Car(self.street_width - 250, self.win_height - self.terminal_height - 100, self.block_size, self.max_car_speed, 'player')
        self.path = None
        self.path_km = 0
        self.old_car_speed = 0
        self.old_timestamp = None
        self.start_time = None
        self.travel_time = None
        self.alert = Alert(self.street_width - 100, 60, 5, self.colors['white'], self.colors['black'])
        self.arrow = Arrow(270, 60, 5, None, 'right', self.colors['white'], self.colors['black'])
        self.actual_street = None

        self.path_progress = None
        self.terminal = Terminal(0, self.win_height - self.terminal_height, self.terminal_height, 20, self.colors)
        self.terminal.write("Insert Destination")

    @staticmethod
    def get_instance():
        if Dashboard.dashboard is None:
            Dashboard.dashboard = Dashboard()
        return Dashboard.dashboard

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
        self.car_speed_counter = 0
        self.terminal.write("Insert Destination")

    def get_path(self, destination_name):

        request = dict()
        request['type'] = 'get_path'
        request['destination_name'] = destination_name
        request['source_coord'] = (GPS.get_instance().get_coord(self.sim, -1)).to_json()

        res = CommunicationManager.get_instance().send(SERVER_IP, SERVER_PORT, request)
        if res is None or "":
            self.terminal.write("Something went wrong")
            return
        elif res['status'] == 0:
            self.path = json_to_path(res['path'])
        elif res['status'] == -1:
            self.terminal.write("Not valid destination")
            return
        elif res['status'] == -2:
            self.terminal.write("Path not found")
            return
        else:
            self.terminal.write("Something went wrong")
            return

        self.terminal.write("Path found ")
        GPS.get_instance().set_path(self.path)
        msg = print_path(self.path)
        self.terminal.write(f"length:  {msg['len']} km")
        self.terminal.write(f"estimated time: {msg['t_m']} minutes {msg['t_s']} seconds")

        self.old_timestamp = time.time()
        self.old_car_speed = 0
        self.start_time = time.time()
        self.travel_time = 0
        path_length = 0
        for way in self.path:
            path_length += way['way'].get('length')
        self.path_progress = PathProgress(self.street_width + (self.win_width - self.street_width - 30)/2, self.street_pos[1] - 50, self.block_size, path_length)

    def show(self):
        self.win.fill(pygame.Color(self.colors['black']))

        # draw sections
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, 0, self.block_size, self.win_height - self.terminal_height))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, self.win_height - self.terminal_height - 70, self.win_width - self.street_width, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_pos[0], self.street_pos[1] - 50, self.street_width, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(0, self.win_height - self.terminal_height, self.win_width, self.block_size))

        font = pygame.font.SysFont('times new roman', 25)

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

            # draw m travelled
            km_surface = font.render(f"{math.floor(self.path_km * 1000)} m", True, self.colors['white'])
            km_rect = km_surface.get_rect()
            km_rect.midtop = (100, 80)
            self.win.blit(km_surface, km_rect)
            # draw path progress
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
        speed_rect.midright = (self.win_width - 50, self.win_height - self.terminal_height - 25)
        self.win.blit(speed_surface, speed_rect)

        self.draw_street()
        self.player_car.draw(self.win, self.colors)

        self.terminal.draw(self.win)

        pygame.display.flip()

    def draw_street(self):
        max_height = self.street_height
        i = 0
        block_size = self.block_size
        line_width = block_size
        line_height = block_size*2
        step_width = line_width / len(self.street_lines)
        step_height = line_height / len(self.street_lines)

        car_speed = self.player_car.get_speed()
        # print central lines
        if self.car_speed_counter > self.max_car_speed:
            self.street_lines = self.street_lines[1:] + self.street_lines[:1]
            self.car_speed_counter = 0
        else:
            self.car_speed_counter += car_speed
        while i < len(self.street_lines):
            if self.street_lines[i] == 1:
                width = line_width - step_width
                height = line_height - step_height
                x = self.street_width / 2 - width / 2
                y = self.win_height - self.terminal_height - (i + 1) * 1.6 * line_height + (i - 1) * step_height
                pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(x, y, width, height))
            i += 1
            step_width += line_width / len(self.street_lines)
            step_height += line_height / len(self.street_lines)

        # print street edges
        i = self.win_height - self.terminal_height
        j = 0
        k = 0
        max_k = 1
        step = self.prospective_street_step
        while i > max_height:
            pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(j, i, block_size - step, block_size - step))
            pygame.draw.rect(self.win, self.colors['white'], pygame.Rect((self.street_width - j), i, block_size - step, block_size - step))

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

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.get_path(self.terminal.get_value())
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

        self.terminal.listen(events)

        self.player_car.move_car(self.commands)


if __name__ == '__main__':

    sim = Dashboard.get_instance()
    sim.set_sim(True)
    while True:
        sim.get_event()
        sim.show()
        sim.wait()




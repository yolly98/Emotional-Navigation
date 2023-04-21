import pygame
import sys
import time
from Client.Dashboard.View.alert import Alert
from Client.Dashboard.View.path_progress import PathProgress
from Client.Dashboard.View.car import Car
from Client.Dashboard.View.arrow import Arrow
from Client.Dashboard.View.terminal import Terminal
from Client.Dashboard.View.face import Face
from Client.communication_manager import CommunicationManager
from Client.state_manager import StateManager
from Client.InputModule.face_recognition_module import FaceRecognitionModule
from Client.InputModule.vocal_command_module import VocalCommandModule
import base64
import polyline
import json
import math


class Dashboard:

    dashboard = None

    def __init__(self):

        # pygame initialization
        pygame.init()

        # set width and height of the window
        self.win_width = 800
        self.win_height = 600

        # create the window
        if StateManager.get_instance().get_state('fullscreen'):
            self.win = pygame.display.set_mode((self.win_width, self.win_height), pygame.FULLSCREEN)
        else:
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

        self.street_lines = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        self.max_car_speed = 200
        self.car_speed_counter = 0
        self.terminal_height = 100
        self.terminal_width = 800
        self.street_width = self.win_width - 200
        self.street_height = self.win_height / 3
        self.street_pos = [0, self.win_height / 3]
        self.player_car = Car(self.street_width - 250, self.win_height - self.terminal_height - 100, self.block_size, self.max_car_speed, 'player')
        self.old_car_speed = 0
        self.old_timestamp = None
        self.start_time = None
        self.travel_time = None
        self.alert = Alert(self.street_width - 100, 60, 5, self.colors['white'], self.colors['black'])
        self.arrow = Arrow(270, 60, 5, None, 'right', self.colors['white'], self.colors['black'])
        self.path_progress = None
        self.terminal = Terminal(0, self.win_height - self.terminal_height, self.terminal_height, 20, self.colors)

    @staticmethod
    def get_instance():
        if Dashboard.dashboard is None:
            Dashboard.dashboard = Dashboard()
        return Dashboard.dashboard

    def end_path(self):
        StateManager.get_instance().set_state('path', None)
        StateManager.get_instance().set_state('travelled_km', 0)
        StateManager.get_instance().set_state('remaining_m', 0)
        StateManager.get_instance().set_state('actual_way_index', 0)
        self.old_car_speed = 0
        self.old_timestamp = None
        self.start_time = None
        self.travel_time = None
        self.path_progress = None
        self.car_speed_counter = 0
        self.terminal.write("Destination reached, Insert new Destination")

    def get_path(self, destination_name):

        request = dict()
        request['username'] = StateManager.get_instance().get_state('username')
        request['destination_name'] = destination_name
        request['source_coord'] = StateManager.get_instance().get_state('last_pos')
        print(request)

        server_ip = StateManager.get_instance().get_state('server_ip')
        server_port = StateManager.get_instance().get_state('server_port')
        res = CommunicationManager.send(server_ip, server_port, "GET", request, "path")
        path = None
        if res is None:
            self.terminal.write("Something went wrong")
            VocalCommandModule.get_instance().say(f"Qualcosa è andato storto, non ho trovato {destination_name}, riprova")  # IT
            return
        elif res['status'] == 0:
            path = json.loads(res['path'])
            print(json.dumps(path, indent=4)) # test
        elif res['status'] == -1:
            self.terminal.write("Path not found")
            VocalCommandModule.get_instance().say(f"Percorso non trovato per {destination_name}") # IT
            return
        else:
            self.terminal.write("Something went wrong")
            VocalCommandModule.get_instance().say(f"Qualcosa è andato storto, riprova") # IT
            return

        path['points'] = polyline.decode(path['points'])
        self.terminal.write(f"Path found for {destination_name}")
        self.terminal.write(f"length:  {round(path['distance'] / 1000, 3)} km")
        self.terminal.write(f"estimated time: {math.floor((path['time']/1000)/60)} minutes {math.floor((path['time']/1000)%60)} seconds")

        self.old_timestamp = time.time()
        self.old_car_speed = 0
        self.start_time = time.time()
        self.travel_time = 0
        self.path_progress = PathProgress(self.street_width + (self.win_width - self.street_width - 30)/2, self.street_pos[1] - 50, self.block_size, path['distance'])
        StateManager.get_instance().path_init(path)
        StateManager.get_instance().set_state('path_destination', destination_name)
        StateManager.get_instance().set_state('end_path', False)
        VocalCommandModule.get_instance().say(f"Ho trovato il percorso migliore per {destination_name}, andiamo!")  # IT

    def show(self):
        self.win.fill(pygame.Color(self.colors['black']))

        # draw sections
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, 0, self.block_size, self.win_height - self.terminal_height))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_width, self.win_height - self.terminal_height - 70, self.win_width - self.street_width, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(self.street_pos[0], self.street_pos[1] - 50, self.street_width, self.block_size / 2))
        pygame.draw.rect(self.win, self.colors['white'], pygame.Rect(0, self.win_height - self.terminal_height, self.win_width, self.block_size))

        font = pygame.font.SysFont('times new roman', 25)

        path = StateManager.get_instance().get_state('path')
        end_path = StateManager.get_instance().get_state('end_path')

        if end_path and path is not None:
            self.end_path()
            return

        if not end_path and path is None:
            print("path recalculation")
            self.get_path(StateManager.get_instance().get_state('path_destination'))
            return

        actual_way = StateManager.get_instance().get_state('actual_way')
        remaining_m = StateManager.get_instance().get_state('remaining_m')

        if actual_way is not None:
            # draw street name
            message = ""
            if actual_way['max_speed'] == -1:
                message = f"{actual_way['street_name']}"
            else:
                message = f"{actual_way['street_name']}, {actual_way['max_speed']} km/h"

            street_surface = font.render(message, True, self.colors['white'])
            street_rect = street_surface.get_rect()
            street_rect.midtop = (self.street_width / 2, 10)
            self.win.blit(street_surface, street_rect)

            if StateManager.get_instance().get_state('path') is not None:

                path_km = StateManager.get_instance().get_state('travelled_km')

                # needed for simulation
                if StateManager.get_instance().get_state('is_sim'):
                    t = time.time() - self.old_timestamp
                    avg_speed = (self.player_car.get_speed() + self.old_car_speed) / 2
                    traveled_km = (avg_speed / 3600) * t
                    path_km += traveled_km
                    self.old_timestamp = time.time()
                    self.old_car_speed = self.player_car.get_speed()
                    StateManager.get_instance().set_state('speed', self.player_car.get_speed())

                    StateManager.get_instance().set_state('travelled_km', path_km)

                # get gps position
                if not StateManager.get_instance().get_state('is_sim'):
                    self.player_car.set_speed(StateManager.get_instance().get_state('speed'))

                # draw m travelled
                m_surface = font.render(f"{math.floor(remaining_m)} m", True, self.colors['white'])
                m_rect = m_surface.get_rect()
                m_rect.midtop = (100, 80)
                self.win.blit(m_surface, m_rect)

                # draw path progress
                self.path_progress.draw(self.win, self.colors, math.floor(path_km * 1000))

                # draw alert
                if 'way_speed' in actual_way and \
                        actual_way['max_speed'] is not None and \
                        not actual_way['max_speed'] == -1 \
                        and StateManager.get_instance().get_state('speed') > actual_way['max_speed']:
                    self.alert.draw(self.win)

                # set arrow direction
                actual_way_index = StateManager.get_instance().get_state('actual_way_index')
                if actual_way_index < len(path['ways']):
                    sign = path['ways'][actual_way_index + 1]['sign']
                    if sign == -8 or sign == 8:
                        self.arrow.set_type('down')
                    elif -3 <= sign < 0 or sign == -7:
                        self.arrow.set_type('left')
                    elif 0 < sign <= 3 or sign == 7:
                        self.arrow.set_type('right')
                    elif sign == 0:
                        self.arrow.set_type('up')

                    if remaining_m <= 50:
                        self.arrow.set_speed(5)
                        self.arrow.draw(self.win)
                    elif remaining_m <= 100:
                        self.arrow.set_speed(10)
                        self.arrow.draw(self.win)
                    else:
                        self.arrow.set_speed(None)
                        self.arrow.draw(self.win)

                    if 99 < remaining_m < 100:
                        VocalCommandModule.get_instance().say(path['ways'][actual_way_index + 1]['text'])
                else:
                    self.arrow.hide()
            else:
                self.arrow.hide()

        # draw car speed
        speed = StateManager.get_instance().get_state('speed')
        speed_surface = font.render(f"{math.floor(speed)} km/h", True, self.colors['white'])
        speed_rect = speed_surface.get_rect()
        speed_rect.midright = (self.win_width - 50, self.win_height - self.terminal_height - 25)
        self.win.blit(speed_surface, speed_rect)

        self.draw_street()
        self.player_car.draw(self.win, self.colors)

        # draw face
        actual_emotion = StateManager.get_instance().get_state('actual_emotion')
        face = Face(self.street_width + (self.win_width - self.street_width) / 2 - 30, 20, 6, actual_emotion)
        face.draw(self.win, self.colors)

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

        car_speed = StateManager.get_instance().get_state('speed')
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

    def get_user(self, username):

        StateManager.get_instance().set_state('username', username)
        root_path = StateManager.get_instance().get_state('root_path')
        is_stored = True
        try:
            with open(f"{root_path}/InputModule/UserImages/{username}.png", "r") as file:
                pass
        except FileNotFoundError:
            is_stored = False

        if not is_stored:
            request = dict()
            request['username'] = username
            server_ip = StateManager.get_instance().get_state('server_ip')
            server_port = StateManager.get_instance().get_state('server_port')
            res = CommunicationManager.send(server_ip, server_port, "GET", request, "user")
            if res is None or res == "":
                self.terminal.write("Something went wrong")
                return
            elif res['status'] == 0:
                image = base64.b64decode(res['image'].encode('utf-8'))
                with open(f"{root_path}/InputModule/UserImages/{username}.png", "wb") as file:
                    file.write(image)
            elif res['status'] == -1:
                self.terminal.write("User not exists")
                self.terminal.write("Do you want to create a new user? [y/n]")
                StateManager.get_instance().set_state('state', 'new_user')
                VocalCommandModule.get_instance().say("L'utente non esiste, vuoi crearne uno nuovo?") # IT
                return
            else:
                self.terminal.write("Something went wrong")
                return

        StateManager.get_instance().set_state('state', 'aut')

    def new_user(self, res):
        res = res.lower()
        if res == 'y' or res == 'yes' or res == 'sì':
            username = StateManager.get_instance().get_state('username')
            self.terminal.write("Press 's' to save a picture")
            self.show()
            FaceRecognitionModule.get_instance().get_picture(username)
            image = None
            root_path = StateManager.get_instance().get_state('root_path')
            with open(f"{root_path}/InputModule/UserImages/{username}.png", "rb") as file:
                image = file.read()

            request = dict()
            request['username'] = username
            request['image'] = base64.b64encode(image).decode('utf-8')
            server_ip = StateManager.get_instance().get_state('server_ip')
            server_port = StateManager.get_instance().get_state('server_port')
            res = CommunicationManager.send(server_ip, server_port, "POST", request, "user")
            if res is None or res == "" or res['status'] < 0:
                self.terminal.write("Something went wrong")
                return
            elif res['status'] == 0:
                pass
            StateManager.get_instance().set_state('state', 'aut')
        elif res == 'n' or res == 'no':
            StateManager.get_instance().set_state('username', None)
            StateManager.get_instance().set_state('state', 'navigator')
        else:
            self.terminal.write("Not valid command, press 'y' or 'n' to create a new user")
            VocalCommandModule.get_instance().say("Comando non valido, si o no?") # IT

    def get_event(self):

        command = None

        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    command = self.terminal.get_value()
                if event.key == pygame.K_UP:
                    self.commands['up'] = True
                if event.key == pygame.K_DOWN:
                    self.commands['down'] = True
                if StateManager.get_instance().get_state('vocal_commands') and event.key == pygame.K_v:
                    command = VocalCommandModule.get_instance().recognize_command()
                    if command is None:
                        VocalCommandModule.get_instance().say("Non ho capito, riprova")  # IT
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    self.commands['up'] = False
                if event.key == pygame.K_DOWN:
                    self.commands['down'] = False

        if command is not None:
            if command == "quit" or command == "esci":
                StateManager.get_instance().set_state('end_path', True)
                self.end_path()
                StateManager.get_instance().set_state('state', 'init')
            if StateManager.get_instance().get_state('state') == 'get_user':
                self.get_user(command)
            elif StateManager.get_instance().get_state('state') == 'new_user':
                self.new_user(command)
            elif StateManager.get_instance().get_state('state') == 'navigator':
                if command == "stop":
                    StateManager.get_instance().set_state('end_path', True)
                    self.end_path()
                else:
                    self.get_path(command)
            else:
                self.terminal.write('Unknown state')

        self.terminal.listen(events)

        self.player_car.move_car(self.commands)

    def run(self):

        while True:
            state = StateManager.get_instance().get_state('state')
            if state == 'init':
                self.terminal.write("Waiting a face ...")
                self.show()
                FaceRecognitionModule.get_instance().find_face()
                self.terminal.write("Face detected")
                self.show()
                StateManager.get_instance().set_state('state', 'aut')
            elif state == 'aut':
                username = FaceRecognitionModule.get_instance().verify_user()
                if username is None:
                    self.terminal.write("User not verified")
                    self.show()
                    self.terminal.write("Insert username")
                    self.show()
                    VocalCommandModule.get_instance().say("Utente non riconosciuto, inserisci il tuo username?") # IT
                    StateManager.get_instance().set_state('state', 'get_user')
                else:
                    self.terminal.write(f"Hi {username}")
                    StateManager.get_instance().set_state('username', username)
                    StateManager.get_instance().set_state('state', 'navigator')
                    self.terminal.write("Where we go?")
                    self.show()
                    VocalCommandModule.get_instance().say(f"Ciao {username}, dove andiamo?") # IT
            else:
                self.get_event()
                self.show()
                self.wait()




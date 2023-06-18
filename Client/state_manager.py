from threading import Lock
from copy import copy
import os


class StateManager:

    state_manager = None

    def __init__(self):
        self.config = dict()
        self.status = dict()
        self.config['fullscreen'] = False
        self.config['server_ip'] = None
        self.config['server_port'] = None
        self.config['dashboard_fps'] = 30
        self.config['is_sim'] = True
        self.config['vocal_commands'] = False
        self.config['out_path_threshold'] = None
        self.config['warning_distance'] = None
        self.status['path'] = None
        self.status['end_path'] = True
        self.status['path_destination'] = None
        self.status['last_time'] = None
        self.status['last_pos'] = None
        self.status['last_pos_index'] = 0
        self.status['actual_way'] = None
        self.status['travelled_km'] = 0
        self.status['speed'] = 0
        # using RLock, many thread can read the state in the same time, but only one can write in the same time
        self.lock = Lock()
        self.status['state'] = None
        self.status['username'] = None
        self.status['actual_emotion'] = 'neutral'
        self.status['monitor_thread'] = False

    @staticmethod
    def get_instance():
        if StateManager.state_manager is None:
            StateManager.state_manager = StateManager()
        return StateManager.state_manager

    def sim_init(self, sim, default_pos=None):
        self.config['is_sim'] = sim
        if sim:
            self.status['last_pos'] = default_pos

    def path_init(self, path):
        if path is None:
            return
        self.status['path'] = path
        self.status['last_pos_index'] = 0
        self.status['travelled_km'] = 0
        self.status['actual_way_index'] = 0
        self.status['actual_way'] = path['ways'][0]
        if 'max_speed' not in self.status['actual_way']:
            self.status['actual_way']['max_speed'] = 60
        self.status['remaining_m'] = path['ways'][0]['distance']
        self.status['end_path'] = False

    def set_config(self, key, value):
        self.config[key] = value

    def set_state(self, key, value):
        with self.lock:
            self.status[key] = value

    def get_config(self, key):
        if key in self.config:
            return copy(self.config[key])
        else:
            return None

    def get_state(self, key):
        with self.lock:
            if key in self.status:
                return copy(self.status[key])
            else:
                return None

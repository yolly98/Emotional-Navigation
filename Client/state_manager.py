from threading import RLock
from copy import copy
from Utility.point import Point
import os


class StateManager:

    state_manager = None

    def __init__(self):
        self.status = dict()
        self.status['fullscreen'] = False
        self.status['server_ip'] = None
        self.status['server_port'] = None
        self.status['path'] = None
        self.status['actual_way'] = None
        self.status['last_time'] = None
        self.status['last_pos'] = None
        self.status['actual_node_index'] = 0
        self.status['travelled_km'] = 0
        self.status['speed'] = 0
        self.status['is_sim'] = True
        # using RLock, many thread can read the state in the same time, but only one can write in the same time
        self.lock = RLock()
        self.status['state'] = None
        self.status['username'] = None
        self.status['root_path'] = os.path.abspath(os.getcwd())
        self.status['actual_emotion'] = 'neutral'
        self.status['vocal_commands'] = False

    @staticmethod
    def get_instance():
        if StateManager.state_manager is None:
            StateManager.state_manager = StateManager()
        return StateManager.state_manager

    def sim_init(self, sim, default_pos=None):
        self.status['is_sim'] = sim
        if sim:
            self.status['last_pos'] = default_pos

    def path_init(self):
        if self.status['path'] is None:
            return
        self.status['actual_node_index'] = 0
        self.status['travelled_km'] = 0
        node = self.status['path'][0]['start_node']
        self.status['last_pos'] = Point(node.get('lat'), node.get('lon'))

    def set_state(self, key, value):
        with self.lock:
            self.status[key] = value

    def get_state(self, key):
        with self.lock:
            if key in self.status:
                return copy(self.status[key])
            else:
                return None

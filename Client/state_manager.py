from threading import RLock
from copy import copy

class StateManager:

    state_manager = None

    def __init__(self):
        self.status = dict()
        self.status['path'] = None
        self.actual_way = None
        # using RLock, many thread can read the state in the same time, but only one can write in the same time
        self.lock = RLock()

    @staticmethod
    def get_instance():
        if StateManager.state_manager is None:
            StateManager.state_manager = StateManager()
        return StateManager.state_manager

    def set_state(self, key, value):
        with self.lock:
            self.status[key] = value

    def get_state(self, key):
        with self.lock:
            if key in self.status:
                return copy(self.status[key])
            else:
                return None

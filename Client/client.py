from threading import Thread
from Client.state_manager import StateManager
from Utility.point import Point
from Client.Dashboard.dashboard import Dashboard
from Client.InputModule.gps_module import GPS

DEFAULT_LAT = '42.3333569'
DEFAULT_LON = '12.2692692'


if __name__ == '__main__':

    StateManager.get_instance().sim_init(True, Point(DEFAULT_LAT, DEFAULT_LON))
    gps_module = Thread(target=GPS.get_instance().run, args=())
    gps_module.setDaemon(False)
    gps_module.start()

    Dashboard.get_instance().run()


from threading import Thread
from Client.state_manager import StateManager
from Utility.point import Point
from Client.Dashboard.dashboard import Dashboard
from Client.InputModule.gps_module import GPS
from Client.InputModule.face_recognition_module import FaceRecognitionModule

DEFAULT_LAT = '42.3333569'
DEFAULT_LON = '12.2692692'
SERVER_IP = "127.0.0.1"
SERVER_PORT = "5000"
FULLSCREEN = False

if __name__ == '__main__':

    StateManager.get_instance().sim_init(True, Point(DEFAULT_LAT, DEFAULT_LON))
    StateManager.get_instance().set_state('server_ip', SERVER_IP)
    StateManager.get_instance().set_state('server_port', SERVER_PORT)
    StateManager.get_instance().set_state('fullscreen', FULLSCREEN)

    FaceRecognitionModule.get_instance().configure(0, 20, 0.3, 20, 20)

    gps_module = Thread(target=GPS.get_instance().run, args=())
    history_collector = Thread(target=FaceRecognitionModule.get_instance().run, args=())
    gps_module.setDaemon(False)
    history_collector.setDaemon(False)
    gps_module.start()
    history_collector.start()

    Dashboard.get_instance().run()


from threading import Thread
from Client.state_manager import StateManager
from Utility.point import Point
from Client.Dashboard.dashboard import Dashboard
from Client.InputModule.gps_module import GPS
from Client.InputModule.face_recognition_module import FaceRecognitionModule
from Client.InputModule.vocal_command_module import VocalCommandModule

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
    VocalCommandModule.get_instance().init()

    FaceRecognitionModule.get_instance().configure(
        camera=1,
        iterations=20,
        wait_time=0.3,
        period=60,
        user_detection_attempts=5)

    if StateManager.get_instance().get_state('is_sim'):
        gps_module = Thread(target=GPS.get_instance().run_simulation, args=(), daemon=False)
    else:
        gps_module = Thread(target=GPS.get_instance().listener, args=(), daemon=False)

    history_collector = Thread(target=FaceRecognitionModule.get_instance().run, args=(), daemon=False)
    gps_module.start()
    history_collector.start()

    Dashboard.get_instance().run()


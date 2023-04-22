from threading import Thread
from Client.state_manager import StateManager
from Client.Dashboard.dashboard import Dashboard
from Client.InputModule.gps_manager import GPS
from Client.InputModule.gps_extern_module import GPSExternModule
from Client.InputModule.face_recognition_module import FaceRecognitionModule
from Client.InputModule.vocal_command_module import VocalCommandModule

import json

if __name__ == '__main__':

    # load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    StateManager.get_instance().sim_init(
        config['simulation'],
        [float(config['default_lat']), float(config['default_lon'])]
    )
    StateManager.get_instance().set_state('server_ip', config['server_ip'])
    StateManager.get_instance().set_state('server_port', config['server_port'])
    StateManager.get_instance().set_state('fullscreen', config['fullscreen'])
    StateManager.get_instance().set_state('vocal_commands', config['vocal_commands'])
    VocalCommandModule.get_instance().init()

    camera = config['face_recognition']
    FaceRecognitionModule.get_instance().configure(
        camera=camera['camera'],
        iterations=camera['iterations'],
        wait_time=camera['wait_time'],
        period=camera['period'],
        user_detection_attempts=camera['user_detection_attempts']
    )

    if not config['user_recognition']:
        StateManager.get_instance().set_state('state', 'navigator')
        StateManager.get_instance().set_state('username', None)
    else:
        StateManager.get_instance().set_state('state', 'init')

    gps_module = None
    if StateManager.get_instance().get_state('is_sim'):
        gps_module = Thread(target=GPS.get_instance().run_simulation, args=(), daemon=False)
    else:
        gps_module = Thread(target=GPS.get_instance().listener, args=(), daemon=False)
    gps_module.start()

    ext_gps_config = config['extern_gps_module']
    if ext_gps_config['enable']:
        GPSExternModule.get_instance().config(
            usb_port=ext_gps_config['usb_port'],
            server_ip=ext_gps_config['server_ip'],
            server_port=ext_gps_config['server_port'],
            target_resource=ext_gps_config['target_resource'],
            interval=ext_gps_config['interval']

        )
        extern_gps_module = Thread(target=GPSExternModule.get_instance().run, args=(), daemon=False)
        extern_gps_module.start()

    if config['history_collections']:
        history_collector = Thread(target=FaceRecognitionModule.get_instance().run, args=(), daemon=False)
        history_collector.start()

    Dashboard.get_instance().run()


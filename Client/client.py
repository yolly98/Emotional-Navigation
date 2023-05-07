from threading import Thread
from Client.state_manager import StateManager
from Client.Dashboard.dashboard import Dashboard
from Client.InputModule.gps_manager import GPS
from Client.InputModule.gps_extern_module import GPSExternModule
from Client.InputModule.face_recognition_module import FaceRecognitionModule
from Client.InputModule.vocal_command_module import VocalCommandModule
from Client.Monitor.monitor import Monitor
from Client.InputModule.Test.gps_module_sim import GPSsim
import os
import signal
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
    StateManager.get_instance().set_state('vocal_commands', config['vocal_commands']['enable'])
    VocalCommandModule.get_instance().init(
        stt_service=config['vocal_commands']['stt_service'],
        mic_device=config['vocal_commands']['mic_device']
    )

    face_rec = config['face_recognition']
    FaceRecognitionModule.get_instance().configure(
        camera=face_rec['camera'],
        emotion_samples=face_rec['emotion_samples'],
        wait_time=face_rec['wait_time'],
        period=face_rec['period'],
        detector=face_rec['detector'],
        model=face_rec['model'],
        distance=face_rec['distance']
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
    StateManager.get_instance().set_state('gps_module_thread', True)
    gps_module.start()

    ext_gps_config = config['extern_gps_module']
    extern_gps_module = None
    if ext_gps_config['enable']:
        GPSExternModule.get_instance().config(
            usb_port=ext_gps_config['usb_port'],
            server_ip=ext_gps_config['server_ip'],
            server_port=ext_gps_config['server_port'],
            target_resource=ext_gps_config['target_resource'],
            interval=ext_gps_config['interval']

        )
        extern_gps_module = Thread(target=GPSExternModule.get_instance().run, args=(), daemon=False)
        StateManager.get_instance().set_state('extern_gps_module_thread', True)
        extern_gps_module.start()
    else:
        extern_gps_module = Thread(target=GPSsim.run, args=(), daemon=False)
        StateManager.get_instance().set_state('extern_gps_module_thread', True)
        extern_gps_module.start()

    history_collector = None
    if config['history_collections']:
        history_collector = Thread(target=FaceRecognitionModule.get_instance().run, args=(), daemon=False)
        StateManager.get_instance().set_state('history_collector_thread', True)
        history_collector.start()

    monitor = None
    if config['monitor']:
        monitor = Thread(target=Monitor.run, args=(), daemon=False)
        StateManager.get_instance().set_state('monitor_thread', True)
        monitor.start()

    Dashboard.get_instance().run()

    StateManager.get_instance().set_state('gps_module_thread', False)
    StateManager.get_instance().set_state('extern_gps_module_thread', False)
    StateManager.get_instance().set_state('history_collector_thread', False)
    StateManager.get_instance().set_state('monitor_thread', False)

    print("App terminated")

    if monitor is not None:
        monitor.join()

    os.kill(os.getpid(), signal.SIGINT)
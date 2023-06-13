from threading import Thread
from Client.state_manager import StateManager
from Client.Dashboard.dashboard import Dashboard
from Client.InOutModules.gps_manager import GPS
from Client.InOutModules.gps_external_module import GPSExternalModule
from Client.InOutModules.face_processing_module import FaceProcessingModule
from Client.InOutModules.vocal_inout_module import VocalInOutModule
from Client.Monitor.monitor import Monitor
from Client.InOutModules.Test.gps_module_sim import GPSsim
from Client.InOutModules.arduino_button_module import ArduinoButton
import os
import signal
import json

if __name__ == '__main__':

    print("-------- START INITIALIZATION --------")

    # load configuration
    actual_path = os.path.dirname(__file__)
    with open(os.path.join(actual_path, 'Resources', 'config.json'), 'r') as f:
        config = json.load(f)

    print("loaded configuration")

    if config['simulation'] == 'sim0':
        simulation = True
    else:
        simulation = False
    StateManager.get_instance().sim_init(
        simulation,
        [float(config['default_lat']), float(config['default_lon'])]
    )
    StateManager.get_instance().set_state('server_ip', config['server_ip'])
    StateManager.get_instance().set_state('server_port', config['server_port'])
    StateManager.get_instance().set_state('fullscreen', config['fullscreen'])
    StateManager.get_instance().set_state('vocal_commands', config['vocal_commands']['enable'])

    print("StateManager configured")

    VocalInOutModule.get_instance().init(
        stt_service=config['vocal_commands']['stt_service'],
        mic_device=config['vocal_commands']['mic_device'],
        mic_timeout=config['vocal_commands']['mic_timeout']
    )

    print("VocalInOutModule configured")

    ArduinoButton.get_instance().init(config['arduino_usb'])

    face_rec = config['face_recognition']
    FaceProcessingModule.get_instance().configure(
        camera=face_rec['camera'],
        max_attempts=face_rec['max_attempts'],
        emotion_samples=face_rec['emotion_samples'],
        wait_time=face_rec['wait_time'],
        period=face_rec['period'],
        detector=face_rec['detector'],
        model=face_rec['model'],
        distance=face_rec['distance']
    )

    StateManager.get_instance().set_state('user_recognition', config['user_recognition'])
    StateManager.get_instance().set_state('state', 'init')

    print("FaceProcessingModule configured")

    ext_gps_config = config['extern_gps_module']
    gps_module = None
    if simulation:
        gps_module = Thread(target=GPS.get_instance().run_simulation, args=(), daemon=True)
    else:
        gps_module = Thread(target=GPS.get_instance().listener, args=(ext_gps_config['server_port'],), daemon=True)
    gps_module.start()

    extern_gps_module = None
    if not simulation:
        if config['simulation'] == 'nosim':
            GPSExternalModule.get_instance().config(
                usb_port=ext_gps_config['usb_port'],
                server_ip=ext_gps_config['server_ip'],
                server_port=ext_gps_config['server_port'],
                target_resource='gps-collector',
                interval=ext_gps_config['interval']

            )
            extern_gps_module = Thread(target=GPSExternalModule.get_instance().run, args=(), daemon=True)
            extern_gps_module.start()
        elif config['simulation'] == 'sim1':
            extern_gps_module = Thread(target=GPSsim.run, args=(ext_gps_config['server_ip'], ext_gps_config['server_port']), daemon=True)
            extern_gps_module.start()
        else:
            print("Unknown simulation mode")
            exit(1)

    print(f"GPSModule configured [{config['simulation']}]")

    history_collector = None
    if config['history_collections']:
        history_collector = Thread(target=FaceProcessingModule.get_instance().run, args=(), daemon=True)
        history_collector.start()

    print("HistoryCollector configured")

    monitor = None
    if config['monitor']:
        monitor = Thread(target=Monitor.run, args=(), daemon=True)
        StateManager.get_instance().set_state('monitor_thread', True)
        monitor.start()

    print("Monitor configured")

    print("-------- INITIALIZATION ENDED --------")

    Dashboard.get_instance().run()

    StateManager.get_instance().set_state('monitor_thread', False)

    print("App terminated")

    if monitor is not None:
        monitor.join()

    try:
        os.kill(os.getpid(), signal.SIGINT)
    except:
        pass
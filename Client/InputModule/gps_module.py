# if you want to get gps coordinate from the smartphone,
# you have to go to 'chrome://flags/#unsafely-treat-insecure-origin-as-secure'
# in the search bar of your chromium browser on the smartphone,
# the you have to enable the ip of this device
# (you have to do this because browsers can't share gps position with not https server)


from Utility.utility_functions import calculate_distance
from Utility.point import Point
from Utility.way import Way
from Utility.gnode import GNode
from math import radians, sin, cos, asin, atan2, degrees
import time
from Client.state_manager import StateManager
from flask import Flask, request, send_file
from flask_cors import CORS
from Client.communication_manager import CommunicationManager
import json

GPS_IP = "0.0.0.0"
GPS_PORT = '4000'


class GPS:

    gps_simulator = None

    def __init__(self):
        self.period = 5
        self.app = Flask(__name__)
        CORS(self.app)

    @staticmethod
    def get_instance():
        if GPS.gps_simulator is None:
            GPS.gps_simulator = GPS()
        return GPS.gps_simulator

    def get_app(self):
        return self.app

    def listener(self):
        self.app.run(host=GPS_IP, port=GPS_PORT, debug=False, threaded=True)

    def get_coord(self, travelled_km):

        actual_node_index = StateManager.get_instance().get_state('actual_node_index')

        path = StateManager.get_instance().get_state('path')
        if path is None:
            return StateManager.get_instance().get_state('last_pos')

        i = 0
        ms = 0
        while i < len(path):
            if i < actual_node_index:
                ms += path[i]['way'].get('length')
            else:
                distance = path[actual_node_index]['way'].get('length')
                if (travelled_km * 1000) <= ms + distance:
                    break
                else:
                    ms += distance
                    if i + 1 < len(path):
                        actual_node_index += 1
            i += 1

        p1 = Point(path[actual_node_index]['start_node'].get('lat'), path[actual_node_index]['start_node'].get('lon'))
        if actual_node_index >= len(path) - 1:
            return p1
        p2 = Point(path[actual_node_index + 1]['start_node'].get('lat'), path[actual_node_index + 1]['start_node'].get('lon'))

        lat1 = float(p1.get_lat())
        lon1 = float(p1.get_lon())
        lat2 = float(p2.get_lat())
        lon2 = float(p2.get_lon())
        d = travelled_km - (ms / 1000)

        R = 6371  # Earth radius in km
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        bearing = atan2(sin(lon2 - lon1) * cos(lat2),
                        cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1))
        lat3 = asin(sin(lat1) * cos(d / R) + cos(lat1) * sin(d / R) * cos(bearing))
        lon3 = lon1 + atan2(sin(bearing) * sin(d / R) * cos(lat1), cos(d / R) - sin(lat1) * sin(lat3))

        p3 = Point(str(round(degrees(lat3), 7)), str(round(degrees(lon3), 7)))

        print(f"GPS pos: {p3}")

        return p3

    def run_simulation(self):
        while True:
            travelled_km = StateManager.get_instance().get_state('travelled_km')
            pos = self.get_coord(travelled_km)
            StateManager.get_instance().set_state('last_pos', pos)

            server_ip = StateManager.get_instance().get_state('server_ip')
            server_port = StateManager.get_instance().get_state('server_port')
            request = pos.to_json()
            res = CommunicationManager.get_instance().send(server_ip, server_port, 'GET', request, 'way')
            actual_way = None
            if res['status'] == 0:
                actual_way = dict()
                actual_way['way'] = Way.json_to_way(res['way'])
                actual_way['start_node'] = GNode.json_to_gnode(res['start_node'])
                actual_way['end_node'] = GNode.json_to_gnode(res['end_node'])
            StateManager.get_instance().set_state('actual_way', actual_way)

            time.sleep(self.period)


app = GPS.get_instance().get_app()


@app.get('/gps')
def get_gps():
    return send_file('send_GPS.html')


@app.post('/gps')
def post_gps():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    lat = received_json['lat']
    lon = received_json['lon']
    new_pos = Point(lat, lon)
    print(f"GPS pos: {new_pos}")
    last_pos = StateManager.get_instance().get_state('last_pos')

    if last_pos is not None:
        distance = calculate_distance(new_pos, last_pos)
        travelled_km = StateManager.get_instance().get_state('travelled_km')
        travelled_km += distance
        speed = (distance / GPS.get_instance().period) * 3600
        StateManager.get_instance().set_state('travelled_km', travelled_km)
        StateManager.get_instance().set_state('speed', speed)
    else:
        StateManager.get_instance().set_state('travelled_km', 0)
        StateManager.get_instance().set_state('speed', 0)

    StateManager.get_instance().set_state('last_pos', new_pos)

    server_ip = StateManager.get_instance().get_state('server_ip')
    server_port = StateManager.get_instance().get_state('server_port')
    server_request = last_pos.to_json()
    res = CommunicationManager.get_instance().send(server_ip, server_port, 'GET', server_request, 'way')
    actual_way = None
    if res['status'] == 0:
        actual_way = dict()
        actual_way['way'] = Way.json_to_way(res['way'])
        actual_way['start_node'] = GNode.json_to_gnode(res['start_node'])
        actual_way['end_node'] = GNode.json_to_gnode(res['end_node'])
    StateManager.get_instance().set_state('actual_way', actual_way)

    return {"status": 0}

@app.post('/gps-collector')
def post_gps_collector():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500

    received_json = request.json
    lat = received_json['lat']
    lon = received_json['lon']
    new_pos = Point(lat, lon)
    print(f"GPS pos: {new_pos}")

    gps_data = None

    try:
        with open('gps-test.json', 'r') as f:
            gps_data = json.load(f)
    except Exception:
        pass

    if gps_data is None:
        gps_data = dict()
        gps_data['gps'] = []

    gps_data['gps'].append(new_pos.to_json())

    with open('gps-test.json', 'w') as f:
        json.dump(gps_data, f)

    return {"status": 0}

if __name__ == '__main__':
    GPS.get_instance().listener()
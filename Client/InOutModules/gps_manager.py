from math import radians, sin, cos, asin, atan2, degrees
import time
from Client.state_manager import StateManager
from Client.communication_manager import CommunicationManager
from Client.Monitor.monitor import Monitor
from flask import Flask, request, send_file
from flask_cors import CORS
import json
from datetime import datetime
import math
import logging
import time

class GPS:

    gps_manager = None

    def __init__(self):
        self.sim_period = 1
        self.app = Flask(__name__)
        CORS(self.app)

    @staticmethod
    def get_instance():
        if GPS.gps_manager is None:
            GPS.gps_manager = GPS()
        return GPS.gps_manager

    def get_app(self):
        return self.app

    def listener(self, port):
        self.app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

    @staticmethod
    def calculate_distance(Point1, Point2):  # in m

        lat1 = float(Point1[0])
        lon1 = float(Point1[1])
        lat2 = float(Point2[0])
        lon2 = float(Point2[1])

        R = 6371000  # Earth radius in m
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        c = 2 * math.asin(math.sqrt(a))
        distance = R * c

        return distance

    @staticmethod
    def get_actual_way():

        travelled_km = StateManager.get_instance().get_state('travelled_km')
        last_pos_index = StateManager.get_instance().get_state('last_pos_index')
        path = StateManager.get_instance().get_state('path')

        remaining_m = 0
        actual_way = None
        travelled_m = travelled_km * 1000
        actual_way_index = 0
        if path is not None:
            for way in path['ways']:
                if way['interval'][0] <= last_pos_index < way['interval'][1]:
                    actual_way = way
                    remaining_m = way['distance'] - travelled_m
                    break
                else:
                    travelled_m -= way['distance']
                    actual_way_index += 1

            for speed in path['max_speed']:
                if speed[0] <= last_pos_index < speed[1]:
                    actual_way['max_speed'] = speed[2]

            # [Test]
            # print(f"remaining_m: {remaining_m}, way_index: {actual_way_index}, pos_index: {last_pos_index} len_ways: {len(path['ways']) - 1}")
            if remaining_m <= 0:
                remaining_m = 0
                if actual_way_index >= (len(path['ways']) - 1):
                    StateManager.get_instance().set_state('end_path', True)
                    return
        else:
            server_ip = StateManager.get_instance().get_state('server_ip')
            server_port = StateManager.get_instance().get_state('server_port')
            server_request = {"coord": StateManager.get_instance().get_state('last_pos')}
            res = CommunicationManager.send(server_ip, server_port, 'GET', server_request, 'way')
            if res['status'] == 0 and res['address'] is not None:
                actual_way = dict()
                if 'road' in res['address']:
                    actual_way['street_name'] = res['address']['road']
                else:
                    actual_way['street_name'] = 'Unknown'
                actual_way['max_speed'] = -1

        if 'max_speed' not in actual_way or actual_way['max_speed'] is None:
            actual_way['max_speed'] = 60

        # [Test]
        # print(json.dumps(actual_way, indent=4))
        # print("-----------------------------------")

        StateManager.get_instance().set_state('actual_way', actual_way)
        StateManager.get_instance().set_state('remaining_m', remaining_m)
        StateManager.get_instance().set_state('actual_way_index', actual_way_index)

    @staticmethod
    def get_hypothetical_position():

        travelled_km = StateManager.get_instance().get_state('travelled_km')
        last_pos_index = StateManager.get_instance().get_state('last_pos_index')
        path = StateManager.get_instance().get_state('path')
        new_pos = None
        if path is None:
            new_pos = StateManager.get_instance().get_state('last_pos')
        else:
            i = 0
            distance = travelled_km * 1000
            while i < len(path['points']):
                if i > 0:
                    m = GPS.calculate_distance(path['points'][i - 1], path['points'][i])
                    distance -= m
                    if i > last_pos_index:
                        if distance > 0:
                            last_pos_index = i
                        else:
                            distance += m
                            break
                i += 1

            # p3 interpolation between p1 and p2
            p1 = path['points'][last_pos_index]
            if last_pos_index >= len(path['points']) - 1:
                new_pos = p1
            else:
                p2 = path['points'][last_pos_index + 1]

                lat1 = float(p1[0])
                lon1 = float(p1[1])
                lat2 = float(p2[0])
                lon2 = float(p2[1])
                d = distance

                R = 6371000  # Earth radius
                lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
                bearing = atan2(sin(lon2 - lon1) * cos(lat2),
                                cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(lon2 - lon1))
                lat3 = asin(sin(lat1) * cos(d / R) + cos(lat1) * sin(d / R) * cos(bearing))
                lon3 = lon1 + atan2(sin(bearing) * sin(d / R) * cos(lat1), cos(d / R) - sin(lat1) * sin(lat3))

                p3 = [float(degrees(lat3)), float(degrees(lon3))]
                new_pos = p3

            return {'last_pos_index': last_pos_index, 'last_pos': new_pos}

        # [Test]
        # print(f"GPS pos: {new_pos}")

    def run_simulation(self):
        while True:
            start_time = time.time()
            res = GPS.get_hypothetical_position()
            if res is None:
                continue
            StateManager.get_instance().set_state('last_pos_index', res['last_pos_index'])
            StateManager.get_instance().set_state('last_pos', res['last_pos'])
            GPS.get_actual_way()

            Monitor.get_instance().collect_measure('gps_manager', time.time() - start_time)
            Monitor.get_instance().collect_measure('gps_coords', f"{res['last_pos'][0]}, {res['last_pos'][1]}")
            time.sleep(self.sim_period)


app = GPS.get_instance().get_app()
logging.getLogger('werkzeug').disabled = True


@app.post('/gps-collector')
def post_gps():
    if request.json is None:
        return {'error': 'No JSON request received'}, 500


    start_time = time.time()
    received_json = request.json
    lat = received_json['pos'][0]
    lon = received_json['pos'][1]
    gps_time = received_json['datetime']
    gps_time = datetime.strptime(gps_time, "%Y-%m-%d %H:%M:%S")
    gps_time = time.mktime(gps_time.timetuple())
    new_pos = [float(lat), float(lon)]

    # [Test]
    # print(f"GPS pos: {new_pos}, datetime: {received_json['datetime']}")
    last_pos = StateManager.get_instance().get_state('last_pos')
    travelled_km = StateManager.get_instance().get_state('travelled_km')

    if last_pos is not None:
        distance = GPS.calculate_distance(new_pos, last_pos) / 1000
        travelled_km += distance
        period = gps_time - StateManager.get_instance().get_state('last_time')
        # period = 1# [Test]
        if not period == 0:
            speed = (distance / period) * 3600
            # print(f"period: {period}, distance: {distance}, speed: {speed}")
            StateManager.get_instance().set_state('last_time', gps_time)
            StateManager.get_instance().set_state('travelled_km', travelled_km)
            StateManager.get_instance().set_state('speed', speed)
    else:
        StateManager.get_instance().set_state('last_time', gps_time)
        StateManager.get_instance().set_state('travelled_km', 0)
        StateManager.get_instance().set_state('speed', 0)

    StateManager.get_instance().set_state('last_pos', new_pos)

    # check if new_pos is in the path
    path = StateManager.get_instance().get_state('path')
    last_pos_index = StateManager.get_instance().get_state('last_pos_index')
    if path is None:
        pass
    else:
        res = GPS.get_hypothetical_position() # get the position in witch I should be
        hypothetical_position = res['last_pos']
        distance = GPS.calculate_distance(new_pos, hypothetical_position)
        if distance < 40:
            StateManager.get_instance().set_state('last_pos_index', res['last_pos_index'])
        else:
            # [Test]
            print(f"position outside the path  [{distance}]")
            StateManager.get_instance().set_state('path', None)
            Monitor.get_instance().collect_measure('path_recalculations', f"{hypothetical_position[0]}, {hypothetical_position[1]}")

    GPS.get_actual_way()

    Monitor.get_instance().collect_measure('gps_manager', time.time() - start_time)
    Monitor.get_instance().collect_measure('gps_coords', f"{lat}, {lon}")
    return {"status": 0}


if __name__ == '__main__':
    GPS.get_instance().listener()
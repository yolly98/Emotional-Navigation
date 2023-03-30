from Utility.utility_functions import calculate_distance
from Utility.point import Point
from math import radians, sin, cos, asin, atan2, degrees
import time
from Client.state_manager import StateManager


class GPS:

    gps_simulator = None

    def __init__(self):
        self.period = 1

    @staticmethod
    def get_instance():
        if GPS.gps_simulator is None:
            GPS.gps_simulator = GPS()
        return GPS.gps_simulator

    def get_coord(self, sim, travelled_km):

        actual_node_index = StateManager.get_instance().get_state('actual_node_index')

        if sim:

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
        else:
            # TODO get from GPS sensor and update travelled km
            new_pos = Point('42.3333569', '12.2692692')
            last_pos = StateManager.get_instance().get_state('last_pos')
            distance = calculate_distance(new_pos, last_pos)
            travelled_km += distance
            speed = (distance / self.period) * 3600
            StateManager.get_instance().set_state('speed', speed)
            pass

    def run(self):
        while True:
            is_sim = StateManager.get_instance().get_state('is_sim')
            travelled_km = StateManager.get_instance().get_state('travelled_km')
            pos = self.get_coord(is_sim, travelled_km)
            StateManager.get_instance().set_state('last_pos', pos)
            time.sleep(self.period)


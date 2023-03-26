from Utility.utility_functions import calculate_distance
from Utility.point import Point
from math import radians, sin, cos, asin, atan2, degrees
import time

DEFAULT_LAT = '42.3333569'
DEFAULT_LON = '12.2692692'


class GPS:

    gps_simulator = None

    def __init__(self):
        self.path = None
        self.actual_node = 0
        self.period = 1
        self.time = None
        self.last_pos = None
        self.speed = 0

    @staticmethod
    def get_instance():
        if GPS.gps_simulator is None:
            GPS.gps_simulator = GPS()
        return GPS.gps_simulator

    def get_speed(self):
        return self.speed

    def get_last_pos(self):
        return self.last_pos

    def set_path(self, path):
        self.path = path
        self.actual_node = 0
        node = path[0]['start_node']
        self.last_pos = Point(node.get('lat'), node.get('lon'))

    def get_coord(self, sim, travelled_km):

        if (self.time is not None) and (time.time() - self.time < self.period):
            return self.last_pos

        self.time = time.time()

        if sim:
            if self.last_pos is None or travelled_km == -1:
                self.last_pos = Point(DEFAULT_LAT, DEFAULT_LON)
                print(f"GPS pos: {self.last_pos}")
                return self.last_pos

            i = 0
            ms = 0
            while i < len(self.path):
                if i < self.actual_node:
                    ms += self.path[i]['way'].get('length')
                else:
                    distance = self.path[self.actual_node]['way'].get('length')
                    if (travelled_km * 1000) <= ms + distance:
                        break
                    else:
                        ms += distance
                        self.actual_node += 1
                i += 1
                if i == len(self.path):
                    return None

            p1 = Point(self.path[self.actual_node]['start_node'].get('lat'), self.path[self.actual_node]['start_node'].get('lon'))
            if self.actual_node >= len(self.path):
                self.last_pos = p1
                return p1
            p2 = Point(self.path[self.actual_node + 1]['start_node'].get('lat'), self.path[self.actual_node + 1]['start_node'].get('lon'))

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

            self.last_pos = p3
            print(f"GPS pos: {self.last_pos}")
            return self.last_pos
        else:
            # TODO get from GPS sensor and update travelled km
            new_pos = Point('42.3333569', '12.2692692')
            distance = calculate_distance(new_pos, self.last_pos)
            travelled_km += distance
            self.speed = (distance / self.period) * 3600
            pass


if __name__ == '__main__':
    print(GPS.get_instance().get_coord(True, -1))
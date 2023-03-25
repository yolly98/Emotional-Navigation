from Utility.utility import Point, calculate_distance
import math
import time


class GPS:

    gps_simulator = None

    def __init__(self):
        self.path = None
        self.actual_node = 0
        self.period = 5
        self.time = None
        self.last_pos = None

    @staticmethod
    def get_instance():
        if GPS.gps_simulator is None:
            GPS.gps_simulator = GPS()
        return GPS.gps_simulator

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
            if travelled_km == -1:
                self.last_pos = Point('42.3333569', '12.2692692')
                print(f"GPS pos: {self.last_pos}")
                return self.last_pos

            p = self.path[self.actual_node]['start_node']
            actual_point = Point(p.get('lat'), p.get('lon'))
            while True:
                if self.actual_node + 1 >= len(self.path):
                    return
                p = self.path[self.actual_node + 1]['start_node']
                next_point = Point(p.get('lat'), p.get('lon'))
                points_distance = calculate_distance(actual_point, next_point)
                if travelled_km <= points_distance:
                    break
                else:
                    travelled_km -= points_distance
                    self.actual_node += 1
                    actual_point = next_point

            p1 = actual_point
            p2 = next_point
            phi1, phi2 = math.radians(float(p1.get_lat())), math.radians(float(p2.get_lat()))
            delta_lambda = math.radians(float(p2.get_lon()) - float(p1.get_lon()))
            y = math.sin(delta_lambda) * math.cos(phi2)
            x = math.cos(phi1) * math.sin(phi2) - math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda)
            azimuth = math.atan2(y, x)
            R = 6371  # Earth radius in km
            d = travelled_km
            lat1, lon1 = math.radians(float(p1.get_lat())), math.radians(float(p1.get_lon()))
            lat3 = math.asin(math.sin(lat1) * math.cos(d / R) + math.cos(lat1) * math.sin(d / R) * math.cos(azimuth))
            lon3 = lon1 + math.atan2(math.sin(azimuth) * math.sin(d / R) * math.cos(lat1),
                                     math.cos(d / R) - math.sin(lat1) * math.sin(lat3))
            p3 = Point(str(round(math.degrees(lat3), 7)), str(round(math.degrees(lon3), 7)))
            self.last_pos = p3
            print(f"GPS pos: {self.last_pos}")
            return self.last_pos
        else:
            # TODO get from GPS sensor
            pass


if __name__ == '__main__':
    print(GPS.get_instance().get_coord(True, -1))
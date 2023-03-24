import math
import json


class Point:

    def __init__(self, lat, lon):
        self.lat = lat
        self.lon = lon

    def get_lat(self):
        return self.lat

    def get_lon(self):
        return self.lon

    def __str__(self):
        return str(f"({self.lat}, {self.lon})")

# -------------------


class Way:

    def __init__(self, id, name, alt_name, ref, speed, length, start_node, end_node):
        self.way = dict()
        self.way['id'] = id
        self.way['name'] = name
        self.way['alt_name'] = alt_name
        self.way['ref'] = ref
        self.way['speed'] = speed
        self.way['length'] = length
        self.way['start_node'] = start_node
        self.way['end_node'] = end_node

    def get(self, key):
        if key in self.way:
            return self.way[key]
        else:
            return -1

    def set(self, key, value):
        if key in self.way:
            self.way[key] = value
            return 0
        else:
            return -1

    def __str__(self):
        return self.way.__str__()

# -------------------


class GNode:

    def __init__(self, id, type, name, lat, lon):
        self.node = dict()
        self.node['id'] = id
        self.node['type'] = type
        self.node['name'] = name
        self.node['lat'] = str(lat)
        self.node['lon'] = str(lon)

    def get(self, key):
        if key in self.node:
            return self.node[key]
        return -1

    def set(self, key, value):
        if key in self.node:
            self.node[key] = value
            return 0
        else:
            return -1

    def __str__(self):
        return self.node.__str__()

# -------------------


def calculate_distance(Point1, Point2): # in km

    lat1 = float(Point1.get_lat())
    lon1 = float(Point1.get_lon())
    lat2 = float(Point2.get_lat())
    lon2 = float(Point2.get_lon())

    R = 6371  # Earth radius in km
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

# ----------------------


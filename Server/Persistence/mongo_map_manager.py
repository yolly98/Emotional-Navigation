from pymongo import MongoClient
from Utility.way import Way
from Utility.gnode import GNode
from Utility.point import Point
import math

class MongoMapManager:

    mongo_map_manager = None

    def __init__(self):
        self.conn = None

    @staticmethod
    def get_instance():
        if MongoMapManager.mongo_map_manager is None:
            MongoMapManager.mongo_map_manager = MongoMapManager()
        return MongoMapManager.mongo_map_manager

    def open_connection(self):
        self.conn = MongoClient('mongodb://admin:password@localhost:27017/')

    def close_connection(self):
        self.conn.close()
        self.conn = None

    def get_way(self, way_id):
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].map_way
        way = db.find_one({'id': way_id})
        if way is None:
            return None
        return Way.json_to_way(way)

    def get_way_by_start_node(self, start_node):
        if self.conn is None:
            return False

        db = self.conn['smart_navigation'].map_way
        json_ways = db.find({'start_node': start_node})
        if json_ways is None:
            return None
        ways = []
        for json_way in json_ways:
            way = Way.json_to_way(json_way)
            ways.append(way)
        return ways

    def get_way_by_name(self, way_name):
        if self.conn is None:
            return False

        db = self.conn['smart_navigation'].map_way
        json_ways = db.find({'name': way_name})
        if json_ways is None:
            return None
        ways = []
        for json_way in json_ways:
            way = Way.json_to_way(json_way)
            ways.append(way)
        return ways

    def get_way_by_end_node(self, end_node):
        if self.conn is None:
            return False

        db = self.conn['smart_navigation'].map_way
        json_ways = db.find({'end_node': end_node})
        if json_ways is None:
            return None
        ways = []
        for json_way in json_ways:
            way = Way.json_to_way(json_way)
            ways.append(way)
        return ways

    def get_way_by_node(self, node):
        if self.conn is None:
            return False

        db = self.conn['smart_navigation'].map_way
        json_ways = db.find(
            {
                '$or': [
                    {'end_node': node},
                    {'end_node': node}
                ]
            }
        )
        if json_ways is None:
            return None
        ways = []
        for json_way in json_ways:
            way = Way.json_to_way(json_way)
            ways.append(way)
        return ways

    def get_node(self, node_id):
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].map_node
        node = db.find_one({'id': node_id})
        if node is None:
            return None
        return GNode.json_to_gnode(node)

    def get_nodes_by_coord(self, max_lat, min_lat, max_lon, min_lon):
        if self.conn is None:
            return False

        db = self.conn['smart_navigation'].map_node
        json_nodes = db.find(
            {
                '$and': [
                    {'lat': {'$lt': max_lat}},
                    {'lat': {'$gt': min_lat}},
                    {'lon': {'$lt': max_lon}},
                    {'lon': {'$gt': min_lon}}
                ]
            }
        )
        if json_nodes is None:
            return None
        nodes = []
        for json_node in json_nodes:
            node = GNode.json_to_gnode(json_node)
            nodes.append(node)
        return nodes

    def get_node_by_coord(self, lat, lon):
        lat = float(lat)
        lon = float(lon)
        if self.conn is None:
            return False
        db = self.conn['smart_navigation'].map_node
        node = db.find_one(
            {
                '$and': [
                    {'lat': lat},
                    {'lon': lon}
                ]
            }
        )
        if node is None:
            return None
        return GNode.json_to_gnode(node)

    def get_nearest_node(self, lat, lon):

        lat = float(lat)
        lon = float(lon)
        max_lat = lat + 0.001
        min_lat = lat - 0.001
        max_lon = lon + 0.001
        min_lon = lon - 0.001

        if self.conn is None:
            return False
        nodes = self.get_nodes_by_coord(max_lat, min_lat, max_lon, min_lon)
        if nodes is None:
            return None

        source = Point(lat, lon)
        distance = None
        nearest_node = None
        for node in nodes:
            d = calculate_distance(source, Point(node.get('lat'), node.get('lon')))
            if distance is None or d < distance:
                distance = d
                nearest_node = node

        return nearest_node


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

if __name__ == '__main__':
    mongo = MongoMapManager().get_instance()
    mongo.open_connection()
    way = mongo.get_way(115)
    node = mongo.get_node(248140361)
    print(way)
    print(node)
    node = mongo.get_node_by_coord('42.3300045', '12.2653073')
    print(node)
    ways = mongo.get_way_by_node(844191299)
    print(ways)
    node = mongo.get_nearest_node('42.3323892', '12.2695975')
    print(node)
    mongo.close_connection()





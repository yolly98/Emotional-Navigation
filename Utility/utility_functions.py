import math
import matplotlib.pyplot as plt
from Server.Persistence.mongo_map_manager import MongoMapManager
from Utility.gnode import GNode
from Utility.way import Way
from Utility.point import Point
import math


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


def print_path(path):
    time = 0
    length_path = 0

    for way in path:
        w = way['way']
        name = w.get('name')
        speed = w.get('speed')
        length = w.get('length')
        length_path += length
        time += (length * 3600) / (speed * 1000)
        print(f"way_name: {name} | length: {length / 1000} km | speed_limit: {speed} km/h")

    length = length_path / 1000
    estimated_time_m = math.floor(time / 60)
    estimated_time_s = math.floor(time % 60)
    print()
    print(f"length:  {length} km")
    print(f"estimated time: {estimated_time_m} minutes {estimated_time_s} seconds")
    return {"len": length, "t_m": estimated_time_m, "t_s": estimated_time_s}


def visualize_path(path, completed=False):

    lats = []
    lons = []
    colors = []
    point_sizes = []
    for way in path:
        node = way['start_node']
        lat = float(node.get('lat'))
        lon = float(node.get('lon'))
        lats.append(lat)
        lons.append(lon)
        colors.append('white')
        point_sizes.append(1)

    fig, ax = plt.subplots()

    if completed:
        # get points in the map
        map = MongoMapManager.get_instance()
        map.open_connection()
        nodes = map.get_nodes_by_coord(max(lats), min(lats), max(lons), min(lons))

        all_lats = lats.copy()
        all_lons = lons.copy()
        colors[0] = 'blue'
        colors[len(colors) - 1] = 'red'
        point_sizes[0] = 100
        point_sizes[len(point_sizes) - 1] = 100
        lines = dict()
        for node in nodes:

            ways = map.get_way_by_node(node.get('id'))
            for way in ways:
                way_id = way.get('id')
                if way_id not in lines:
                    lines[way_id] = dict()
                    lines[way_id]['lat'] = []
                    lines[way_id]['lon'] = []
                    lines[way_id]['lat'].append(float(node.get('lat')))
                    lines[way_id]['lon'].append(float(node.get('lon')))
                else:
                    lines[way_id]['lat'].append(float(node.get('lat')))
                    lines[way_id]['lon'].append(float(node.get('lon')))
                    if way.get('ref') == "":
                        ax.plot(lines[way_id]['lon'], lines[way_id]['lat'], c='white', alpha=1, linewidth=1)
                    else:
                        ax.plot(lines[way_id]['lon'], lines[way_id]['lat'], c='violet', alpha=1, linewidth=2)

            all_lats.append(node.get('lat'))
            all_lons.append(node.get('lon'))
            point_sizes.append(1)
            colors.append('white')

        map.close_connection()
        ax.scatter(all_lons, all_lats, c=colors, alpha=1, s=point_sizes)

    ax.plot(lons, lats, c='yellow', alpha=1, linewidth=2)
    fig.set_facecolor('black')
    ax.set_title("Path")
    ax.axis('off')
    plt.show()


def visualize_map():

    fig, ax = plt.subplots()

    # get points in the map
    map = MongoMapManager.get_instance()
    map.open_connection()
    nodes = map.get_all_nodes()

    all_lats = []
    all_lons = []
    point_sizes = []
    lines = dict()
    i = 0
    progress = 0
    for node in nodes:
        if not progress == math.floor((i * 100) / (len(nodes))):
            progress = math.floor((i*100)/(len(nodes)))
            print(f"calculation {progress}%")
        ways = map.get_way_by_node(node.get('id'))
        for way in ways:
            way_id = way.get('id')
            if way_id not in lines:
                lines[way_id] = dict()
                lines[way_id]['lat'] = []
                lines[way_id]['lon'] = []
                lines[way_id]['lat'].append(float(node.get('lat')))
                lines[way_id]['lon'].append(float(node.get('lon')))
            else:
                lines[way_id]['lat'].append(float(node.get('lat')))
                lines[way_id]['lon'].append(float(node.get('lon')))
                ax.plot(lines[way_id]['lon'], lines[way_id]['lat'], c='white', alpha=1, linewidth=1)

        all_lats.append(node.get('lat'))
        all_lons.append(node.get('lon'))
        point_sizes.append(1)
        i += 1

    map.close_connection()
    # ax.scatter(all_lons, all_lats, c='white', alpha=1, s=point_sizes)
    fig.set_facecolor('black')
    ax.set_title("Path")
    ax.axis('off')
    plt.show()


def path_to_json(path):
    json = []
    for relationship in path:
        item = {}
        item['start_node'] = relationship['start_node'].to_json()
        item['end_node'] = relationship['end_node'].to_json()
        item['way'] = relationship['way'].to_json()
        json.append(item)
    return json


def json_to_path(json):
    path = []
    for relationship in json:
        way = dict()
        way['way'] = Way.json_to_way(relationship['way'])
        way['start_node'] = GNode.json_to_gnode(relationship['start_node'])
        way['end_node'] = GNode.json_to_gnode(relationship['end_node'])
        path.append(way)
    return path


if __name__ == '__main__':
    visualize_map()
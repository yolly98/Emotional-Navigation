import math
from Utility.utility import Point, calculate_distance
from Persistence.map_sql_manager import MapSqlManager
from Persistence.graph_manager import GraphManager
import matplotlib.pyplot as plt
import matplotlib.image as mpimage


class MapEngine:

    @staticmethod
    def calculate_path(source, destination):

        graph_manager = GraphManager.get_instance()
        graph_manager.open_connection()
        ret = graph_manager.get_path(source, destination)
        graph_manager.close_connection()

        if ret is None:
            return {}

        nodes = ret['nodes']
        ways = ret['ways']

        sql_manager = MapSqlManager.get_instance()
        sql_manager.open_connection()
        path = dict()
        ordered_path = []
        order = 0
        for item in ways:

            way = sql_manager.get_way(int(item['way_id']))
            name = way.get('name')
            alt_name = way.get('alt_name')
            ref = way.get('ref')
            speed = way.get('speed')
            length = way.get('length')
            if name == "" and alt_name == "" and ref == "":
                name = "unknown"

            if name not in path:
                path[name] = dict()
                street = dict()
                street['name'] = name
                street['ref'] = ref
                street['speed'] = speed
                path[name]['order'] = order
                path[name]['ref'] = ref
                path[name]['speed'] = speed
                path[name]['length'] = length
                order += 1
                ordered_path.append(street)
            else:
                path[name]['length'] += length

        sql_manager.close_connection()

        for street_name in path:
            ordered_path[path[street_name]['order']]['length'] = path[street_name]['length']

        return {'nodes': nodes, 'path': ordered_path}

    @staticmethod
    def calculate_path_avoid_street(nodes, source, destination, way_name):

        graph_manager = GraphManager.get_instance()
        sql_manager = MapSqlManager.get_instance()

        sql_manager.open_connection()
        ways = sql_manager.get_instance().get_way_from_name(way_name)
        sql_manager.get_instance().close_connection()

        graph_manager.open_connection()
        # update length with big value to avoid the way in the path calculation
        for way in ways:
            graph_manager.update_way_length(way.get('id'), 1000)
        graph_manager.close_connection()

        res = MapEngine.calculate_path(source, destination)

        graph_manager.open_connection()
        # restore updated length
        for way in ways:
            graph_manager.update_way_length(way.get('id'), way.get('length'))
        graph_manager.close_connection()

        if nodes == res['nodes']:
            return None
        return res

    @staticmethod
    def print_path(path):
        time = 0
        length_path = 0
        for way in path:
            name = way['name']
            speed = way['speed']
            length = way['length']
            length_path += length
            time += (length * 3600) / (speed * 1000)
            print(f"way_name: {name} | length: {length / 1000} km | speed_limit: {speed} km/h")

        print()
        print(f"length:  {length_path / 1000} km")
        print(f"estimated time: {math.floor(time / 60)} minutes {math.floor(time % 60)} seconds")

    @staticmethod
    def visualize_path(nodes):

        lats = []
        lons = []
        colors = []
        point_sizes = []
        for node in nodes:
            lat = float(node['lat'])
            lon = float(node['lon'])
            lats.append(lat)
            lons.append(lon)
            colors.append('white')
            point_sizes.append(1)

        # get points in the map
        sql_manager = MapSqlManager.get_instance()
        sql_manager.open_connection()
        nodes = sql_manager.get_nodes_from_coord(max(lats), min(lats), max(lons), min(lons))

        all_lats = lats.copy()
        all_lons = lons.copy()
        colors[0] = 'blue'
        colors[len(colors) - 1] = 'red'
        point_sizes[0] = 100
        point_sizes[len(point_sizes) - 1] = 100
        fig, ax = plt.subplots()
        lines = dict()
        for node in nodes:

            starting_ways = sql_manager.get_way_from_start_node(node.get('id'))
            ending_ways = sql_manager.get_way_from_end_node(node.get('id'))
            ways = starting_ways + ending_ways
            for way in ways:
                way_id = way.get('id')
                if way_id not in lines:
                    lines[way_id] = dict()
                    lines[way_id]['lat'] = []
                    lines[way_id]['lon'] = []
                    lines[way_id]['lat'].append(node.get('lat'))
                    lines[way_id]['lon'].append(node.get('lon'))
                else:
                    lines[way_id]['lat'].append(node.get('lat'))
                    lines[way_id]['lon'].append(node.get('lon'))
                    if way.get('ref') == "":
                        ax.plot(lines[way_id]['lon'], lines[way_id]['lat'], c='white', alpha=1, linewidth=1)
                    else:
                        ax.plot(lines[way_id]['lon'], lines[way_id]['lat'], c='violet', alpha=1, linewidth=2)

            all_lats.append(node.get('lat'))
            all_lons.append(node.get('lon'))
            point_sizes.append(1)
            colors.append('white')

        sql_manager.close_connection()

        ax.plot(lons, lats, c='yellow', alpha=1, linewidth=2)
        ax.scatter(all_lons, all_lats, c=colors, alpha=1, s=point_sizes)
        fig.set_facecolor('black')
        ax.set_title("Path")
        ax.axis('off')
        # ax.set_xlim(min(lons) - 0.0001, max(lons) + 0.0001)
        # ax.set_ylim(min(lats) - 0.0001, max(lats) + 0.0001)
        plt.show()
        #plt.savefig('path.png')
        #plt_matrix = mpimage.imread('path.png')
        #print(plt_matrix)

# --------------------------------


if __name__ == "__main__":

    source = Point('42.3333569', '12.2692692')
    destination = Point('42.3295099', '12.2659779')

    res = MapEngine.calculate_path(source, destination)
    if res:
        MapEngine.print_path(res['path'])
    print(f"air distance: {calculate_distance(source, destination)} km")

    if res:
        MapEngine.visualize_path(res['nodes'])

    res = MapEngine.calculate_path_avoid_street(res['nodes'], source, destination, "Via Santa Maria")
    if res:
        MapEngine.print_path(res['path'])
    print(f"air distance: {calculate_distance(source, destination)} km")

    if res:
        MapEngine.visualize_path(res['nodes'])

import math
from Utility.utility_functions import calculate_distance
from Utility.point import Point
from Persistence.map_sql_manager import MapSqlManager
from Persistence.graph_manager import GraphManager
import matplotlib.pyplot as plt


class MapEngine:

    @staticmethod
    def calculate_path(source, destination):

        graph_manager = GraphManager.get_instance()
        graph_manager.open_connection()

        sql_manager = MapSqlManager.get_instance()
        sql_manager.open_connection()

        source = (sql_manager.get_node_by_coord(source.get_lat(), source.get_lon()))
        if source is False:
            print("Source position not found")
            return None
        source_id = source.get('id')
        destination = (sql_manager.get_node_by_coord(destination.get_lat(), destination.get_lon()))
        if destination is False:
            print("Destination position not found")
            return None
        destination_id = destination.get('id')
        ret = graph_manager.get_path(source_id, destination_id)
        graph_manager.close_connection()
        if ret is None:
            return {}

        neo4j_path = ret['ways']
        path = []
        for relationship in neo4j_path:
            r = relationship
            start_node = sql_manager.get_node(int(r.start_node.get('id')))
            end_node = sql_manager.get_node(int(r.end_node.get('id')))
            way_properties = sql_manager.get_way(r['way_id'])
            way = dict()
            way['way'] = way_properties
            way['start_node'] = start_node
            way['end_node'] = end_node
            if way_properties.get('name') == "" and way_properties.get('alt_name') == "" and way_properties.get('ref') == "":
                way_properties.set('name', "Unknown")
            path.append(way)

        return path

    @staticmethod
    def calculate_path_avoid_street(path, source, destination, way_name):

        graph_manager = GraphManager.get_instance()
        sql_manager = MapSqlManager.get_instance()

        sql_manager.open_connection()
        ways = sql_manager.get_instance().get_way_by_name(way_name)
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

        if path == res:
            return None
        return res

    @staticmethod
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

        print()
        print(f"length:  {length_path / 1000} km")
        print(f"estimated time: {math.floor(time / 60)} minutes {math.floor(time % 60)} seconds")

    @staticmethod
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
            sql_manager = MapSqlManager.get_instance()
            sql_manager.open_connection()
            nodes = sql_manager.get_nodes_by_coord(max(lats), min(lats), max(lons), min(lons))

            all_lats = lats.copy()
            all_lons = lons.copy()
            colors[0] = 'blue'
            colors[len(colors) - 1] = 'red'
            point_sizes[0] = 100
            point_sizes[len(point_sizes) - 1] = 100
            lines = dict()
            for node in nodes:

                ways = sql_manager.get_way_by_node(node.get('id'))
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

            sql_manager.close_connection()
            ax.scatter(all_lons, all_lats, c=colors, alpha=1, s=point_sizes)

        ax.plot(lons, lats, c='yellow', alpha=1, linewidth=2)
        fig.set_facecolor('black')
        ax.set_title("Path")
        ax.axis('off')
        plt.show()

# --------------------------------


if __name__ == "__main__":

    source = Point('42.3333569', '12.2692692')
    destination = Point('42.3295099', '12.2659779')

    path = MapEngine.calculate_path(source, destination)
    if path:
        MapEngine.print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")

    if path:
        MapEngine.visualize_path(path)

    path = MapEngine.calculate_path_avoid_street(path, source, destination, "Via Santa Maria")
    if path:
        MapEngine.print_path(path)
    print(f"air distance: {calculate_distance(source, destination)} km")

    if path:
       MapEngine.visualize_path(path)
